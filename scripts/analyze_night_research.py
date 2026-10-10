#!/usr/bin/env python3
"""Read completed, locked replay batches; fixed 12m descriptive analysis only.

No raw prices, future bundles, fitting, parameter search, or engine modifications.
Matching uses ALL eligible locked predictions, before joining outcome availability.
"""
import argparse
import csv
import hashlib
import json
import math
import random
import os
import statistics
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HORIZON = "12m"
BOOTSTRAP_DRAWS = 1000
BOOTSTRAP_SEED = 20261008
RULE_ID = "R002-TREND-PRIOR-v001"
RULE_SHA256 = "3f45039c4376334501be3e177bab113cc65d7f4b3296f9c6b2e82e66a57b5729"
INDUSTRIES = {
    "XLK": "科技", "SOXX": "半导体", "SMH": "半导体", "XLF": "金融",
    "XLE": "资源/能源", "XLB": "资源/材料", "XLV": "医药/医疗",
    "XLP": "消费/必需", "XLY": "消费/可选", "XLI": "工业/制造", "XLU": "公用事业",
    "SPY": "综合权益", "^HSI": "综合权益", "^N225": "综合权益", "EWH": "综合权益", "EWJ": "综合权益",
}
DELTA_METRICS = (
    "brier_delta_vs_constant_06", "hypothetical_decision_delta_vs_all_long",
    "hypothetical_decision_delta_vs_assumed_cash0",
    "model_ev_exposure_delta_vs_all_long", "model_ev_exposure_delta_vs_assumed_cash0",
)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def mean(values):
    values = [v for v in values if finite(v)]
    return sum(values)/len(values) if values else None


def quantile(values, probability):
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered)-1)*probability
    low, high = math.floor(position), math.ceil(position)
    return ordered[low] + (ordered[high]-ordered[low])*(position-low)


def load_completed_batches(batch_dirs):
    """Only outputs after all-lock + completed Stage B summary exist are read."""
    rows, sources, ids = [], {}, set()
    for directory in sorted({str(Path(p).resolve()) for p in batch_dirs}):
        root = Path(directory)
        sentinel_path = root/"all_locks.v001.json"
        summary_path = root/"evaluation_summary.v001.json"
        if not sentinel_path.is_file() or not summary_path.is_file():
            raise ValueError("batch not fully locked/revealed; analyzer will not read it: " + str(root))
        sentinel = read_json(sentinel_path)
        if sentinel.get("status") != "ALL_EX_ANTE_LOCKED":
            raise ValueError("invalid all-lock sentinel " + str(root))
        sources[str(sentinel_path)] = sha256(sentinel_path)
        sources[str(summary_path)] = sha256(summary_path)
        for eid in sentinel["episode_ids"]:
            if eid in ids:
                raise ValueError("globally duplicate episode_id; new cohorts require unique IDs: " + eid)
            ids.add(eid)
            lock_path = root/"locks"/(eid+".v001.lock.json")
            pred_path = root/"predictions"/(eid+".v001.json")
            md_path = root/"predictions"/(eid+".v001.md")
            label_path = root/"labels"/(eid+".v001.json")
            lock = read_json(lock_path)
            if sha256(lock_path) != sentinel["lock_sha256"][eid] or sha256(pred_path) != lock["prediction_sha256"] or sha256(md_path) != lock["prediction_markdown_sha256"]:
                raise ValueError("frozen prediction/lock integrity failure " + eid)
            prediction = read_json(pred_path)
            if prediction.get("rule_id") != RULE_ID:
                raise ValueError("do not pool different frozen rules: " + eid)
            frozen_rule = prediction.get("frozen_rule")
            rule_payload = (json.dumps(frozen_rule,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n").encode("utf-8")
            if prediction.get("rule_sha256") != RULE_SHA256 or hashlib.sha256(rule_payload).hexdigest() != RULE_SHA256:
                raise ValueError("same rule ID with altered/missing frozen parameters cannot be pooled: " + eid)
            label = read_json(label_path)
            if label.get("prediction_sha256") != sha256(pred_path) or label.get("lock_sha256") != sha256(lock_path):
                raise ValueError("outcome is not linked to this prediction/lock " + eid)
            if label.get("episode_id") != eid or prediction.get("episode_id") != eid:
                raise ValueError("prediction/label episode mismatch")
            if label.get("asset_id", prediction["asset_id"]) != prediction["asset_id"] or label.get("cutoff_at", prediction["cutoff_at"]) != prediction["cutoff_at"]:
                raise ValueError("prediction/label asset or cutoff mismatch")
            for path in (lock_path, pred_path, md_path, label_path):
                sources[str(path)] = sha256(path)
            features = prediction.get("features", {})
            quality = prediction.get("input_quality", {})
            pred_h = prediction.get("horizons", {}).get(HORIZON, {})
            outcome = label.get("horizons", {}).get(HORIZON, {})
            sigma = features.get("annual_volatility_252")
            normalized = [features.get("r63")/sigma, features.get("r252")/sigma] if finite(sigma) and sigma > 0 and finite(features.get("r63")) and finite(features.get("r252")) else None
            status = outcome.get("status", label.get("status", "UNRESOLVED_DATA"))
            net = outcome.get("net_return")
            mature = status == "REVEALED" and finite(net)
            p_up = pred_h.get("p_up_scoring_probability")
            batch_name = root.parent.name if root.name == "run" else root.name
            domain = "SECTOR_PROXY" if "SECTOR" in batch_name else "CROSS_ASSET" if "XASSET" in batch_name else "MAINLAND_INDEX" if "ASHARE" in batch_name else "EQUITY_BENCHMARK" if batch_name.startswith("ROUND_002") or "XTIME" in batch_name else "OTHER_EXPLICIT_COHORT"
            row = {
                "episode_id": eid, "batch_path": str(root), "asset_id": prediction["asset_id"],
                "batch": batch_name, "analysis_domain": domain,
                "market": prediction["market"], "cutoff_at": prediction["cutoff_at"],
                "date_cluster": prediction["cutoff_at"][:10],
                "calendar_year": prediction["cutoff_at"][:4],
                "calendar_period_status": "CALENDAR_LABEL_NOT_MACRO_OR_CAUSAL_REGIME",
                "industry": quality.get("industry") or INDUSTRIES.get(prediction["asset_id"], "UNKNOWN_INDUSTRY"),
                "industry_status": "ETF_MANDATE_OR_FROZEN_INPUT_CATEGORY_NOT_POINT_IN_TIME_CONSTITUENT_INFERENCE",
                "ex_ante_trend_regime": prediction.get("regime", "INSUFFICIENT_HISTORY"),
                "features": features, "normalized_match_features": normalized,
                "exposure": prediction.get("exposure"), "probability_up": p_up,
                "probability_up_range": pred_h.get("p_up_range"),
                "outcome_status": status, "mature": mature,
                "return_basis": prediction.get("return_basis"), "tradability": prediction.get("tradability"),
                "currency": prediction.get("currency"), "net_return": net if mature else None,
                "actual_up": bool(net > 0) if mature else None,
                "actual_scenario": outcome.get("actual_scenario") if mature else None,
                "cash_status": prediction.get("cash_alternative_status"),
                "model_expected_value": pred_h.get("model_expected_value"),
                "model_ev_status": "UNFITTED_SCENARIO_ASSUMPTION_NOT_ESTIMATED_EXPECTED_RETURN",
                "max_adverse_excursion": outcome.get("max_adverse_excursion") if mature else None,
                "max_favorable_excursion": outcome.get("max_favorable_excursion") if mature else None,
                "max_drawdown": outcome.get("max_drawdown") if mature else None,
            }
            if mature:
                if not finite(p_up) or not 0 <= p_up <= 1 or row["exposure"] not in (0, 1):
                    raise ValueError("mature outcome without valid frozen probability/exposure: " + eid)
                actual_up = int(row["actual_up"])
                brier = (p_up-actual_up)**2
                if outcome.get("actual_up") is not None and bool(outcome["actual_up"]) != bool(actual_up):
                    raise ValueError("outcome event inconsistent with frozen event definition: " + eid)
                if finite(outcome.get("brier_score")) and not math.isclose(outcome["brier_score"], brier, abs_tol=1e-12):
                    raise ValueError("outcome Brier inconsistent with frozen probability: " + eid)
                decision = net if row["exposure"] else 0.0
                model_ev = row["model_expected_value"]
                row.update(
                    brier=brier, constant_05_brier=(.5-actual_up)**2,
                    constant_06_brier=(.6-actual_up)**2,
                    brier_delta_vs_constant_06=brier-(.6-actual_up)**2,
                    direction_correct=(actual_up == int(p_up > .5)) if p_up != .5 else None,
                    hypothetical_decision_return=decision,
                    hypothetical_decision_delta_vs_all_long=decision-net,
                    hypothetical_decision_delta_vs_assumed_cash0=decision,
                    model_ev_exposure_delta_vs_all_long=(row["exposure"]-1)*model_ev if finite(model_ev) else None,
                    model_ev_exposure_delta_vs_assumed_cash0=row["exposure"]*model_ev if finite(model_ev) else None,
                )
            rows.append(row)
    return rows, sources


def summarize_group(rows):
    valid = [r for r in rows if r["mature"]]
    direction = [r for r in valid if r.get("direction_correct") is not None]
    positive = [r for r in valid if r["net_return"] > 0]
    negative = [r for r in valid if r["net_return"] < 0]
    up_denom = sum(r["net_return"] for r in positive)
    down_denom = -sum(r["net_return"] for r in negative)
    calibration = []
    for low, high in ((0., .45), (.45, .55), (.55, 1.000001)):
        group = [r for r in valid if low <= r["probability_up"] < high]
        calibration.append({"bin": [low, min(high, 1.)], "n": len(group),
            "date_cluster_count": len({r["date_cluster"] for r in group}),
            "year_cluster_count": len({r["calendar_year"] for r in group}),
            "mean_probability": mean([r["probability_up"] for r in group]),
            "observed_up_fraction": mean([float(r["actual_up"]) for r in group]),
            "status": "DESCRIPTIVE_NOT_ESTABLISHED_CALIBRATION"})
    return {"n_locked": len(rows), "n_mature": len(valid), "n_unresolved_or_pending": len(rows)-len(valid),
        "date_cluster_count": len({r["date_cluster"] for r in valid}),
        "year_cluster_count": len({r["calendar_year"] for r in valid}),
        "locked_year_cluster_count": len({r["calendar_year"] for r in rows}),
        "independent_n": None, "effective_sample_status": "DEPENDENT_MARKETS_INDUSTRIES_AND_OVERLAPPING_HORIZONS",
        "mean_brier": mean([r["brier"] for r in valid]),
        "constant_05_brier": mean([r["constant_05_brier"] for r in valid]),
        "constant_06_brier": mean([r["constant_06_brier"] for r in valid]),
        "always_up_direction_accuracy": mean([float(r["actual_up"]) for r in valid]),
        "direction_accuracy": mean([float(r["direction_correct"]) for r in direction]),
        "n_direction_scored": len(direction),
        "mean_all_long_net_label": mean([r["net_return"] for r in valid]),
        "mean_hypothetical_decision_return": mean([r["hypothetical_decision_return"] for r in valid]),
        "upside_capture": sum(r["hypothetical_decision_return"] for r in positive)/up_denom if up_denom else None,
        "downside_avoidance": sum(r["hypothetical_decision_delta_vs_all_long"] for r in negative)/down_denom if down_denom else None,
        "mean_max_adverse_excursion": mean([r["max_adverse_excursion"] for r in valid]),
        "mean_max_favorable_excursion": mean([r["max_favorable_excursion"] for r in valid]),
        "calibration": calibration, "deltas": {key: mean([r.get(key) for r in valid]) for key in DELTA_METRICS},
        "return_average_status": "DESCRIPTIVE_LOCAL_CURRENCY_LABEL_AVERAGE_NOT_EXECUTABLE_PORTFOLIO_RETURN"}


def shared_cluster_bootstrap(rows, group_specs, unit="year", moving_block_years=0):
    """Resample shared years by default; fixed two-year block is sensitivity only."""
    if unit not in {"year", "date"} or moving_block_years not in {0, 2} or (moving_block_years and unit != "year"):
        raise ValueError("only shared year/date or fixed two-year sensitivity permitted")
    valid = [r for r in rows if r["mature"]]
    by_cluster = defaultdict(list)
    field = "calendar_year" if unit == "year" else "date_cluster"
    for row in valid:
        by_cluster[row[field]].append(row)
    clusters = sorted(by_cluster)
    if not clusters:
        return {"status": "NO_MATURE_LABELS", "groups": {}}
    rng = random.Random(BOOTSTRAP_SEED)
    windows = [[year, str(int(year)+1)] for year in clusters if str(int(year)+1) in by_cluster] if unit == "year" else []
    if moving_block_years:
        if not windows:
            return {"status":"NO_CONTIGUOUS_TWO_YEAR_WINDOWS","groups":{}}
        draws = [[year for _ in range(math.ceil(len(clusters)/2)) for year in rng.choice(windows)][:len(clusters)] for _ in range(BOOTSTRAP_DRAWS)]
    else:
        draws = [[rng.choice(clusters) for _ in clusters] for _ in range(BOOTSTRAP_DRAWS)]
    output = {"method": "FIXED_TWO_CALENDAR_YEAR_MOVING_BLOCK_PERCENTILE_SENSITIVITY" if moving_block_years else "SHARED_"+unit.upper()+"_CLUSTER_PERCENTILE_BOOTSTRAP", "seed": BOOTSTRAP_SEED,
        "draws": BOOTSTRAP_DRAWS, "date_cluster_count": len({r["date_cluster"] for r in valid}),
        "year_cluster_count": len({r["calendar_year"] for r in valid}), "resampled_cluster_count": len(clusters),
        "unit": unit, "independent_n": None,
        "resampling_unit": "entire calendar year including all March/September cutoffs, markets and industries" if unit == "year" else "entire cutoff date including every market/industry row at that date",
        "block_length_calendar_years": moving_block_years or None,
        "contiguous_year_windows": windows if moving_block_years else [],
        "block_edge_rule": "sample ceil(Kyears/2) non-circular overlapping contiguous two-year windows, concatenate and truncate to Kyears; gaps never treated as adjacent years" if moving_block_years else None,
        "limitations": ["March and September 12m windows overlap; date count is not independent sample size.",
            "Year clustering preserves within-year shocks but serial cross-year overlap remains; nominal intervals can be too narrow.",
            "Two-year moving blocks are a fixed descriptive sensitivity, not significance or a method chosen to improve the result.",
            "Small cluster count, adaptive expansion and nonrandom benchmark sample do not establish generalizable advantage.",
            "Unfitted model EV intervals describe variation in assumptions, not estimated expected-return uncertainty."], "groups": {}}
    for name, criterion in group_specs.items():
        belongs = lambda r: all(r.get(field) == value for field, value in criterion.items())
        actual = [r for r in valid if belongs(r)]
        metric_draws = {key: [] for key in DELTA_METRICS}
        for draw in draws:
            sample = [r for cluster in draw for r in by_cluster[cluster] if belongs(r)]
            for key in DELTA_METRICS:
                value = mean([r.get(key) for r in sample])
                if value is not None:
                    metric_draws[key].append(value)
        output["groups"][name] = {"n_mature": len(actual), "date_cluster_count": len({r["date_cluster"] for r in actual}),
            "year_cluster_count": len({r["calendar_year"] for r in actual}),
            "metrics": {key: {"estimate": mean([r.get(key) for r in actual]),
                "percentile_95_interval": [quantile(metric_draws[key], .025), quantile(metric_draws[key], .975)],
                "draws_with_nonmissing_group": len(metric_draws[key]),
                "sign_interpretation": "negative improves Brier" if key.startswith("brier") else "positive favors hypothetical exposure over stated baseline"}
                for key in DELTA_METRICS}}
    return output


def nearest_exante_pairs(rows):
    """Use all locked rows with valid features, even if their outcome is pending."""
    eligible = sorted([r for r in rows if r["normalized_match_features"] is not None], key=lambda r: r["episode_id"])
    pairs, unmatched = {}, []
    for anchor in eligible:
        candidates = [r for r in eligible if r["date_cluster"] != anchor["date_cluster"]]
        if not candidates:
            unmatched.append(anchor["episode_id"])
            continue
        distance = lambda r: math.sqrt(sum((a-b)**2 for a,b in zip(anchor["normalized_match_features"], r["normalized_match_features"])))
        other = min(candidates, key=lambda r: (distance(r), r["episode_id"]))
        key = tuple(sorted([anchor["episode_id"], other["episode_id"]]))
        if key not in pairs:
            pairs[key] = {"episode_ids": list(key), "feature_distance": distance(other), "selected_by_anchors": [],
                "outcome_statuses": {r["episode_id"]: r["outcome_status"] for r in (anchor, other)},
                "net_returns": {r["episode_id"]: r["net_return"] for r in (anchor, other)},
                "trend_regimes": {r["episode_id"]: r["ex_ante_trend_regime"] for r in (anchor, other)},
                "markets": {r["episode_id"]: r["market"] for r in (anchor, other)},
                "industries": {r["episode_id"]: r["industry"] for r in (anchor, other)},
                "reference_is_future_dated_by_anchor": {}}
        pairs[key]["selected_by_anchors"].append(anchor["episode_id"])
        pairs[key]["reference_is_future_dated_by_anchor"][anchor["episode_id"]] = other["date_cluster"] > anchor["date_cluster"]
    return {"method": "one nearest other-cutoff neighbor per eligible locked prediction; deduplicate undirected pairs",
        "features": ["r63/annual_volatility_252", "r252/annual_volatility_252"],
        "metric": "Euclidean", "tie_break": "lexicographic episode_id", "excluded": "same cutoff date; missing or nonpositive volatility",
        "outcomes_used_for_selection": False, "eligible_locked_count": len(eligible), "unmatched_episode_ids": unmatched,
        "historical_analogue_library_available_at_target_T": False,
        "limitations": "Reusable neighbors; no distance cutoff; no valuation/macro/industry matching; no causal interpretation or independent matched sample. Later-dated episodes may be references in this post-lock exploratory comparison, never an analogue available at target T or input to Stage A. Prospective analogues require reference outcome maturity <= target T.",
        "pairs": [pairs[key] for key in sorted(pairs)]}


def analyze(rows, sources=None, bootstrap_unit="year"):
    fields = ("analysis_domain", "batch", "market", "industry", "ex_ante_trend_regime", "calendar_year", "return_basis", "tradability")
    groups = {field: {str(value): summarize_group([r for r in rows if r.get(field) == value]) for value in sorted({r.get(field) for r in rows}, key=str)} for field in fields}
    specs = {"ALL": {}}
    for field in ("analysis_domain", "batch", "market", "industry", "ex_ante_trend_regime"):
        for value in sorted({r.get(field) for r in rows}, key=str):
            specs[field+":"+str(value)] = {field: value}
    valid = [r for r in rows if r["mature"]]
    counterexamples = {
        "positive_trend_loses": [r["episode_id"] for r in valid if r["exposure"] == 1 and r["net_return"] < 0],
        "negative_or_mixed_misses_up": [r["episode_id"] for r in valid if r["exposure"] == 0 and r["net_return"] > 0],
        "negative_or_mixed_misses_bull_scenario": [r["episode_id"] for r in valid if r["exposure"] == 0 and r["actual_scenario"] == "Bull"],
        "positive_trend_ordinary_or_bear": [r["episode_id"] for r in valid if r["exposure"] == 1 and r["actual_scenario"] != "Bull"],
    }
    return {"analysis_id": "NIGHT_FIXED_12M_DESCRIPTIVE", "created_at": datetime.now(timezone.utc).isoformat(),
        "horizon": HORIZON, "rule_id": RULE_ID, "rule_sha256": RULE_SHA256,
        "analyzer_source_sha256": sha256(__file__),
        "parameter_searches": 0, "status": "NO_ROBUST_PATTERN_ESTABLISHED_BY_THIS_ANALYSIS",
        "causal_evidence": "NONE", "candidate_evidence_ceiling": "C_PRELIMINARY", "prospective_validation": False,
        "source_sha256": sources or {}, "overall": summarize_group(rows), "groups": groups,
        "counterexamples": counterexamples,
        "shared_cluster_bootstrap": shared_cluster_bootstrap(rows, specs, unit=bootstrap_unit),
        "shared_date_cluster_bootstrap": shared_cluster_bootstrap(rows, specs, unit="date"),
        "fixed_two_year_block_sensitivity": shared_cluster_bootstrap(rows, specs, unit="year", moving_block_years=2),
        "nearest_exante_pairs": nearest_exante_pairs(rows), "rows": rows,
        "limitations": ["All batches are historical masked replays; rules designed today may encode historical priors.",
            "Successive batches chosen after seeing previous results are adaptive exploratory cohorts, never independent confirmatory holdouts.",
            "Industry labels follow ETF mandates/frozen inputs; no claim about historical constituents, earnings, valuation or capital cycle.",
            "Calendar year is a calendar label, not an inferred causal or macro regime.",
            "Pooling weights each mature row equally; cohorts with more industry assets give their dates/markets more weight. No representative portfolio allocation is implied.",
            "Cash zero and transaction costs are frozen assumptions; native indices use price labels, ETFs economic total return conventions.",
            "Brier and all-long baselines describe odds discrimination; above-zero average return alone does not establish skill.",
            "Missing/pending labels remain missing and cannot contribute zero returns or failures.",
            "Output hashes are content audit, not immutable storage or independent trusted timestamps."]}


def markdown(result):
    total = result["overall"]
    out = ["# 夜间研究：固定12个月描述性比较", "", "状态：`NO ROBUST PATTERN ESTABLISHED BY THIS ANALYSIS`；不是策略成立或前瞻盲测。", "",
        f"已锁 {total['n_locked']} 行；成熟 {total['n_mature']} 行；日期簇 {total['date_cluster_count']}；成熟年份簇 {total['year_cluster_count']}（设计年份 {total['locked_year_cluster_count']}）；独立N未知。", "",
        "|范围|成熟行|日期簇|Brier|常数60% Brier|方向准确率|总是看涨|假设曝光收益|All-long标签收益|", "|---|---|---|---|---|---|---|---|---|"]
    def number(value): return "null" if value is None else f"{value:.5f}"
    out.append("|全部|"+"|".join([str(total["n_mature"]),str(total["date_cluster_count"]),number(total["mean_brier"]),number(total["constant_06_brier"]),number(total["direction_accuracy"]),number(total["always_up_direction_accuracy"]),number(total["mean_hypothetical_decision_return"]),number(total["mean_all_long_net_label"])])+"|")
    for field in ("analysis_domain", "batch", "market", "industry", "ex_ante_trend_regime", "calendar_year"):
        for name, value in result["groups"][field].items():
            out.append("|"+field+":"+name+"|"+"|".join([str(value["n_mature"]),str(value["date_cluster_count"]),number(value["mean_brier"]),number(value["constant_06_brier"]),number(value["direction_accuracy"]),number(value["always_up_direction_accuracy"]),number(value["mean_hypothetical_decision_return"]),number(value["mean_all_long_net_label"])])+"|")
    out += ["", "年份只是日历分组；产业是基金授权范围。混合本币百分比平均不构成可执行投资组合收益。", "", "## 概率校准", "", "|代表概率分箱|成熟行|日期簇|平均预测|实际上涨比例|", "|---|---|---|---|---|"]
    for group in total["calibration"]:
        out.append(f"|{group['bin']}|{group['n']}|{group['date_cluster_count']}|{number(group['mean_probability'])}|{number(group['observed_up_fraction'])}|")
    bootstrap = result["shared_cluster_bootstrap"]
    out += ["", "## 共享年份簇重采样与固定敏感性", "", f"默认单位 {bootstrap.get('unit')}；固定seed {BOOTSTRAP_SEED}，{BOOTSTRAP_DRAWS}次；同年份全部March/September、市场和产业一起抽样。3月与9月12m窗口重叠，增加日期不等于增加独立年份，跨年重叠仍会使区间过窄。另固定2个连续calendar-year移动块，仅作描述性敏感性，旧日期簇结果也保留。", "", "|配对差值|估计|默认簇95%区间|固定2年移动块95%区间|", "|---|---|---|---|"]
    boot = bootstrap.get("groups", {}).get("ALL", {}).get("metrics", {})
    block = result["fixed_two_year_block_sensitivity"].get("groups", {}).get("ALL", {}).get("metrics", {})
    for name, value in boot.items():
        out.append(f"|{name}|{number(value['estimate'])}|{value['percentile_95_interval']}|{block.get(name,{}).get('percentile_95_interval')}|")
    out += ["", "Brier差值负为改善；曝光收益差值正为改善。Model EV来自未经校准的情景假设；其区间不是实证预期收益区间。", "", "## 反例与错过赢家", ""]
    for name, ids in result["counterexamples"].items():
        out.append(f"- {name} ({len(ids)}): {', '.join(ids) or '无成熟案例'}")
    pairs = result["nearest_exante_pairs"]
    out += ["", "## 相近事前条件案例", "", "只使用r63/年波动、r252/年波动欧氏距离；排除相同cutoff日期；选邻居时不读结果，也保留其未成熟结果。邻居可重用，没有距离阈值，不是因果对照。此为锁后探索比较：邻居可能发生在目标T之后，不是当时可用类比库，更不得回写Stage A。JSON逐anchor标明是否引用未来日期；未来使用类比时要求参考案例结果成熟时间≤目标T。", "", "|案例对|事前距离|12m标签|", "|---|---|---|"]
    for pair in pairs["pairs"]:
        out.append(f"|{' / '.join(pair['episode_ids'])}|{pair['feature_distance']:.5f}|{pair['net_returns']}|")
    out += ["", "## 限制", ""]+["- "+x for x in result["limitations"]]
    out += ["", "完整市场/行业/趋势分组、全部反例、重采样与输入哈希见同名JSON；本工具不新增已验证原则。", ""]
    return "\n".join(out)


def write_csv_rows(path, rows):
    """Flatten all locked rows; null remains an empty CSV cell, never zero."""
    fields = ["episode_id","batch","analysis_domain","asset_id","market","industry","cutoff_at","calendar_year","date_cluster","outcome_status","mature","currency","return_basis","tradability","ex_ante_trend_regime","exposure","probability_up","probability_up_lower","probability_up_upper","r63","r252","annual_volatility_252","normalized_r63_vol","normalized_r252_vol","net_return","actual_up","actual_scenario","brier","constant_05_brier","constant_06_brier","brier_delta_vs_constant_06","hypothetical_decision_return","hypothetical_decision_delta_vs_all_long","hypothetical_decision_delta_vs_assumed_cash0","model_expected_value","model_ev_status","model_ev_exposure_delta_vs_all_long","model_ev_exposure_delta_vs_assumed_cash0","max_adverse_excursion","max_favorable_excursion","max_drawdown","cash_status"]
    with Path(path).open("x",encoding="utf-8",newline="") as out:
        writer=csv.DictWriter(out,fieldnames=fields);writer.writeheader()
        for row in rows:
            flat={field:row.get(field) for field in fields}
            features=row.get("features",{})
            for field in ("r63","r252","annual_volatility_252"):flat[field]=features.get(field)
            interval=row.get("probability_up_range") or [None,None]
            flat["probability_up_lower"],flat["probability_up_upper"]=interval
            normalized=row.get("normalized_match_features") or [None,None]
            flat["normalized_r63_vol"],flat["normalized_r252_vol"]=normalized
            writer.writerow(flat)


def plot_calibration(result, png_path, pdf_path):
    """Static export only. Common axes; observed rate and denominator, no fake CI."""
    os.environ.setdefault("MPLCONFIGDIR","/tmp/investment-lab-matplotlib")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows=result["rows"]
    panels=[]
    for market in sorted({r["market"] for r in rows}):
        panels.append(("Market: "+market,[r for r in rows if r["market"]==market]))
    sector_names=[("XLK","Technology"),("SOXX","Semiconductors"),("XLE","Energy/resources"),("XLV","Healthcare"),("XLY","Consumer discretionary"),("XLI","Industrial/manufacturing"),("XLU","Utilities")]
    for asset,label in sector_names:
        group=[r for r in rows if r["asset_id"]==asset]
        panels.append((label+" ("+asset+")",group))
    ncols=4;nrows=math.ceil(len(panels)/ncols)
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.titlesize":11,"axes.labelsize":10,"figure.facecolor":"white","axes.facecolor":"white","savefig.facecolor":"white","pdf.fonttype":42})
    fig,axes=plt.subplots(nrows,ncols,figsize=(15,3.4*nrows),squeeze=False)
    colors={.4:"#355C7D",.5:"#B68226",.6:"#A24B67"}
    markers={.4:"o",.5:"s",.6:"^"}
    chart_rows=[]
    for axis,(title,group) in zip(axes.flat,panels):
        stats=summarize_group(group)
        axis.plot([0,100],[0,100],color="#444444",linewidth=1,linestyle="--",label="Ideal calibration")
        axis.axhline(60,color="#757575",linewidth=1,linestyle=":",label="Constant 60% prior")
        for binrow in stats["calibration"]:
            if not binrow["n"]:continue
            p=round(binrow["mean_probability"],1);x=100*binrow["mean_probability"];y=100*binrow["observed_up_fraction"]
            axis.scatter([x],[y],s=65,color=colors.get(p,"#355C7D"),marker=markers.get(p,"o"),edgecolor="#333333",linewidth=.6,zorder=3)
            axis.annotate("n="+str(binrow["n"]),(x,y),xytext=(4,5 if p!=.5 else -13),textcoords="offset points",fontsize=8,color="#333333")
            chart_rows.append({"panel":title,"predicted_up_probability":binrow["mean_probability"],"observed_up_fraction":binrow["observed_up_fraction"],"n":binrow["n"],"year_clusters":binrow["year_cluster_count"]})
        axis.set_title(title+f"\nN={stats['n_mature']}, years={stats['year_cluster_count']}",loc="left")
        axis.set_xlim(0,100);axis.set_ylim(0,100);axis.set_xticks([0,40,60,100]);axis.set_yticks([0,40,60,100])
        axis.set_xlabel("Frozen probability up (%)");axis.set_ylabel("Observed 12m up fraction (%)")
        axis.grid(axis="y",color="#E6E6E6",linewidth=.6)
        axis.spines[["top","right"]].set_visible(False)
        if not stats["n_mature"]:axis.text(.5,.2,"No mature labels",transform=axis.transAxes,ha="center",fontsize=10)
    for axis in list(axes.flat)[len(panels):]:axis.set_visible(False)
    finance=summarize_group([r for r in rows if r["asset_id"]=="XLF"])
    fig.suptitle("Frozen 40/50/60% priors versus observed 12-month outcomes",x=.035,ha="left",fontsize=15,fontweight="bold",y=.985)
    fig.text(.035,.949,"Historical masked replay; shared year dependence. Labels include local-currency price indices and ETF economic returns.",fontsize=10,color="#444444")
    fig.text(.035,.022,f"Financial proxy XLF: {finance['n_mature']}/{finance['n_locked']} mature. Missing labels excluded. Markers show unfitted priors; rates do not establish calibration.\nDashed diagonal: ideal probability calibration. Dotted horizontal: unfitted constant 60% baseline. No binomial CI assumes independent rows.",fontsize=9,color="#444444")
    fig.subplots_adjust(left=.065,right=.99,top=.89,bottom=.105,hspace=.66,wspace=.42)
    for path in (png_path,pdf_path):
        if Path(path).exists():raise FileExistsError(str(path))
    fig.savefig(png_path,dpi=180)
    fig.savefig(pdf_path)
    plt.close(fig)
    return {"chart_type":"common-scale calibration small multiples","data":chart_rows,"financial_proxy":finance,"png":str(png_path),"pdf":str(pdf_path),"png_sha256":sha256(png_path),"pdf_sha256":sha256(pdf_path),"uncertainty_status":"no statistical binomial CI; year dependence and exploratory sampling explicitly disclosed"}


def synthetic_self_test():
    """No real labels; exercise date clustering and matching anti-leakage."""
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    from lab.replay import RULE as engine_rule
    rows = []
    for i in range(8):
        for j in range(2):
            net = .10 if (i+j)%3 else -.08
            exposure = int(i%2 == 0)
            p_up = .6 if exposure else .4
            actual_up = int(net > 0)
            brier = (p_up-actual_up)**2
            rows.append({"episode_id":f"SYNTH-{i}-{j}", "date_cluster":f"{2000+i}-09-30", "calendar_year":str(2000+i),
                "asset_id":f"SYNTH-{j}", "market":f"SYNTH-{j}", "industry":"SYNTHETIC_ONLY", "ex_ante_trend_regime":"POSITIVE_TREND" if exposure else "NEGATIVE_TREND", "exposure":exposure,
                "normalized_match_features":[i/10+j/100,(i-3)/10], "mature":True, "net_return":net, "actual_up":bool(actual_up), "actual_scenario":"Bull" if net>0 else "Bear", "probability_up":p_up,
                "outcome_status":"REVEALED", "brier":brier, "constant_05_brier":.25,"constant_06_brier":(.6-actual_up)**2,
                "direction_correct":actual_up==int(p_up>.5),"hypothetical_decision_return":net*exposure,
                "brier_delta_vs_constant_06":brier-(.6-actual_up)**2,
                "hypothetical_decision_delta_vs_all_long":net*(exposure-1),"hypothetical_decision_delta_vs_assumed_cash0":net*exposure,
                "model_ev_exposure_delta_vs_all_long":.02*(exposure-1),"model_ev_exposure_delta_vs_assumed_cash0":.02*exposure,
                "max_adverse_excursion":-.1,"max_favorable_excursion":.15,"return_basis":"SYNTHETIC_ONLY","tradability":"SYNTHETIC_ONLY"})
    a=analyze(rows); b=analyze(rows)
    assert a["shared_cluster_bootstrap"]["unit"] == "year"
    assert a["fixed_two_year_block_sensitivity"]["block_length_calendar_years"] == 2
    assert a["shared_date_cluster_bootstrap"] == b["shared_date_cluster_bootstrap"]
    assert a["overall"]["date_cluster_count"] == 8 and a["overall"]["n_mature"] == 16
    pair_selection = [(p["episode_ids"],p["feature_distance"]) for p in a["nearest_exante_pairs"]["pairs"]]
    mutated = [dict(r,net_return=1000+r["net_return"],actual_up=False) for r in rows]
    same = nearest_exante_pairs(mutated)
    assert pair_selection == [(p["episode_ids"],p["feature_distance"]) for p in same["pairs"]]
    mapping = {r["episode_id"]:r for r in rows}
    for p in a["nearest_exante_pairs"]["pairs"]:
        assert len({mapping[e]["date_cluster"] for e in p["episode_ids"]}) == 2
    unresolved = dict(rows[0],episode_id="SYNTH-PENDING",mature=False,net_return=None,outcome_status="PENDING_HORIZON",normalized_match_features=[.001,.002])
    full = analyze(rows+[unresolved])
    assert full["overall"]["n_mature"] == 16 and full["overall"]["n_unresolved_or_pending"] == 1
    assert full["nearest_exante_pairs"]["eligible_locked_count"] == 17
    assert len(a["shared_date_cluster_bootstrap"]["groups"]["ALL"]["metrics"]) == len(DELTA_METRICS)
    with tempfile.TemporaryDirectory(prefix="night-analysis-synthetic-") as temp:
        p=Path(temp)/"fixture.json";p.write_text(json.dumps(a,allow_nan=False));read_json(p)
        assert "固定12个月" in markdown(a)
        batch=Path(temp)/"batch"
        try:load_completed_batches([batch])
        except ValueError:pass
        else:raise AssertionError("unlocked/unrevealed input accepted")
        eid="SYNTH-LOADER-001"
        for name in ("predictions","locks","labels"):(batch/name).mkdir(parents=True,exist_ok=True)
        pred={"episode_id":eid,"asset_id":"SYNTH","market":"SYNTH","cutoff_at":"2000-09-30T23:59:59+00:00","rule_id":RULE_ID,"rule_sha256":RULE_SHA256,"frozen_rule":engine_rule,"features":{"r63":.05,"r252":.1,"annual_volatility_252":.2},"input_quality":{},"horizons":{"12m":{"p_up_scoring_probability":.6,"p_up_range":[.45,.75],"model_expected_value":.02}},"exposure":1,"regime":"POSITIVE_TREND","return_basis":"PRICE_ONLY","tradability":"SYNTHETIC_ONLY","currency":"USD"}
        pp=batch/"predictions"/(eid+".v001.json");mp=batch/"predictions"/(eid+".v001.md")
        pp.write_text(json.dumps(pred));mp.write_text("SYNTHETIC ENGINEERING ONLY")
        lp=batch/"locks"/(eid+".v001.lock.json")
        lp.write_text(json.dumps({"prediction_sha256":sha256(pp),"prediction_markdown_sha256":sha256(mp)}))
        (batch/"all_locks.v001.json").write_text(json.dumps({"status":"ALL_EX_ANTE_LOCKED","episode_ids":[eid],"lock_sha256":{eid:sha256(lp)}}))
        (batch/"evaluation_summary.v001.json").write_text("{}")
        label={"episode_id":eid,"prediction_sha256":sha256(pp),"lock_sha256":sha256(lp),"horizons":{"12m":{"status":"REVEALED","net_return":.1,"actual_up":True,"actual_scenario":"Bull","brier_score":.16}}}
        lab=batch/"labels"/(eid+".v001.json");lab.write_text(json.dumps(label))
        loaded,sources=load_completed_batches([batch]);assert len(loaded)==1 and loaded[0]["mature"] and len(sources)==6
        pp.write_text(pp.read_text()+" ")
        try:load_completed_batches([batch])
        except ValueError:pass
        else:raise AssertionError("tampered frozen prediction accepted")
        march=dict(rows[0],episode_id="SYNTH-MARCH",date_cluster="2000-03-31")
        both=analyze(rows+[march])
        assert both["overall"]["date_cluster_count"]==9 and both["overall"]["year_cluster_count"]==8
        csvpath=Path(temp)/"all.csv";write_csv_rows(csvpath,rows+[unresolved])
        with csvpath.open() as csvinput:csvrows=list(csv.DictReader(csvinput))
        assert len(csvrows)==17 and csvrows[-1]["net_return"]==""
    return {"status":"PASS","scope":"SYNTHETIC_ENGINEERING_ONLY_NOT_INVESTMENT_EVIDENCE", "checks":14,"synthetic_date_clusters":8,"synthetic_rows":16,"real_labels_read":False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch",action="append",default=[],help="Completed replay output directory; repeat for completed cohorts only")
    parser.add_argument("--output-dir",default="research/night")
    parser.add_argument("--name",default="fixed_12m_analysis.v001",help="Append a unique version; existing evidence is never overwritten")
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--bootstrap-unit",choices=["year","date"],default="year")
    args=parser.parse_args()
    if args.self_test:
        print(json.dumps(synthetic_self_test(),ensure_ascii=False));return
    if not args.batch:
        parser.error("at least one explicitly completed --batch is required")
    if Path(args.name).name != args.name:
        parser.error("--name must be a filename stem, not a path")
    rows,sources=load_completed_batches(args.batch)
    result=analyze(rows,sources,bootstrap_unit=args.bootstrap_unit)
    directory=Path(args.output_dir);directory.mkdir(parents=True,exist_ok=True)
    jp=directory/(args.name+".json");mp=directory/(args.name+".md")
    cp=directory/(args.name+".all_locked.csv");mcp=directory/(args.name+".mature.csv")
    png=directory/(args.name+".calibration.png");pdf=directory/(args.name+".calibration.pdf")
    if any(path.exists() for path in (jp,mp,cp,mcp,png,pdf)):
        raise FileExistsError("analysis already exists; choose a new --name version")
    write_csv_rows(cp,rows);write_csv_rows(mcp,[r for r in rows if r["mature"]])
    result["csv_artifacts"]={"all_locked":{"path":str(cp),"rows":len(rows),"sha256":sha256(cp)},"mature":{"path":str(mcp),"rows":sum(r["mature"] for r in rows),"sha256":sha256(mcp)},"missing_value_convention":"empty cell, never zero"}
    result["calibration_figure"]=plot_calibration(result,png,pdf)
    with jp.open("x",encoding="utf-8") as out:json.dump(result,out,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False);out.write("\n")
    with mp.open("x",encoding="utf-8") as out:out.write(markdown(result))
    print(json.dumps({"json":str(jp),"markdown":str(mp),"mature_rows":result["overall"]["n_mature"],"date_clusters":result["overall"]["date_cluster_count"],"year_clusters":result["overall"]["year_cluster_count"],"csv":str(cp),"png":str(png),"pdf":str(pdf),"status":result["status"]},ensure_ascii=False))


if __name__=="__main__":main()
