#!/usr/bin/env python3
"""Append-only SPY/BIL cash and weekly sell mechanics; no parameter search.

--preregister and --self-test never open market-data files. Execute only after
the root's BREADY message, with --b-ready pointing to a completed Stage B summary.
This is a separate retrospective walk-forward reconstruction, not rescoring any
old locked prediction. Current vendor vintages and ex-date reinvestment qualify
all economic returns; no claim of historically executable payment-date cash.
"""
from __future__ import annotations
import argparse
import bisect
import hashlib
import json
import math
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lab.schema import historical_wealth, timestamp, validate_actions, validate_records

PREREG = ROOT / "research/night/CASH_SELL_PREREGISTRATION.json"
LOCK = PREREG.with_suffix(".lock.json")
HORIZONS = {"1w": 5, "1m": 21, "3m": 63, "6m": 126, "12m": 252, "24m": 504}
DESIGN = {
    "cycle_id": "NIGHT-CASH-SELL-v001",
    "research_mode": "EXPLORATORY_RETROSPECTIVE_WALK_FORWARD_MECHANICS",
    "confidence": "D",
    "replay_claim": "NOT_TRUE_BLIND_NOT_OLD_PREDICTION_RESCORING",
    "selection": {"years": list(range(2008, 2025)), "month_day": "09-30", "cutoff_time": "23:59:59+00:00", "outcome_inspection_for_selection": False},
    "assets": ["SPY", "BIL"], "currency": "USD", "horizon_sessions": HORIZONS,
    "primary_horizons": ["12m", "24m"],
    "signal": {"lookbacks": [63, 252], "rule": "SPY past known-action economic wealth ratios BOTH > 0 => SPY; otherwise BIL", "thresholds": [0.0, 0.0], "minimum_prices": 253, "future_metadata_or_action_announcements": "NEVER_SIGNAL_INPUT", "insufficient_history": "KEEP_UNRESOLVED_NO_CASH_FALLBACK"},
    "review": {"weekday": "Friday", "at": "23:59:59+00:00", "price_gate": "available_at <= review_at AND session_close_at <= review_at", "action_gate": "available_at <= review_at AND date <= last_known_price_date", "conservative_vendor_lag": "preserved; Friday close normally becomes available Saturday 00:00 America/New_York, so Friday UTC review can use Thursday close"},
    "execution": {"entry": "first common observed SPY/BIL session OPEN strictly after annual cutoff", "switch": "first common observed session OPEN strictly after Friday review", "exit": "OPEN after N complete common observed sessions, same for every benchmark", "timing": "NO_SAME_CLOSE_FILL_NO_INTRAWEEK_PRICE_TRIGGER", "holdings": "100pct SPY or 100pct BIL, unlevered; no discretionary override"},
    "benchmarks": ["ALWAYS_SPY", "ALWAYS_BIL", "FIXED_ENTRY_CHOICE", "FIXED_50_50_BUY_HOLD"],
    "fixed_mix": {"initial_weights": {"SPY": 0.5, "BIL": 0.5}, "rebalance": "NONE", "wealth": "0.5*same-timing SPY wealth + 0.5*same-timing BIL wealth; each component pays identical entry/exit leg cost", "drawdown": "calculated from summed daily wealth path, never average the two drawdowns", "purpose": "negative control for merely reducing equity exposure, no optimized weight"},
    "costs": {"primary_per_order_leg_bps": 25.0, "primary_buy_sell_roundtrip_bps": 50.0, "fixed_sensitivity_per_order_leg_bps": 5.0, "fixed_sensitivity_roundtrip_bps": 10.0, "selection_by_cost_result": False, "gross": "zero trading costs only; embedded fund expense remains", "formula": "buy shares=free_cash/(open*(1+leg_cost)); sale cash=shares*open*(1-leg_cost); every switch pays both legs", "dividend_reinvestment_fee": 0.0},
    "accounting": {"prices": "audited canonical UNADJUSTED economic units; no Adj Close", "splits": "ordinary verified split changes held share count before ex-date distribution/trade; future split proof is admin only", "dividends": "entitlement to shares held before ex-date; retained after selling at ex-date open; reinvested at that session close in current portfolio asset; exit-open receivable added to terminal value", "switch_day_dividend": "kept as receivable until close, not available to buy the new asset at open", "entry_exdate": "new purchase does not receive that day's distribution", "fund_fees": "already embedded in ETF market performance; do not subtract a second annual expense ratio", "payment_dates": "unknown; ex-date reinvestment is an economic convention, not proved executable cash availability", "tax_fx": "no taxes or FX; USD instruments only"},
    "metrics": ["gross_return", "net_return", "excess_vs_ALWAYS_SPY", "excess_vs_ALWAYS_BIL", "excess_vs_FIXED_ENTRY_CHOICE", "excess_vs_FIXED_50_50_BUY_HOLD", "close_path_max_drawdown", "switch_count", "order_count", "turnover_sum_notional_over_preorder_NAV", "BIL_segment_missed_rallies", "BIL_segment_avoided_losses", "SPY_and_BIL_holding_sessions"],
    "cash_interval_diagnostics": {"missed_rally": "during each BIL interval, gross SPY matched-open economic return > gross BIL matched-open economic return", "avoided_loss": "during each BIL interval, gross SPY return <0 AND BIL return > SPY return", "aggregation": "counts and descriptive mean relative-return gaps; intervals/horizons overlap, not independent events"},
    "missingness": "keep each annual-cutoff/horizon record; PENDING_HORIZON or UNRESOLVED_DATA, never replace with 0",
    "limitations": ["BIL is a traded short Treasury ETF, not risk-free cash; bid-ask, premium/discount and fund risks remain", "Current provider historical vintages can be corrected; archived quote vintages unavailable", "Daily OHLC/normal-session clocks cannot verify halts, half days, intraday ordering or execution slippage", "Provider dividend amounts not all independently reconciled; economic ex-date reinvestment only", "Fixed 50bp primary and 10bp sensitivity are assumptions, not estimated historical costs", "Annual and 24m horizon observations overlap; report date clusters rather than independent-bet claims", "Rule designed in 2026 with historical prior knowledge; no causal evidence, strategy optimization or robust-pattern claim", "Do not modify or reinterpret original 24 Stage A predictions or original zero-cash scoring"],
    "parameter_searches": 0, "inference": "DESCRIPTIVE_ONLY_NO_HYPOTHESIS_PROMOTION",
}

def canonical(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def write_once(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output: output.write(canonical(obj))
    return sha(path)

def read(path):
    return json.loads(Path(path).read_text())

def code_hashes():
    return {"scripts/analyze_cash_and_sell.py": sha(__file__), "lab/schema.py": sha(ROOT / "lab/schema.py")}

def preregister():
    if PREREG.exists() or LOCK.exists():
        verify_preregistration()
        return {"status": "EXISTING_PREREGISTRATION_INTEGRITY_PASS", "preregistration_sha256": sha(PREREG)}
    body = {"registered_at": now(), "real_future_prices_read_by_this_cycle_before_registration": False, "implementation_sha256": code_hashes(), "design": DESIGN}
    digest = write_once(PREREG, body)
    write_once(LOCK, {"cycle_id": DESIGN["cycle_id"], "locked_at": now(), "preregistration_sha256": digest, "implementation_sha256": code_hashes(), "external_trusted_timestamp": False, "hash_does_not_prove_no_prior_knowledge": True})
    return {"status": "PREREGISTERED_BEFORE_REAL_OUTCOME_READ", "preregistration_sha256": digest}

def verify_preregistration():
    if not PREREG.exists() or not LOCK.exists(): raise ValueError("preregister first, before opening any real data")
    body, lock = read(PREREG), read(LOCK)
    if lock["preregistration_sha256"] != sha(PREREG) or body["implementation_sha256"] != code_hashes() or lock["implementation_sha256"] != code_hashes() or body["design"] != DESIGN:
        raise ValueError("immutable preregistration/code integrity failed; new cycle/version required")
    return lock

def load_asset(path, asset_id):
    bundle = read(path); meta = bundle.get("metadata", {})
    if bundle.get("asset_id") != asset_id or meta.get("currency") != "USD" or meta.get("instrument_type") != "ETF": raise ValueError("only named USD ETFs allowed")
    if meta.get("price_basis") != "UNADJUSTED" or meta.get("adjclose_used") or not meta.get("total_return_eligible") or meta.get("split_action_validation_required"):
        raise ValueError("audited economic units/action eligibility required")
    if bundle.get("action_coverage") != "COMPLETE": raise ValueError("provider action coverage must be COMPLETE and qualified")
    validate_records(bundle["prices"], require_prices=True)
    validate_actions(bundle.get("actions", []))
    for row in bundle["prices"] + bundle.get("actions", []):
        if row.get("asset_id") != asset_id or row["source_sha256"] != meta.get("source_sha256"): raise ValueError("asset/source provenance mismatch")
    prices = sorted(bundle["prices"], key=lambda r: timestamp(r["session_open_at"]))
    if len({r["date"] for r in prices}) != len(prices): raise ValueError("duplicate observed session date")
    return {**bundle, "prices": prices, "metadata": meta}

def known_signal(spy, at):
    # This is the only signal interface. Metadata, BIL outcomes, future actions,
    # open/high/low values and later prices cannot influence its decision.
    at = timestamp(at)
    rows = [r for r in spy["prices"] if timestamp(r["available_at"]) <= at and timestamp(r["session_close_at"]) <= at]
    rows = rows[-253:]
    if len(rows) < 253: return {"status": "INSUFFICIENT_HISTORY", "decision": None, "review_at": at.isoformat(), "known_price_rows": len(rows)}
    actions = [a for a in spy.get("actions", []) if timestamp(a["available_at"]) <= at and rows[0]["date"] < a["date"] <= rows[-1]["date"]]
    validate_records(rows, at.isoformat(), require_prices=True); validate_actions(actions, at.isoformat())
    missing_action_dates = sorted({a["date"] for a in actions} - {r["date"] for r in rows})
    if missing_action_dates:
        return {"status": "UNRESOLVED_KNOWN_ACTION_DATE_NO_PRICE", "decision": None, "review_at": at.isoformat(), "missing_action_dates": missing_action_dates}
    chain = historical_wealth(rows, actions); w = [x[1] for x in chain]
    r63, r252 = w[-1] / w[-64] - 1, w[-1] / w[-253] - 1
    return {"status": "KNOWN_AT_REVIEW_RECONSTRUCTED_VENDOR_VINTAGE", "review_at": at.isoformat(), "decision": "SPY" if r63 > 0 and r252 > 0 else "BIL", "r63": r63, "r252": r252, "last_known_price_date": rows[-1]["date"], "latest_price_available_at": rows[-1]["available_at"], "price_evidence_record_ids": [rows[i]["record_id"] for i in (-253, -64, -1)], "action_evidence_record_ids": [a["record_id"] for a in actions], "future_metadata_used": False}

def common_sessions(assets):
    by_date = {a: {r["date"]: r for r in assets[a]["prices"]} for a in ("SPY", "BIL")}
    dates = sorted(set(by_date["SPY"]) & set(by_date["BIL"]))
    rows = []
    for d in dates:
        pair = {a: by_date[a][d] for a in ("SPY", "BIL")}
        if timestamp(pair["SPY"]["session_open_at"]) != timestamp(pair["BIL"]["session_open_at"]): raise ValueError("benchmark session open mismatch")
        rows.append(pair)
    return rows

def action_maps(assets):
    maps = {}
    for asset, bundle in assets.items():
        maps[asset] = {}
        for a in bundle.get("actions", []): maps[asset].setdefault(a["date"], []).append(a)
    return maps

def simulate(rows, actions, initial, switches, leg_bps):
    """Entry/exit open; distributions owned before ex-date, revalue at close."""
    if len(rows) < 2: raise ValueError("need entry plus at least one later exit open")
    cost = leg_bps / 10000.0
    cash, receivable, shares, held = 1.0, 0.0, 0.0, None
    path, orders, turnover, switch_count = [1.0], [], 0.0, 0
    holding_sessions = {"SPY": 0, "BIL": 0}
    executed_switches = []
    last_index = len(rows) - 1
    for i, pair in enumerate(rows):
        day = pair["SPY"]["date"]
        if held is not None and i:
            for a in actions[held].get(day, []):
                if a["action_type"] == "split": shares *= float(a["ratio"])
            receivable = sum(shares * float(a["amount"]) for a in actions[held].get(day, []) if a["action_type"] == "dividend")
        target = initial if i == 0 else switches.get(i, held)
        if i == last_index: target = None
        if target != held:
            prior = held
            if held is not None:
                px = pair[held]["open"]; notional = shares * px; nav = cash + receivable + notional
                turnover += notional / nav; cash += notional * (1 - cost)
                orders.append({"date": day, "asset": held, "side": "SELL", "notional": notional, "leg_cost_bps": leg_bps})
                held, shares = None, 0.0
            if target is not None:
                px = pair[target]["open"]; nav = cash + receivable
                shares = cash / (px * (1 + cost)); notional = shares * px
                turnover += notional / nav if nav else 0.0; cash -= notional * (1 + cost)
                if abs(cash) < 1e-12: cash = 0.0
                orders.append({"date": day, "asset": target, "side": "BUY", "notional": notional, "leg_cost_bps": leg_bps})
                held = target
            if prior is not None and target is not None:
                switch_count += 1; executed_switches.append({"index": i, "date": day, "from": prior, "to": target})
        if i == last_index:
            terminal = cash + receivable; path.append(terminal); break
        holding_sessions[held] += 1
        close = pair[held]["close"]
        path.append(cash + shares * close + receivable)
        if receivable:
            shares += receivable / close; receivable = 0.0
    peak, mdd = 1.0, 0.0
    for w in path: peak = max(peak, w); mdd = min(mdd, w / peak - 1)
    return {"return": terminal - 1, "max_drawdown": mdd, "max_drawdown_basis": "daily portfolio closes plus initial NAV and terminal exit OPEN; no intraday order inference", "switch_count": switch_count, "order_count": len(orders), "turnover": turnover, "turnover_definition": "sum order notional / NAV immediately before each order", "holding_sessions": holding_sessions, "orders": orders, "executed_switches": executed_switches, "daily_close_wealth_path": path}

def fixed_mix(spy, bil):
    if len(spy["daily_close_wealth_path"]) != len(bil["daily_close_wealth_path"]): raise ValueError("fixed mix needs identical wealth valuation dates")
    path = [0.5*a+0.5*b for a,b in zip(spy["daily_close_wealth_path"],bil["daily_close_wealth_path"])]
    peak, mdd = 1.0, 0.0
    for w in path: peak=max(peak,w); mdd=min(mdd,w/peak-1)
    orders = [{**o,"notional":o["notional"]*0.5} for p in (spy,bil) for o in p["orders"]]
    buys = [o for o in orders if o["side"]=="BUY"]; sells=[o for o in orders if o["side"]=="SELL"]
    nav, turnover = 1.0, 0.0
    for o in buys:
        turnover += o["notional"]/nav; nav -= o["notional"]*o["leg_cost_bps"]/10000
    nav = path[-1]+sum(o["notional"]*o["leg_cost_bps"]/10000 for o in sells)
    for o in sells:
        turnover += o["notional"]/nav; nav -= o["notional"]*o["leg_cost_bps"]/10000
    return {"return":path[-1]-1,"max_drawdown":mdd,"max_drawdown_basis":"exact sum of matched daily component wealth paths, initial fixed 50/50 buy-hold allocation", "switch_count":0,"order_count":len(orders),"turnover":turnover,"turnover_definition":"sum order notional/global pre-order NAV; same-time orders ordered SPY then BIL", "holding_sessions":{"SPY":spy["holding_sessions"]["SPY"]*0.5,"BIL":bil["holding_sessions"]["BIL"]*0.5}, "orders":buys+sells,"executed_switches":[],"daily_close_wealth_path":path}

def bil_intervals(rows, initial, switches):
    n = len(rows) - 1; held, start, intervals = initial, 0, []
    for i in sorted(switches):
        target = switches[i]
        if i >= n or target == held: continue
        if held == "BIL": intervals.append((start, i))
        held, start = target, i
    if held == "BIL" and start < n: intervals.append((start, n))
    return intervals

def interval_diagnostics(rows, actions, initial, switches):
    output = []
    for start, end in bil_intervals(rows, initial, switches):
        segment = rows[start:end+1]
        spy = simulate(segment, actions, "SPY", {}, 0)["return"]
        bil = simulate(segment, actions, "BIL", {}, 0)["return"]
        output.append({"start_date": segment[0]["SPY"]["date"], "end_date": segment[-1]["SPY"]["date"], "common_sessions": end-start, "spy_gross_return": spy, "bil_gross_return": bil, "bil_minus_spy_return_gap": bil-spy, "missed_rally": spy > bil, "avoided_loss": spy < 0 and bil > spy})
    return output

def weekly_schedule(spy, rows, cutoff, get_signal):
    cutoff = timestamp(cutoff); exit_at = timestamp(rows[-1]["SPY"]["session_open_at"])
    opening_times = [timestamp(x["SPY"]["session_open_at"]) for x in rows]
    day = cutoff.date() + timedelta(days=(4-cutoff.weekday()) % 7)
    review = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=timezone.utc)
    if review <= cutoff: review += timedelta(days=7)
    switches, reviews = {}, []
    while review < exit_at:
        signal = get_signal(review.isoformat())
        if signal["decision"] is None: return None, reviews + [signal]
        index = bisect.bisect_right(opening_times, review)
        if 0 <= index < len(rows)-1:
            switches[index] = signal["decision"]
            reviews.append({**signal, "execution_date": rows[index]["SPY"]["date"], "execution_at": opening_times[index].isoformat()})
        review += timedelta(days=7)
    return switches, reviews

def analyze(assets, output_dir):
    sessions = common_sessions(assets); opens = [timestamp(p["SPY"]["session_open_at"]) for p in sessions]
    actions = action_maps(assets); signal_cache, episodes = {}, []
    def get_signal(at):
        if at not in signal_cache: signal_cache[at] = known_signal(assets["SPY"], at)
        return signal_cache[at]
    for year in DESIGN["selection"]["years"]:
        cutoff = f"{year}-09-30T23:59:59+00:00"; initial_signal = get_signal(cutoff)
        start = bisect.bisect_right(opens, timestamp(cutoff))
        for horizon, n in HORIZONS.items():
            episode = {"episode_id": f"NIGHT-CASH-SELL-{year}-{horizon}", "cutoff_at": cutoff, "horizon": horizon, "sessions": n, "initial_signal": initial_signal, "results": {}}
            if initial_signal["decision"] is None: episode["status"] = "UNRESOLVED_DATA_INSUFFICIENT_KNOWN_HISTORY"; episodes.append(episode); continue
            if start + n >= len(sessions): episode["status"] = "PENDING_HORIZON"; episodes.append(episode); continue
            rows = sessions[start:start+n+1]; session_dates = {p["SPY"]["date"] for p in rows}
            missing_action_dates = [a["date"] for b in assets.values() for a in b.get("actions", []) if rows[0]["SPY"]["date"] < a["date"] <= rows[-1]["SPY"]["date"] and a["date"] not in session_dates]
            if missing_action_dates:
                episode.update(status="UNRESOLVED_DATA_ACTION_DATE_NOT_IN_COMMON_SESSIONS", missing_action_dates=sorted(set(missing_action_dates))); episodes.append(episode); continue
            switches, reviews = weekly_schedule(assets["SPY"], rows, cutoff, get_signal)
            if switches is None: episode.update(status="UNRESOLVED_DATA_WEEKLY_SIGNAL_HISTORY", reviews=reviews); episodes.append(episode); continue
            episode.update(status="RETROSPECTIVE_ECONOMIC_RECONSTRUCTION", entry_date=rows[0]["SPY"]["date"], exit_date=rows[-1]["SPY"]["date"], weekly_review_count=len(reviews), weekly_review_timestamps=[r["review_at"] for r in reviews], entry_open_after_cutoff=True)
            portfolios = {"WEEKLY_SWITCH": (initial_signal["decision"], switches), "ALWAYS_SPY": ("SPY", {}), "ALWAYS_BIL": ("BIL", {}), "FIXED_ENTRY_CHOICE": (initial_signal["decision"], {})}
            gross = {p: simulate(rows, actions, initial, transitions, 0.0) for p, (initial, transitions) in portfolios.items()}
            gross["FIXED_50_50_BUY_HOLD"] = fixed_mix(gross["ALWAYS_SPY"],gross["ALWAYS_BIL"])
            for label, bps in (("primary_50bp_roundtrip", 25.0), ("fixed_10bp_sensitivity", 5.0)):
                net = {p: simulate(rows, actions, initial, transitions, bps) for p, (initial, transitions) in portfolios.items()}
                net["FIXED_50_50_BUY_HOLD"] = fixed_mix(net["ALWAYS_SPY"],net["ALWAYS_BIL"])
                results = {}
                for p in net:
                    netrow = net[p]
                    results[p] = {"gross_return": gross[p]["return"], "net_return": netrow["return"], "gross_max_drawdown": gross[p]["max_drawdown"], "net_max_drawdown": netrow["max_drawdown"], "order_count": netrow["order_count"], "switch_count": netrow["switch_count"], "turnover": netrow["turnover"], "holding_sessions": netrow["holding_sessions"], "excess_vs_ALWAYS_SPY": netrow["return"]-net["ALWAYS_SPY"]["return"], "excess_vs_ALWAYS_BIL": netrow["return"]-net["ALWAYS_BIL"]["return"], "excess_vs_FIXED_ENTRY_CHOICE": netrow["return"]-net["FIXED_ENTRY_CHOICE"]["return"], "excess_vs_FIXED_50_50_BUY_HOLD":netrow["return"]-net["FIXED_50_50_BUY_HOLD"]["return"]}
                    if horizon in DESIGN["primary_horizons"] and p == "WEEKLY_SWITCH": results[p]["orders"] = netrow["orders"]
                episode["results"][label] = {"cost_per_leg_bps": bps, "portfolios": results}
            episode["BIL_intervals"] = interval_diagnostics(rows, actions, initial_signal["decision"], switches)
            episode["missed_rally_count"] = sum(x["missed_rally"] for x in episode["BIL_intervals"])
            episode["avoided_loss_count"] = sum(x["avoided_loss"] for x in episode["BIL_intervals"])
            episodes.append(episode)
    output = {"cycle_id": DESIGN["cycle_id"], "status": "DESCRIPTIVE_RETROSPECTIVE_RECONSTRUCTION_NO_ROBUST_PATTERN_CLAIM", "built_at": now(), "preregistration_sha256": sha(PREREG), "source_qualification": {a: {k: assets[a]["metadata"].get(k) for k in ("source_id", "source_sha256", "source_url", "original_vintage_status", "total_return_validation", "dividend_amounts_independently_reconciled", "ordinary_split_evidence")} for a in assets}, "design": DESIGN, "episode_count": len(episodes), "annual_cutoff_cluster_count": 17, "episodes": episodes, "signal_audit": [signal_cache[k] for k in sorted(signal_cache)], "summary": {}}
    for horizon in HORIZONS:
        rows = [e for e in episodes if e["horizon"] == horizon and e["results"]]
        result = {"n_mature": len(rows), "n_pending_or_unresolved": 17-len(rows), "costs": {}}
        for label in ("primary_50bp_roundtrip", "fixed_10bp_sensitivity"):
            if not rows: continue
            result["costs"][label] = {p: {"mean_gross_return": statistics.mean(e["results"][label]["portfolios"][p]["gross_return"] for e in rows), "mean_net_return": statistics.mean(e["results"][label]["portfolios"][p]["net_return"] for e in rows), "median_net_return": statistics.median(e["results"][label]["portfolios"][p]["net_return"] for e in rows), "mean_excess_vs_SPY": statistics.mean(e["results"][label]["portfolios"][p]["excess_vs_ALWAYS_SPY"] for e in rows), "mean_excess_vs_BIL": statistics.mean(e["results"][label]["portfolios"][p]["excess_vs_ALWAYS_BIL"] for e in rows), "mean_excess_vs_FIXED_50_50_BUY_HOLD":statistics.mean(e["results"][label]["portfolios"][p]["excess_vs_FIXED_50_50_BUY_HOLD"] for e in rows), "mean_net_max_drawdown": statistics.mean(e["results"][label]["portfolios"][p]["net_max_drawdown"] for e in rows), "worst_net_max_drawdown": min(e["results"][label]["portfolios"][p]["net_max_drawdown"] for e in rows), "mean_turnover": statistics.mean(e["results"][label]["portfolios"][p]["turnover"] for e in rows), "mean_switch_count": statistics.mean(e["results"][label]["portfolios"][p]["switch_count"] for e in rows)} for p in ("WEEKLY_SWITCH", "ALWAYS_SPY", "ALWAYS_BIL", "FIXED_ENTRY_CHOICE", "FIXED_50_50_BUY_HOLD")}
        output["summary"][horizon] = result
    write_once(Path(output_dir) / "CASH_SELL_RESULTS.v001.json", output)
    markdown = ["# Cash 与每周卖出机制：独立历史重建", "", "固定 2008–2024 年度 9 月 30 日；没有筛选时点、阈值或成本。原 24 个锁定预测与计分完全独立。规则于 2026 年设计，结果属于回顾性 walk-forward mechanics，不是真正盲测或策略优化。", "", "BIL 为有风险的短国债 ETF；这里只计算带公司行动的经济回报，分红使用 ex-date close 再投资，未证明支付日现金与成交可实现。基金费用已嵌入价格；交易费用为固定假设；无税、无 FX。", "", "主成本每 leg 25bp（简单进出 50bp），固定敏感性每 leg 5bp（进出 10bp）；每次 SPY↔BIL 切换都付两个 legs。Gross 仍包含基金本身费用。", "", "固定 50% SPY／50% BIL 对照仅在入场分配、随后不再平衡；两者相同时点的逐日财富加权，回撤从组合财富重新算，不能将两回撤平均。它用于检查减股票暴露本身是否足以解释回撤改善。", "", "|期限／成本|成熟样本|每周切换平均 net|始终 SPY|始终 BIL|固定入场选择|固定50/50|切换相对 SPY|切换相对50/50|切换平均 MDD|平均切换次数|", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for h in HORIZONS:
        s = output["summary"][h]
        for label, portfolios in s["costs"].items():
            weekly = portfolios["WEEKLY_SWITCH"]
            markdown.append(f"|{h} / {label}|{s['n_mature']}|{weekly['mean_net_return']:.2%}|{portfolios['ALWAYS_SPY']['mean_net_return']:.2%}|{portfolios['ALWAYS_BIL']['mean_net_return']:.2%}|{portfolios['FIXED_ENTRY_CHOICE']['mean_net_return']:.2%}|{portfolios['FIXED_50_50_BUY_HOLD']['mean_net_return']:.2%}|{weekly['mean_excess_vs_SPY']:.2%}|{weekly['mean_excess_vs_FIXED_50_50_BUY_HOLD']:.2%}|{weekly['mean_net_max_drawdown']:.2%}|{weekly['mean_switch_count']:.2f}|")
    markdown += ["", "结果是重叠小样本描述。12m/24m 需逐年查看反例、错过上涨区间、避免亏损区间及换手成本；不能据均值升级投资原则。未检验最佳参数、长期年化收益、因果机制或概率校准。", "", "Friday UTC 截止严格保留源 available_at：典型周五日线直到周六纽约零点才准入，因此复核可能只用周四收盘。下一共同可观测 US session 开盘才交易；没有完整交易所停牌／半日会话审计。", ""]
    path = Path(output_dir) / "CASH_SELL_RESULTS.v001.md"; path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f: f.write("\n".join(markdown))
    return output

def synthetic_tests():
    # Engineering-only fixtures; no real market rows, economic conclusions or
    # fake support episodes. Test cash entitlement and open/close order exactly.
    def row(day, price):
        return {"date": day, "open": price, "close": price}
    rows = [{"SPY": row("2020-01-02",100.), "BIL": row("2020-01-02",50.)}, {"SPY": row("2020-01-03",99.), "BIL": row("2020-01-03",50.)}, {"SPY": row("2020-01-06",100.), "BIL": row("2020-01-06",50.)}]
    empty = {"SPY": {}, "BIL": {}}
    def close(actual, expected):
        if not math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10): raise AssertionError((actual, expected))
    close(simulate(rows, empty, "SPY", {}, 0)["return"],0.)
    close(simulate(rows, empty, "BIL", {},25)["return"],(1-.0025)/(1+.0025)-1)
    dist = {"SPY": {"2020-01-03": [{"action_type":"dividend", "amount":1.}]}, "BIL": {}}
    close(simulate(rows, dist, "SPY", {1:"BIL"},0)["return"],0.)
    exitdist = {"SPY": {"2020-01-06": [{"action_type":"dividend", "amount":2.}]}, "BIL": {}}
    close(simulate(rows, exitdist, "SPY", {},0)["return"],.02)
    entrydist = {"SPY": {"2020-01-02": [{"action_type":"dividend", "amount":20.}]}, "BIL": {}}
    close(simulate(rows, entrydist, "SPY", {},0)["return"],0.)
    splitrows = [{"SPY":row("2020-01-02",100.),"BIL":row("2020-01-02",50.)}, {"SPY":row("2020-01-03",50.),"BIL":row("2020-01-03",50.)}]
    split = {"SPY":{"2020-01-03":[{"action_type":"split","ratio":2.}]}, "BIL":{}}
    close(simulate(splitrows, split, "SPY", {},0)["return"],0.)
    twice = simulate(rows, empty, "BIL", {1:"SPY"},25)
    assert twice["switch_count"] == 1 and twice["order_count"] == 4
    # Synthetic dates are abstract sessions, not asserted real US trading days.
    start = datetime(2018,1,1,tzinfo=timezone.utc); quotes=[]
    for i in range(253):
        d=start+timedelta(days=i); px=100.+i
        quotes.append({"record_id":f"SYNTHETIC:{i}", "asset_id":"SPY", "date":d.date().isoformat(), "session_open_at":d.replace(hour=13).isoformat(), "session_close_at":d.replace(hour=20).isoformat(), "available_at":(d+timedelta(days=1)).replace(hour=4).isoformat(), "open":px,"high":px,"low":px,"close":px,"source_id":"SYNTHETIC_ENGINEERING_ONLY","source_sha256":"synthetic-not-market","pit_status":"KNOWN_MARKET_OBSERVATION_RECONSTRUCTED"})
    cutoff=timestamp(quotes[-1]["available_at"]); bundle={"prices":quotes,"actions":[]}
    before=known_signal(bundle,cutoff.isoformat()); assert before["decision"]=="SPY"
    later=quotes[-1].copy(); later.update(record_id="SYNTHETIC:FUTURE",date=(cutoff+timedelta(days=1)).date().isoformat(),available_at=(cutoff+timedelta(days=2)).isoformat(),session_open_at=(cutoff+timedelta(days=1,hours=9)).isoformat(),session_close_at=(cutoff+timedelta(days=1,hours=16)).isoformat(),open=.01,high=.01,low=.01,close=.01)
    future_action={"record_id":"SYNTHETIC:FUTURE_ACTION","asset_id":"SPY","date":quotes[-1]["date"],"available_at":(cutoff+timedelta(days=1)).isoformat(),"action_type":"dividend","amount":10000.,"source_id":"SYNTHETIC_ENGINEERING_ONLY","source_sha256":"synthetic-not-market","pit_status":"KNOWN_CORPORATE_ACTION_RECONSTRUCTED"}
    after=known_signal({"prices":quotes+[later],"actions":[future_action],"metadata":{"future_story":"must be ignored"}},cutoff.isoformat())
    assert before==after
    prior=known_signal(bundle,(cutoff-timedelta(seconds=1)).isoformat()); assert prior["decision"] is None
    mixrows=[{"SPY":{"date":"2020-01-02","open":100.,"close":80.},"BIL":{"date":"2020-01-02","open":100.,"close":110.}}, {"SPY":{"date":"2020-01-03","open":80.,"close":120.},"BIL":{"date":"2020-01-03","open":110.,"close":115.}}, {"SPY":{"date":"2020-01-06","open":120.,"close":120.},"BIL":{"date":"2020-01-06","open":115.,"close":115.}}]
    mixture=fixed_mix(simulate(mixrows,empty,"SPY",{},0),simulate(mixrows,empty,"BIL",{},0))
    close(mixture["return"],.175); close(mixture["max_drawdown"],-.05)
    return {"status":"SYNTHETIC_ENGINEERING_ONLY_PASS", "checks":12, "real_market_files_opened":False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preregister", action="store_true"); mode.add_argument("--self-test", action="store_true"); mode.add_argument("--execute", action="store_true")
    parser.add_argument("--spy", default=str(ROOT / "data/raw/round_002/market/SPY.canonical.json"))
    parser.add_argument("--bil", default=str(ROOT / "data/raw/round_002/market/BIL.canonical.json"))
    parser.add_argument("--b-ready"); parser.add_argument("--output-dir", default=str(ROOT / "research/night/cash_sell"))
    args = parser.parse_args()
    if args.self_test: print(json.dumps(synthetic_tests())); return
    if args.preregister: print(json.dumps(preregister())); return
    lock = verify_preregistration()
    if not args.b_ready: raise ValueError("root BREADY and an existing completed Stage B summary are required before data read")
    ready = read(args.b_ready)
    if ready.get("status") != "DESCRIPTIVE_SMALL_DEPENDENT_SAMPLE_NOT_CONFIRMATORY" or ready.get("episode_count",0) < 24:
        raise ValueError("BREADY witness is not a completed core Stage B summary")
    read_audit = {"cycle_id": DESIGN["cycle_id"], "first_real_data_read_authorized_at": now(), "preregistration_sha256": sha(PREREG), "lock_sha256": sha(LOCK), "stage_b_ready_path": str(Path(args.b_ready)), "stage_b_ready_sha256": sha(args.b_ready), "source_bundle_sha256": {"SPY":sha(args.spy), "BIL":sha(args.bil)}, "reconstruction_not_old_rescoring":True}
    write_once(Path(args.output_dir) / "CASH_SELL_READ_AUDIT.v001.json", read_audit)
    assets = {"SPY":load_asset(args.spy,"SPY"), "BIL":load_asset(args.bil,"BIL")}
    output = analyze(assets,args.output_dir)
    print(json.dumps({"status":output["status"], "episode_count":output["episode_count"], "summary":{h:output["summary"][h] for h in DESIGN["primary_horizons"]}},ensure_ascii=False,indent=2))

if __name__ == "__main__": main()
