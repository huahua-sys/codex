"""Stage A. Ratio-only rule; does not import the evaluator or read future labels."""
import hashlib
import math
import statistics
from datetime import timedelta
from pathlib import Path
from .schema import CONTEXT_CATEGORIES, HORIZONS, historical_wealth, json_bytes, read_json, sha256, timestamp, utc_now, validate_input, write_once

RULE = {
    "id": "R002-TREND-PRIOR-v001", "confidence": "D", "fitted": False,
    "features": ["known_action_total_return_63_sessions", "known_action_total_return_252_sessions", "past_252_session_annualized_volatility"],
    "positive": {"p_up": .60, "p_up_range": [.45, .75], "scenarios": [.20, .40, .40], "exposure": 1},
    "negative": {"p_up": .40, "p_up_range": [.25, .55], "scenarios": [.40, .40, .20], "exposure": 0},
    "mixed": {"p_up": .50, "p_up_range": [.35, .65], "scenarios": [.30, .40, .30], "exposure": 0},
    "scenario_probability_half_width": .15,
    "scenario_band_vol_multiplier": .5,
    "model_payoff_vol_multiplier": 1.0,
    "horizon_sessions": HORIZONS,
    "primary_horizon": "12m",
    "cost_bps_roundtrip_default": 50.0,
    "cash_return_default": 0.0,
    "cash_status": "ASSUMPTION_NOT_OBSERVED_CASH_RETURN",
    "minimum_past_returns": 252,
    "date_asset_specific_logic": False,
    "parameter_searches": 0,
    "probability_baselines": [0.5, 0.6],
    "baseline_interpretation": "constant fair-coin and unfitted equity-upward-prior; no selection by outcome",
}


def implementation_hashes():
    root = Path(__file__).resolve().parents[1]
    return {name: sha256(root / name) for name in ("lab/schema.py", "lab/replay.py", "lab/evaluate.py", "lab/select.py", "scripts/run_replay.py")}


def make_prediction(packet):
    validate_input(packet)
    input_actions = packet.get("actions", [])
    if packet.get("metadata", {}).get("return_basis", "PRICE_ONLY") == "PRICE_ONLY":
        input_actions = [a for a in input_actions if a["action_type"] == "split"]
    chain = historical_wealth(packet["prices"], input_actions)
    result = {
        "record_type": "prediction_ex_ante", "status": "EX_ANTE_DRAFTED", "round_id": "ROUND_002",
        "episode_id": packet["episode_id"], "asset_id": packet["asset_id"], "market": packet["market"],
        "cutoff_at": packet["cutoff_at"], "cutoff_timezone": "UTC", "created_at": utc_now(),
        "research_stage": "EXPLORATORY", "replay_type": "EXPLORATORY_RULE_BASED_MASKED_REPLAY",
        "rule_id": RULE["id"], "confidence": "D", "fitted": False,
        "frozen_rule": RULE,
        "rule_sha256": hashlib.sha256(json_bytes(RULE)).hexdigest(),
        "model_memory_contamination": "NO_PER_EPISODE_LLM_JUDGMENT_RULE_DESIGNED_IN_2026_WITH_PRIOR_KNOWLEDGE_POSSIBLE",
        "separation": "SEPARATION_LOGICAL_ONLY", "information_set": "KNOWN_AT_T_ONLY",
        "context_state": {}, "features": {}, "horizons": {},
        "cost_bps_roundtrip": float(packet.get("cost_bps_roundtrip", RULE["cost_bps_roundtrip_default"])),
        "cash_alternative_return": 0.0, "cash_alternative_status": RULE["cash_status"],
        "execution_rule": "first available session OPEN strictly after cutoff; exit OPEN after N complete sessions; N=5/21/63/126/252/504; no interim rebalance",
        "return_basis": packet.get("metadata", {}).get("return_basis", "PRICE_ONLY"),
        "tradability": packet.get("metadata", {}).get("tradability", "UNVERIFIED"),
        "currency": packet["currency"], "reporting_currency": packet["currency"], "fx_return": None,
        "input_quality": packet.get("metadata", {}),
        "price_in_assessment": "UNKNOWN: only lagged market behavior observed; no historical valuation/expectation source, cannot identify expectations already reflected",
        "biggest_unknown": "缺少盈利、估值、信用初值和可验证政策执行；趋势延续与反转均可能发生。",
        "next_review_at": (timestamp(packet["cutoff_at"]) + timedelta(days=7)).isoformat(),
        "kill_thesis": ["每周复核；若最近63或252个完整已公开时段总回报不再同时为正，则原趋势买入理由失效。", "若数据来源、公司行动、时间证据或可交易性被否定，则暂停，不以未来结果重写原判断。"],
        "kill_thesis_execution": "DIAGNOSTIC_ONLY_THIS_ROUND_FIXED_HOLDING_NO_DYNAMIC_EXIT_LABEL",
        "missing_features_not_imputed": True,
    }
    context = packet.get("context", [])
    for cat in CONTEXT_CATEGORIES:
        rows = sorted([r for r in context if r.get("category") == cat], key=lambda r: (timestamp(r["available_at"]), r.get("record_id", "")))
        result["context_state"][cat] = {"value": rows[-1].get("value") if rows else None, "status": "KNOWN_AT_T" if rows else "DATA_REQUIRED", "evidence_record_ids": [r["record_id"] for r in rows]}
    if len(chain) < 253:
        result.update(status="INSUFFICIENT_HISTORY", decision="WAIT", exposure=None, direction=None,
                      positive_evidence=[], negative_evidence=[], limitations=["fewer than 252 prior session returns"])
        return result
    wealth = [v for _, v in chain]
    r63, r252 = wealth[-1] / wealth[-64] - 1, wealth[-1] / wealth[-253] - 1
    daily = [wealth[i] / wealth[i-1] - 1 for i in range(len(wealth)-252, len(wealth))]
    sigma = statistics.stdev(daily) * math.sqrt(252)
    key = "positive" if r63 > 0 and r252 > 0 else "negative" if r63 < 0 and r252 < 0 else "mixed"
    params = RULE[key]
    ids = [chain[i][0]["record_id"] for i in (-1, -64, -253)]
    result["features"] = {"r63": r63, "r252": r252, "annual_volatility_252": sigma,
                          "price_rows": len(chain), "evidence_record_ids": ids,
                          "actions_used": [r["record_id"] for r in input_actions],
                          "formula": "known-action wealth ratios; sample stdev(last252 daily simple returns)*sqrt(252)"}
    result.update(regime=key.upper() + "_TREND", exposure=params["exposure"],
                  decision="HYPOTHETICAL_LONG" if params["exposure"] else "WAIT",
                  direction="Bull" if params["p_up"] > .5 else "Bear" if params["p_up"] < .5 else "Base")
    positive, negative = [], []
    for name, value, record in (("63-session", r63, ids[1]), ("252-session", r252, ids[2])):
        basis = "价格回报" if result["return_basis"] == "PRICE_ONLY" else "已知行动经济总回报"
        row = {"type": "OBSERVED_SIGNAL", "statement": f"{name}历史{basis}={value:.6f}", "evidence_record_ids": [record, ids[0]]}
        (positive if value > 0 else negative).append(row)
    # Missing evidence is a limitation, never a fabricated negative observation.
    while len(positive) < 3:
        positive.append({"type": "NO_ADDITIONAL_POSITIVE_EVIDENCE", "statement": "可靠正面证据不足；不得用故事补足。", "evidence_record_ids": []})
    while len(negative) < 3:
        negative.append({"type": "LIMITATION_NOT_OBSERVED_NEGATIVE_SIGNAL", "statement": "估值/盈利/信用缺失；不能排除价格已反映预期或状态改变。", "evidence_record_ids": []})
    result["positive_evidence"], result["negative_evidence"] = positive, negative
    result["context_state"]["Trend"] = {"value": result["regime"], "status": "KNOWN_AT_T", "evidence_record_ids": ids}
    for horizon, n in HORIZONS.items():
        scaled_vol = sigma * math.sqrt(n / 252)
        band = .5 * scaled_vol
        scenarios = []
        for scenario, p, payoff in zip(("Bear", "Base", "Bull"), params["scenarios"], (-scaled_vol, 0.0, scaled_vol)):
            scenarios.append({"scenario": scenario, "probability_range": [max(0., p-.15), min(1., p+.15)], "scoring_probability": p, "assumed_net_payoff": payoff})
        result["horizons"][horizon] = {"session_count": n, "direction": result["direction"],
            "p_up_range": params["p_up_range"], "p_up_scoring_probability": params["p_up"],
            "up_event": "net outcome > 0 using frozen model costs; index label is hypothetical price return, not investable total return",
            "scenario_threshold_lower": -band, "scenario_threshold_upper": band,
            "scenario_definition": "Bear net<-band; Base -band<=net<=band; Bull net>band; net includes frozen cost assumption",
            "scenarios": scenarios, "model_expected_value": sum(s["scoring_probability"] * s["assumed_net_payoff"] for s in scenarios),
            "expected_value_status": "UNFITTED_SCENARIO_ASSUMPTION_NOT_ESTIMATED_EXPECTED_RETURN",
            "payoff_assumption": "Bear=-past annualvol*sqrt(N/252);Base=0;Bull=+same; not tail bounds",
            "risk": "volatility-scale assumption; actual losses can exceed scenario payoff; valuation/credit/earnings unobserved"}
    return result


def prediction_markdown(p):
    out = [f"# {p['episode_id']} — Stage A", "", f"Cutoff: `{p['cutoff_at']}`；信息集 `KNOWN_AT_T`；`EXPLORATORY_RULE_BASED_MASKED_REPLAY`。", "", f"资产：{p['asset_id']} / {p['market']}；动作：{p['decision']}；置信度 D。", "", "只运行冻结的匿名比值规则，没有按日期/资产调用历史记忆作判断。规则设计本身仍可能受先验知识影响，不能称真实事前盲测。", "", "## 当时信息", ""]
    for cat, state in p["context_state"].items():
        out.append(f"- {cat}: {state['value']}；{state['status']}；记录 {','.join(state['evidence_record_ids']) or '无'}")
    out += ["", "## 正面证据（不足处明确为空）", ""]
    out += [f"- {r['type']}: {r['statement']}；{','.join(r['evidence_record_ids']) or '无'}" for r in p.get("positive_evidence", [])]
    out += ["", "## 反面证据 / 限制（限制不是反向观察）", ""]
    out += [f"- {r['type']}: {r['statement']}；{','.join(r['evidence_record_ids']) or '无'}" for r in p.get("negative_evidence", [])]
    out += ["", "## 概率与风险", "", "|期限|方向|上涨概率区间 / 固定代表值|Bear/Base/Bull固定代表值|模型EV|", "|---|---|---|---|---|"]
    for h, x in p["horizons"].items():
        out.append(f"|{h}|{x['direction']}|{x['p_up_range']} / {x['p_up_scoring_probability']}|{'/'.join(str(s['scoring_probability']) for s in x['scenarios'])}|{x['model_expected_value']:.6f}|")
        out.append(f"\n{h} 情景概率区间：" + "; ".join(f"{s['scenario']} {s['probability_range']}" for s in x["scenarios"]) + f"；中性带 ±{x['scenario_threshold_upper']:.6f}。\n")
    out += ["", "模型EV是未校准情景假设；不是已估计预期收益。三类情景概率不直接等于上涨概率。", "", f"Price-in: {p['price_in_assessment']}", "", f"最大未知：{p['biggest_unknown']}", "", "Kill Thesis：", ""] + ["- " + x for x in p["kill_thesis"]]
    out += ["", "本轮终值用固定持有，Kill Thesis只作每周诊断，未模拟动态止损。原生指数仅价格标签，不等于可交易净总回报；现金0%是模型假设。", ""]
    return "\n".join(out)


def run_stage_a(exante_dir, output_dir, selection_path, preregistration_path):
    exante_dir, output_dir = Path(exante_dir), Path(output_dir)
    selection = read_json(selection_path)
    inputs = read_json(exante_dir / "manifest.json")
    expected = {e["episode_id"] for e in selection["episodes"]}
    if set(inputs["inputs"]) != expected:
        raise ValueError("input/selection episode mismatch")
    hashes = {"selection_sha256": sha256(selection_path), "preregistration_sha256": sha256(preregistration_path), "input_manifest_sha256": sha256(exante_dir / "manifest.json"), "implementation_sha256": implementation_hashes()}
    for eid in sorted(expected):
        info = inputs["inputs"][eid]
        path = (exante_dir / info["path"]).resolve()
        if exante_dir.resolve() not in path.parents:
            raise ValueError("input path escapes exante directory")
        if sha256(path) != info["sha256"]:
            raise ValueError("input hash mismatch " + eid)
        packet = read_json(path)
        selected = next(x for x in selection["episodes"] if x["episode_id"] == eid)
        for field in ("episode_id", "cutoff_at", "asset_id", "market"):
            if packet[field] != selected[field]:
                raise ValueError("input/selection mismatch " + field)
        pred_path = output_dir / "predictions" / (eid + ".v001.json")
        md_path = output_dir / "predictions" / (eid + ".v001.md")
        lock_path = output_dir / "locks" / (eid + ".v001.lock.json")
        if lock_path.exists():
            lock = read_json(lock_path)
            if any(lock[k] != v for k, v in hashes.items()) or lock["input_sha256"] != sha256(path) or lock["prediction_sha256"] != sha256(pred_path) or lock["prediction_markdown_sha256"] != sha256(md_path):
                raise ValueError("existing lock integrity mismatch " + eid)
            continue
        if pred_path.exists() or md_path.exists():
            raise ValueError("partial prior Stage A artifact: do not overwrite; inspect and append a version")
        p = make_prediction(packet)
        p.update(hashes, input_sha256=sha256(path), status="EX_ANTE_LOCKED" if p["horizons"] else "INSUFFICIENT_HISTORY")
        prediction_hash = write_once(pred_path, p)
        markdown_hash = write_once(md_path, prediction_markdown(p), text=True)
        write_once(lock_path, {"episode_id": eid, "status": "EX_ANTE_LOCKED", "locked_at": utc_now(), "operator": "deterministic-python-stage-a", "rule_id": RULE["id"], "prediction_sha256": prediction_hash, "prediction_markdown_sha256": markdown_hash, "input_sha256": sha256(path), "input_path": info["path"], "hash_is_not_trusted_timestamp": True, "separation": "SEPARATION_LOGICAL_ONLY", **hashes})
    # Completion sentinel exists only after every lock is verified.
    done_path = output_dir / "all_locks.v001.json"
    done = {"status": "ALL_EX_ANTE_LOCKED", "episode_ids": sorted(expected), "lock_sha256": {eid: sha256(output_dir / "locks" / (eid + ".v001.lock.json")) for eid in sorted(expected)}, "insufficient_history_episode_ids": [eid for eid in sorted(expected) if read_json(output_dir / "predictions" / (eid + ".v001.json"))["status"] == "INSUFFICIENT_HISTORY"], **hashes}
    if done_path.exists():
        if read_json(done_path) != done:
            raise ValueError("all-lock sentinel mismatch")
    else:
        write_once(done_path, done)
    return done
