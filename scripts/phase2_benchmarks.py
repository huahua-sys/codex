#!/usr/bin/env python3
"""Append-only Phase 2 residual benchmarks; never optimize or rerun timing rules.

The old cash/sell outcomes are already known. This registration freezes the
new comparison and accounting, but is not an independent blind validation.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import math
import random
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lab.schema import HORIZONS, timestamp
from scripts.analyze_cash_and_sell import load_asset, simulate

OUT = ROOT / "research/phase2"
PREREG = OUT / "benchmarks.preregistration.v001.json"
LOCK = OUT / "benchmarks.preregistration.v001.lock.json"
OLD = ROOT / "research/night/cash_sell/CASH_SELL_RESULTS.v001.json"
SOURCE = {a: ROOT / f"data/raw/round_002/market/{a}.canonical.json" for a in ("SPY", "IEF", "BIL")}
WEIGHTS = {
    "ALWAYS_SPY": {"SPY": 1.0},
    "ALWAYS_BIL": {"BIL": 1.0},
    "ALWAYS_IEF": {"IEF": 1.0},
    "FIXED_50_50_SPY_BIL": {"SPY": 0.5, "BIL": 0.5},
    "FIXED_60_40_SPY_IEF": {"SPY": 0.6, "IEF": 0.4},
    "FIXED_70_30_SPY_IEF": {"SPY": 0.7, "IEF": 0.3},
}
DESIGN = {
    "study_id": "PHASE2-RESIDUAL-BENCHMARKS-v001",
    "status": "EXPLORATORY_COMPARISON_AFTER_OLD_RESULTS_KNOWN",
    "old_results_known_before_design": True,
    "no_new_independent_replay_or_prediction": True,
    "selection": {"years": list(range(2008, 2025)), "cutoff": "09-30T23:59:59+00:00", "all_existing_cash_sell_rows_retained": True},
    "horizons": HORIZONS,
    "primary_horizon": "12m",
    "secondary_horizons": ["1w", "1m", "3m", "6m", "24m"],
    "benchmarks_initial_weights": WEIGHTS,
    "rebalancing": "NONE; fixed initial buy-and-hold weights, drifting thereafter; not annual-rebalanced allocation or CAGR",
    "entry": "first common observed SPY/IEF/BIL US session OPEN strictly after T",
    "exit": "OPEN after N complete common observed sessions; same entry and exit for every benchmark",
    "costs_per_order_leg_bps": {"primary_50bp_roundtrip": 25.0, "fixed_10bp_sensitivity": 5.0},
    "cost_choice_optimized": False,
    "accounting": "UNADJUSTED units; split before distribution; dividends earned by prior holdings, ex-date CLOSE reinvestment; exit-open entitlement retained as cash; no entry-exdate entitlement",
    "dividend_payment_dates": "UNKNOWN: economic ex-date reinvestment, not verified executable payment-date cash",
    "daily_wealth": "initial NAV, every held-session CLOSE, terminal exit OPEN; mixed daily paths weighted before recomputing MDD",
    "MAE_MFE_basis": "DAILY_CLOSE_WEALTH_AND_TERMINAL_OPEN_NOT_INTRADAY_EXTREMA",
    "old_rules": "copy WEEKLY_SWITCH and FIXED_ENTRY_CHOICE results only; no new signal, rerun, parameter change or sample filtering",
    "parity_requirement": "all old SPY/BIL and 50/50 returns/MDD match under both costs and every horizon; fail whole run on timing discrepancy",
    "residuals": "paired net-return difference from each specified same-timing benchmark; not estimated causal alpha",
    "beta_control": "descriptive OLS weekly-minus-BIL on SPY-minus-BIL per horizon/cost; no trade weights or model prediction derived",
    "intervals": "1000 paired annual-cutoff resamples, fixed seed 20261009, percentile 2.5/97.5; descriptive only, overlapping 24m/year regimes invalidate independent-bet interpretation",
    "parameter_searches": 0,
    "threshold_optimization": False,
    "limitations": ["current corrected/backfilled vendor vintages, not archived quotes", "provider-reported dividends not independently reconciled", "BIL split-unit admin evidence only", "surviving ETF sample", "normal-session timing; halts and half-days not exhaustively audited", "USD only; no FX or taxes", "fund expenses embedded; trading costs assumed", "17 annual clusters, overlapping horizons and common macro shocks", "fixed allocation controls do not demonstrate optimal asset allocation", "no return edge, risk edge or principle promotion from sample averages alone"],
}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write_once(path, body):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(body, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    with path.open("xb") as output:
        output.write(payload)
    return digest(path)


def inputs():
    return {str(p.relative_to(ROOT)): digest(p) for p in [*SOURCE.values(), OLD, ROOT / "scripts/analyze_cash_and_sell.py", ROOT / "lab/schema.py", Path(__file__)]}


def preregister():
    if PREREG.exists() or LOCK.exists():
        verify()
        return {"status": "EXISTING_EXPLORATORY_REGISTRATION_INTEGRITY_PASS", "sha256": digest(PREREG)}
    body = {"registered_at": now(), "design": DESIGN, "source_and_code_sha256": inputs(), "honesty_note": "Old 102 cash/sell records and summary were inspected before this new comparator design; this lock cannot establish blindness."}
    h = write_once(PREREG, body)
    write_once(LOCK, {"locked_at": now(), "preregistration_sha256": h, "source_and_code_sha256": body["source_and_code_sha256"], "external_trusted_timestamp": False})
    return {"status": "EXPLORATORY_NEW_BENCHMARK_COMPARISON_LOCKED", "sha256": h}


def verify():
    body, lock = read(PREREG), read(LOCK)
    if body["design"] != DESIGN or lock["preregistration_sha256"] != digest(PREREG) or body["source_and_code_sha256"] != inputs() or lock["source_and_code_sha256"] != inputs():
        raise ValueError("frozen source/design/code changed: append a new version, never overwrite")


def path_metrics(path):
    peak, mdd = 1.0, 0.0
    for wealth in path:
        if not math.isfinite(wealth) or wealth <= 0:
            raise ValueError("invalid wealth")
        peak = max(peak, wealth)
        mdd = min(mdd, wealth / peak - 1.0)
    return {"net_return": path[-1] - 1.0, "net_max_drawdown": mdd, "close_wealth_MAE": min(path) - 1.0, "close_wealth_MFE": max(path) - 1.0}


def single_asset_path(rows, actions, leg_bps):
    if len(rows) < 2:
        raise ValueError("entry and exit sessions required")
    by_date = {}
    for action in actions:
        by_date.setdefault(action["date"], []).append(action)
    c = leg_bps / 10000.0
    shares = 1.0 / (rows[0]["open"] * (1.0 + c))
    path = [1.0]
    for i, row in enumerate(rows):
        receivable = 0.0
        if i:
            for a in by_date.get(row["date"], []):
                if a["action_type"] == "split":
                    shares *= float(a["ratio"])
            receivable = sum(shares * float(a["amount"]) for a in by_date.get(row["date"], []) if a["action_type"] == "dividend")
        if i == len(rows) - 1:
            path.append(shares * row["open"] * (1.0 - c) + receivable)
        else:
            path.append(shares * row["close"] + receivable)
            shares += receivable / row["close"]
    return {**path_metrics(path), "daily_close_wealth_path": path}


def mix_paths(components, weights):
    if not math.isclose(sum(weights.values()), 1.0) or any(w < 0 for w in weights.values()):
        raise ValueError("unlevered weights must sum to one")
    n = {len(components[a]["daily_close_wealth_path"]) for a in weights}
    if len(n) != 1:
        raise ValueError("mixed wealth must share every valuation timestamp")
    path = [sum(w * components[a]["daily_close_wealth_path"][i] for a, w in weights.items()) for i in range(n.pop())]
    equity_weight = [weights.get("SPY", 0.0) * components["SPY"]["daily_close_wealth_path"][i] / path[i] for i in range(1, len(path) - 1)]
    return {**path_metrics(path), "daily_close_wealth_path": path, "average_stock_weight_closes": statistics.mean(equity_weight)}


def evaluate_cutoff(assets, cutoff_at, horizon_sessions, leg_bps=25.0):
    """LABEL helper for separately registered experiments, never a T feature.

    Caller must freeze its design before invoking this function. Returns the
    fixed SPY/IEF/BIL common-timing economic labels; no choice of best outcome.
    """
    if set(assets) != {"SPY", "IEF", "BIL"} or not isinstance(horizon_sessions, int) or horizon_sessions < 1:
        raise ValueError("three named assets and a positive session horizon required")
    by_date = {a: {r["date"]: r for r in x["prices"]} for a, x in assets.items()}
    dates = sorted(set.intersection(*(set(d) for d in by_date.values())))
    opens = [timestamp(by_date["SPY"][d]["session_open_at"]) for d in dates]
    start = bisect.bisect_right(opens, timestamp(cutoff_at))
    if start + horizon_sessions >= len(dates):
        return {"status": "PENDING_HORIZON"}
    chosen = dates[start:start + horizon_sessions + 1]
    for d in chosen:
        if len({by_date[a][d]["session_open_at"] for a in assets}) != 1:
            raise ValueError("US common session clocks differ")
    missing = [action["date"] for bundle in assets.values() for action in bundle["actions"] if chosen[0] < action["date"] <= chosen[-1] and action["date"] not in set(chosen)]
    if missing:
        return {"status": "UNRESOLVED_ACTION_DATE_NOT_COMMON_SESSION", "missing_action_dates": sorted(set(missing))}
    components = {a: single_asset_path([by_date[a][d] for d in chosen], assets[a]["actions"], leg_bps) for a in assets}
    return {"status": "EXPLORATORY_VENDOR_ECONOMIC_RECONSTRUCTION", "cutoff_at": cutoff_at, "horizon_sessions": horizon_sessions, "entry_date": chosen[0], "exit_date": chosen[-1], "components": components, "portfolios": {p: mix_paths(components, weights) for p, weights in WEIGHTS.items()}}


def paired_interval(values):
    if not values:
        return None
    rng = random.Random(20261009)
    resampled = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(1000))
    return {"mean": statistics.mean(values), "median": statistics.median(values), "descriptive_paired_year_resample_2_5pct": resampled[24], "descriptive_paired_year_resample_97_5pct": resampled[974], "n_years": len(values), "not_confirmatory_or_independent_bet_CI": True}


def beta_control(rows):
    x = [r["ALWAYS_SPY"]["net_return"] - r["ALWAYS_BIL"]["net_return"] for r in rows]
    y = [r["WEEKLY_SWITCH"]["net_return"] - r["ALWAYS_BIL"]["net_return"] for r in rows]
    mx, my = statistics.mean(x), statistics.mean(y)
    variance = sum((v - mx)**2 for v in x)
    if variance <= 0:
        return {"status": "INSUFFICIENT_VARIATION"}
    slope = sum((a - mx) * (b - my) for a, b in zip(x, y)) / variance
    intercept = my - slope * mx
    error = sum((b - intercept - slope * a)**2 for a, b in zip(x, y))
    total = sum((b - my)**2 for b in y)
    return {"status": "DESCRIPTIVE_SAMPLE_OLS_NOT_CAUSAL_ALPHA", "n": len(x), "equity_excess_return_slope": slope, "sample_intercept_per_horizon": intercept, "r_squared": 1.0 - error / total if total > 0 else None, "used_to_select_weights_or_rule": False}


def close(a, b):
    if not math.isclose(a, b, abs_tol=1e-10, rel_tol=1e-10):
        raise AssertionError((a, b))


def self_test():
    def r(d, o, c):
        return {"date": d, "open": o, "close": c}
    rows = [r("2020-01-02", 100, 100), r("2020-01-03", 99, 99), r("2020-01-06", 100, 100)]
    close(single_asset_path(rows, [], 25)["net_return"], (1 - .0025) / (1 + .0025) - 1)
    dividend = [{"date": "2020-01-03", "action_type": "dividend", "amount": 1.0}]
    close(single_asset_path(rows, dividend, 0)["net_return"], 100 / 99 - 1)
    close(single_asset_path(rows, [{"date": rows[0]["date"], "action_type": "dividend", "amount": 20}], 0)["net_return"], 0)
    close(single_asset_path(rows, [{"date": rows[-1]["date"], "action_type": "dividend", "amount": 2}], 0)["net_return"], .02)
    splitrows = [r("2020-01-02", 100, 100), r("2020-01-03", 50, 50)]
    close(single_asset_path(splitrows, [{"date": "2020-01-03", "action_type": "split", "ratio": 2}], 0)["net_return"], 0)
    close(single_asset_path(splitrows, [{"date": "2020-01-03", "action_type": "split", "ratio": 2}, {"date": "2020-01-03", "action_type": "dividend", "amount": 1}], 0)["net_return"], .02)
    components = {"SPY": {"daily_close_wealth_path": [1, .8, 1.2]}, "BIL": {"daily_close_wealth_path": [1, 1.1, 1.15]}}
    mix = mix_paths(components, {"SPY": .5, "BIL": .5})
    close(mix["net_max_drawdown"], -.05)
    close(mix["net_return"], .175)
    pair = [{"SPY": x, "BIL": x} for x in rows]
    maps = {"SPY": {"2020-01-03": dividend}, "BIL": {}}
    for bps in (0, 5, 25):
        modern = single_asset_path(rows, dividend, bps)
        old = simulate(pair, maps, "SPY", {}, bps)
        for a, b in zip(modern["daily_close_wealth_path"], old["daily_close_wealth_path"]):
            close(a, b)
    return {"status": "SYNTHETIC_ENGINEERING_ONLY_PASS", "checks": 11, "real_market_files_opened": False}


def execute():
    verify()
    old = read(OLD)
    assets = {a: load_asset(path, a) for a, path in SOURCE.items()}
    by_date = {a: {r["date"]: r for r in x["prices"]} for a, x in assets.items()}
    dates = sorted(set.intersection(*(set(d) for d in by_date.values())))
    opens = [timestamp(by_date["SPY"][d]["session_open_at"]) for d in dates]
    for d in dates:
        if len({by_date[a][d]["session_open_at"] for a in assets}) != 1:
            raise ValueError("US common session clocks differ")
    episodes, csv_rows, parity_checks = [], [], 0
    old_index = {(int(e["cutoff_at"][:4]), e["horizon"]): e for e in old["episodes"]}
    for year in DESIGN["selection"]["years"]:
        cutoff = f"{year}-09-30T23:59:59+00:00"
        start = bisect.bisect_right(opens, timestamp(cutoff))
        for horizon, n in HORIZONS.items():
            prior = old_index[(year, horizon)]
            entry = {"episode_id": f"PHASE2-BENCHMARK-{year}-{horizon}", "year": year, "cutoff_at": cutoff, "horizon": horizon, "original_cash_sell_episode_id": prior["episode_id"], "results": {}}
            if start + n >= len(dates):
                entry["status"] = "PENDING_HORIZON"
                episodes.append(entry)
                continue
            chosen = dates[start:start + n + 1]
            missing_actions = [a["date"] for bundle in assets.values() for a in bundle["actions"] if chosen[0] < a["date"] <= chosen[-1] and a["date"] not in set(chosen)]
            if missing_actions:
                entry.update(status="UNRESOLVED_ACTION_DATE_NOT_COMMON_SESSION", missing_action_dates=sorted(set(missing_actions)))
                episodes.append(entry)
                continue
            if prior["entry_date"] != chosen[0] or prior["exit_date"] != chosen[-1]:
                raise ValueError("IEF common-session filtering altered old benchmark timing; cannot silently compare")
            entry.update(status="EXPLORATORY_VENDOR_ECONOMIC_RECONSTRUCTION", entry_date=chosen[0], exit_date=chosen[-1])
            gross = {a: single_asset_path([by_date[a][d] for d in chosen], assets[a]["actions"], 0) for a in assets}
            for cost, bps in DESIGN["costs_per_order_leg_bps"].items():
                net = {a: single_asset_path([by_date[a][d] for d in chosen], assets[a]["actions"], bps) for a in assets}
                results = {p: {**mix_paths(net, weights), "gross_return": mix_paths(gross, weights)["net_return"], "initial_weights": weights} for p, weights in WEIGHTS.items()}
                for new_name, old_name in (("ALWAYS_SPY", "ALWAYS_SPY"), ("ALWAYS_BIL", "ALWAYS_BIL"), ("FIXED_50_50_SPY_BIL", "FIXED_50_50_BUY_HOLD")):
                    for metric in ("net_return", "net_max_drawdown"):
                        close(results[new_name][metric], prior["results"][cost]["portfolios"][old_name][metric])
                        parity_checks += 1
                for old_rule in ("WEEKLY_SWITCH", "FIXED_ENTRY_CHOICE"):
                    copied = prior["results"][cost]["portfolios"][old_rule]
                    holding = copied["holding_sessions"]
                    results[old_rule] = {"net_return": copied["net_return"], "gross_return": copied["gross_return"], "net_max_drawdown": copied["net_max_drawdown"], "average_stock_weight_closes": holding["SPY"] / sum(holding.values()), "close_wealth_MAE": None, "close_wealth_MFE": None, "source": "COPIED_OLD_FROZEN_RULE_OUTPUT_NO_RERUN", "stock_exposure_basis": "fraction of observed held sessions; binary position, not new fitted weight"}
                for name, result in results.items():
                    result["residual_net_returns"] = {p: result["net_return"] - results[p]["net_return"] for p in WEIGHTS}
                    result["paired_MDD_differences"] = {p: result["net_max_drawdown"] - results[p]["net_max_drawdown"] for p in WEIGHTS}
                    row = {"year": year, "cutoff_at": cutoff, "horizon": horizon, "common_sessions": n, "entry_date": chosen[0], "exit_date": chosen[-1], "cost": cost, "portfolio_id": name, "asset_id": name.replace("ALWAYS_", "") if name.startswith("ALWAYS_") else "PORTFOLIO", "gross_return": result["gross_return"], "net_return": result["net_return"], "net_max_drawdown": result["net_max_drawdown"], "close_wealth_MAE": result["close_wealth_MAE"], "close_wealth_MFE": result["close_wealth_MFE"], "average_stock_exposure": result["average_stock_weight_closes"]}
                    row.update({f"residual_vs_{p}": result["residual_net_returns"][p] for p in WEIGHTS})
                    csv_rows.append(row)
                entry["results"][cost] = results
            episodes.append(entry)
    summary = {}
    for h in HORIZONS:
        eligible = [e for e in episodes if e["horizon"] == h and e["results"]]
        summary[h] = {"n_year_clusters": len(eligible), "costs": {}}
        for cost in DESIGN["costs_per_order_leg_bps"]:
            rows = [e["results"][cost] for e in eligible]
            if not rows:
                continue
            comparison = {}
            for p in (*WEIGHTS, "WEEKLY_SWITCH", "FIXED_ENTRY_CHOICE"):
                comparison[p] = {"mean_net_return": statistics.mean(r[p]["net_return"] for r in rows), "median_net_return": statistics.median(r[p]["net_return"] for r in rows), "mean_net_max_drawdown": statistics.mean(r[p]["net_max_drawdown"] for r in rows), "worst_net_max_drawdown": min(r[p]["net_max_drawdown"] for r in rows), "mean_stock_exposure": statistics.mean(r[p]["average_stock_weight_closes"] for r in rows)}
            summary[h]["costs"][cost] = {"portfolios": comparison, "weekly_paired_return_residuals": {p: paired_interval([r["WEEKLY_SWITCH"]["net_return"] - r[p]["net_return"] for r in rows]) for p in WEIGHTS}, "weekly_paired_MDD_differences": {p: paired_interval([r["WEEKLY_SWITCH"]["net_max_drawdown"] - r[p]["net_max_drawdown"] for r in rows]) for p in WEIGHTS}, "weekly_beta_control": beta_control(rows)}
    output = {"built_at": now(), "status": "EXPLORATORY_PAIRED_BENCHMARKS_NO_GENERIC_TIMING_EDGE_CLAIM", "preregistration_sha256": digest(PREREG), "design": DESIGN, "source_and_code_sha256": inputs(), "episode_count": len(episodes), "year_cluster_count": 17, "parity_checks": parity_checks, "all_old_rule_outputs_copied_unchanged": True, "episodes": episodes, "summary": summary, "new_historical_replays": 0, "new_predictions": 0}
    write_once(OUT / "benchmarks.results.v001.json", output)
    csv_path = OUT / "benchmarks.residuals.v001.csv"
    with csv_path.open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)
    render_report(output)
    return {"status": output["status"], "records": len(episodes), "csv_rows": len(csv_rows), "parity_checks": parity_checks, "primary_summary": summary["12m"]}


def render_report(output):
    lines = ["# Phase 2：固定配置与残差基准", "", "本次比较在旧 102 条 SPY/BIL 卖出结果已知之后设计，属于 EXPLORATORY。没有新增预测，没有重跑或优化失败规则，没有更改旧锁定判断。固定 2008–2024 年 9 月 30 日全部 17 个起点；六期限不是 102 个独立样本。", "", "ETF 为今天供应商历史版本的经济重建。SPY、IEF、BIL 使用相同 US 观测 session 的下一开盘进场、经过 N 个完整 session 后开盘退出。分红按 ex-date close 再投资，支付日未知；这不是经过验证的历史可执行现金回报。基金费已包含；无税和 FX。", "", "50/50 是 SPY/BIL；60/40 和 70/30 是 SPY/IEF。IEF 为 7–10 年美国国债 ETF，含久期风险，绝不能称短债。权重只在进场时固定，之后不再平衡。回撤由逐日组合财富重算；收益为各独立持有期简单收益，不是滚动长期 CAGR。", "", "|期限/成本|组合|年簇|平均净收益|中位净收益|平均 MDD|最差 MDD|平均股票暴露|", "|---|---|---|---|---|---|---|---|"]
    for h in ("12m", "24m"):
        for cost, s in output["summary"][h]["costs"].items():
            for p, v in s["portfolios"].items():
                lines.append(f"|{h}/{cost}|{p}|{output['summary'][h]['n_year_clusters']}|{v['mean_net_return']:.2%}|{v['median_net_return']:.2%}|{v['mean_net_max_drawdown']:.2%}|{v['worst_net_max_drawdown']:.2%}|{v['mean_stock_exposure']:.1%}|")
    lines += ["", "## 每周切换规则的增量信息", "", "以下为固定主成本（每 leg 25bp，简单进出共50bp）。差值按同年配对；正的 MDD 差值代表每周规则回撤较浅。", "", "|期限|基准|平均收益残差|配对年重采样2.5–97.5%|平均 MDD 差值|", "|---|---|---|---|---|"]
    for h in ("12m", "24m"):
        s = output["summary"][h]["costs"]["primary_50bp_roundtrip"]
        for p, v in s["weekly_paired_return_residuals"].items():
            dd = s["weekly_paired_MDD_differences"][p]["mean"]
            lines.append(f"|{h}|{p}|{v['mean']:.2%}|{v['descriptive_paired_year_resample_2_5pct']:.2%}至{v['descriptive_paired_year_resample_97_5pct']:.2%}|{dd:.2%}|")
        b = s["weekly_beta_control"]
        lines += ["", f"{h} 描述性 OLS：每周规则相对 BIL 收益对 SPY 相对 BIL 收益的 slope={b['equity_excess_return_slope']:.3f}，样本截距={b['sample_intercept_per_horizon']:.2%}，R²={b['r_squared']:.3f}。这些是样本拟合描述，不能称 alpha，也不生成新组合权重。", ""]
    lines += ["## 解释边界", "", "RETURN EDGE：旧每周规则是否增加收益，必须看对固定配置的配对残差；相对全股票回撤较小本身不是择时信息。DOWNSIDE PROTECTION：可以单独保留防大亏研究问题，但若固定减少股票已提供相近或更低回撤，就不能将改善全归功于信号。RETURN/RISK EDGE：仍未用连续独立投资路径、风险预算匹配和现实资金约束证实；不能用这些重叠持有期的均值冒充 Sharpe 或 CAGR。", "", "1000 次固定 seed 年簇重采样只描述本样本差值不确定性，不是确认性统计结论；24m 标签相互重叠，年份共享危机／政策环境。没有筛选最优权重、期限、费用或起点。所有六期限及两成本保存在 JSON/CSV。", "", f"工程核验：{output['parity_checks']} 次旧 SPY、BIL、50/50 收益及 MDD 对齐全部通过；合成会计测试只验证程序。原模型概率、原结论和原判断没有改变。", "", "接口：[benchmarks.residuals.v001.csv](research/phase2/benchmarks.residuals.v001.csv) 包含 year/cutoff/horizon/cost/portfolio_id/asset_id、净收益、MDD、close-wealth MAE/MFE 和相对每一固定基准残差。MAE/MFE 来自收盘财富与退出开盘；不是日内极值。旧每周规则只复制已保存收益/MDD，未保存的 MAE/MFE 留空，禁止以0填补。", ""]
    with (OUT / "benchmarks.results.v001.md").open("x") as f:
        f.write("\n".join(lines))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--preregister", action="store_true")
    group.add_argument("--execute", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    result = self_test() if args.self_test else preregister() if args.preregister else execute()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
