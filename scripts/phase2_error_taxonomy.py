#!/usr/bin/env python3
"""Audit existing frozen forecasts; never refit or generate replacement predictions.

Classification is an outcome audit. Its examples are explicitly selected AFTER
reveal and must never be reused as independent confirmation of a new condition.
"""
import csv
import hashlib
import io
import json
import math
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCHES = (
    "ROUND_002_V003", "NIGHT_XTIME_V003", "NIGHT_SECTOR_V002",
    "NIGHT_XASSET", "NIGHT_ASHARE", "NIGHT_CALENDAR_CONTROL",
    "NIGHT_EARLY", "NIGHT_RECENT",
)
HORIZONS = ("1w", "1m", "3m", "6m", "12m", "24m")
RULE_HASH = "3f45039c4376334501be3e177bab113cc65d7f4b3296f9c6b2e82e66a57b5729"
CONTEXT = ("Macro", "Rates", "Inflation", "Credit", "Liquidity", "Valuation",
           "Breadth", "Industry", "Earnings", "Policy", "Capital Actions",
           "News", "Sentiment")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def payload(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def mean(items):
    values = [x for x in items if isinstance(x, (int, float)) and math.isfinite(x)]
    return statistics.mean(values) if values else None


def classification(probability, net):
    if probability == .5:
        return "ABSTAIN"
    if probability > .5:
        return "TRUE_POSITIVE" if net > 0 else "FALSE_POSITIVE"
    return "FALSE_NEGATIVE" if net > 0 else "TRUE_NEGATIVE"


def assert_hash(path, expected):
    actual = digest(path)
    assert actual == expected, f"hash mismatch: {path}"
    return actual


def audit_rows():
    rows, provenance, batch_counts, evidence = [], {}, {}, {}
    unique_ids = set()
    from datetime import datetime
    for batch in BATCHES:
        directory = ROOT / "research/replays" / batch
        run = directory / "run"
        sentinel = load(run / "all_locks.v001.json")
        assert sentinel["status"] == "ALL_EX_ANTE_LOCKED"
        assert (run / "evaluation_summary.v001.json").is_file()
        manifest_path = directory / "ex_ante/manifest.json"
        manifest = load(manifest_path)
        manifest_hash = assert_hash(manifest_path, sentinel["input_manifest_sha256"])
        bundle_hash = digest(directory / "admin_bundle.v001.json")
        assert_hash(directory / "selection.v001.json", sentinel["selection_sha256"])
        assert_hash(directory / "preregistration.v001.json", sentinel["preregistration_sha256"])
        for code, expected in sentinel["implementation_sha256"].items():
            assert_hash(ROOT / code, expected)
        provenance[batch] = {
            "all_locks_sha256": digest(run / "all_locks.v001.json"),
            "evaluation_summary_sha256": digest(run / "evaluation_summary.v001.json"),
            "source_bundle_sha256": bundle_hash,
            "input_manifest_sha256": manifest_hash,
            "selection_sha256": sentinel["selection_sha256"],
            "preregistration_sha256": sentinel["preregistration_sha256"],
            "implementation_sha256": sentinel["implementation_sha256"],
        }
        statuses = Counter()
        for eid in sentinel["episode_ids"]:
            assert eid not in unique_ids
            unique_ids.add(eid)
            lock_path = run / "locks" / f"{eid}.v001.lock.json"
            pred_path = run / "predictions" / f"{eid}.v001.json"
            label_path = run / "labels" / f"{eid}.v001.json"
            lock = load(lock_path)
            lock_hash = assert_hash(lock_path, sentinel["lock_sha256"][eid])
            pred_hash = assert_hash(pred_path, lock["prediction_sha256"])
            assert_hash(run / "predictions" / f"{eid}.v001.md", lock["prediction_markdown_sha256"])
            input_path = directory / "ex_ante" / lock["input_path"]
            input_hash = assert_hash(input_path, lock["input_sha256"])
            assert input_hash == manifest["inputs"][eid]["sha256"]
            prediction, label, packet = load(pred_path), load(label_path), load(input_path)
            assert prediction["rule_id"] == "R002-TREND-PRIOR-v001"
            assert prediction["rule_sha256"] == RULE_HASH
            assert hashlib.sha256(payload(prediction["frozen_rule"])).hexdigest() == RULE_HASH
            assert label["prediction_sha256"] == pred_hash
            assert label["lock_sha256"] == lock_hash
            assert label["source_bundle_sha256"] == bundle_hash
            assert label["episode_id"] == prediction["episode_id"] == packet["episode_id"] == eid
            assert label.get("asset_id", prediction["asset_id"]) == prediction["asset_id"] == packet["asset_id"]
            assert label.get("cutoff_at", prediction["cutoff_at"]) == prediction["cutoff_at"] == packet["cutoff_at"]
            cutoff = datetime.fromisoformat(packet["cutoff_at"])
            assert packet["metadata"]["original_vintage_status"] == "NOT_ARCHIVED_PROVIDER_CORRECTIONS_POSSIBLE"
            for source in packet["prices"] + packet.get("actions", []) + packet.get("context", []):
                assert datetime.fromisoformat(source["available_at"]) <= cutoff
                assert source["source_sha256"] and source["source_id"]
            context_state = prediction.get("context_state", {})
            missing = {k: context_state.get(k, {}).get("status") != "KNOWN_AT_T" for k in CONTEXT}
            context_age = {}
            for category in CONTEXT:
                observed = [source for source in packet.get("context", []) if source.get("category") == category]
                latest = max((datetime.fromisoformat(source["available_at"]) for source in observed), default=None)
                context_age[category] = (cutoff-latest).total_seconds()/86400 if latest is not None else None
            features = prediction.get("features", {})
            if features.get("r63") is not None:
                ids = set(features["evidence_record_ids"])
                known = [{k: source.get(k) for k in (
                    "record_id", "date", "available_at", "source_id", "source_sha256", "pit_status")}
                    for source in packet["prices"] if source["record_id"] in ids]
                assert len(known) == len(ids)
                evidence[eid] = known
            for horizon in HORIZONS:
                outcome = label.get("horizons", {}).get(horizon, {})
                forecast = prediction.get("horizons", {}).get(horizon, {})
                status = outcome.get("status", label.get("status", "UNRESOLVED_DATA"))
                statuses[(horizon, status)] += 1
                net = outcome.get("net_return")
                mature = status == "REVEALED" and isinstance(net, (int, float)) and math.isfinite(net)
                p = forecast.get("p_up_scoring_probability")
                if mature:
                    assert p in (.4, .5, .6)
                    assert outcome["actual_up"] == (net > 0)
                    assert p == outcome["predicted_up_probability"]
                    assert prediction["exposure"] in (0, 1)
                    upper, lower = forecast["scenario_threshold_upper"], forecast["scenario_threshold_lower"]
                    scenario = "Bull" if net > upper else "Bear" if net < lower else "Base"
                    assert scenario == outcome["actual_scenario"]
                    assert math.isclose(outcome["brier_score"], (p - int(net > 0)) ** 2, abs_tol=1e-12)
                    tag = classification(p, net)
                    wait = prediction["exposure"] == 0
                else:
                    tag, wait, scenario = "UNSCORED", None, None
                rows.append({
                    "episode_id": eid, "batch": batch, "cohort": "ORIGINAL_282" if batch in BATCHES[:5] else "ADDED_COHORT",
                    "asset_id": prediction["asset_id"], "market": prediction["market"], "currency": prediction["currency"],
                    "cutoff_at": prediction["cutoff_at"], "horizon": horizon, "mature": mature, "outcome_status": status,
                    "probability_up": p, "classification": tag, "exposure": prediction.get("exposure"),
                    "no_trade_class": ("MISSED_OPPORTUNITY_PROXY" if scenario == "Bull" else "CORRECT_NO_TRADE_PROXY") if wait else None,
                    "net_return": net if mature else None, "actual_scenario": scenario,
                    "max_adverse_excursion_gross": outcome.get("max_adverse_excursion") if mature else None,
                    "max_favorable_excursion_gross": outcome.get("max_favorable_excursion") if mature else None,
                    "max_drawdown_close_basis_gross": outcome.get("max_drawdown") if mature else None,
                    "entry_date": outcome.get("entry_date"), "exit_date": outcome.get("exit_date"),
                    "r63_known_at_t": features.get("r63"), "r252_known_at_t": features.get("r252"),
                    "annual_volatility_known_at_t": features.get("annual_volatility_252"),
                    "trend_regime_known_at_t": prediction.get("regime"), "missing_context": missing,
                    "context_latest_observation_age_days": context_age,
                    "actual_error_cause": "UNIDENTIFIED_NOT_INFERRED_FROM_PRICE_LABEL",
                    "prediction_path": str(pred_path.relative_to(ROOT)), "input_path": str(input_path.relative_to(ROOT)),
                    "label_path": str(label_path.relative_to(ROOT)), "prediction_sha256": pred_hash,
                    "input_sha256": input_hash, "label_sha256": digest(label_path), "source_bundle_sha256": bundle_hash,
                    "rule_sha256": RULE_HASH, "return_basis": prediction["return_basis"], "tradability": prediction["tradability"],
                    "context_evidence_record_ids": {k: context_state.get(k, {}).get("evidence_record_ids", []) for k in CONTEXT},
                })
        batch_counts[batch] = {
            "selected_rows": len(sentinel["episode_ids"]),
            "horizon_statuses": {h: {s: n for (hh, s), n in statuses.items() if hh == h} for h in HORIZONS},
        }
    return rows, provenance, batch_counts, evidence


def summarize(rows):
    out = {}
    for h in HORIZONS:
        all_rows = [r for r in rows if r["horizon"] == h]
        mature = [r for r in all_rows if r["mature"]]
        counts = Counter(r["classification"] for r in mature)
        wait_counts = Counter(r["no_trade_class"] for r in mature if r["exposure"] == 0)
        scored = [r for r in mature if r["classification"] != "ABSTAIN"]
        out[h] = {
            "n_selected": len(all_rows), "n_mature": len(mature), "n_unscored": len(all_rows)-len(mature),
            "classification_counts": {c: counts[c] for c in ("TRUE_POSITIVE", "FALSE_POSITIVE", "TRUE_NEGATIVE", "FALSE_NEGATIVE", "ABSTAIN")},
            "wait_outcome_proxy_counts": dict(wait_counts),
            "date_cluster_count": len({r["cutoff_at"][:10] for r in mature}),
            "year_cluster_count": len({r["cutoff_at"][:4] for r in mature}),
            "direction_accuracy_on_nonabstained": sum(r["classification"] in ("TRUE_POSITIVE", "TRUE_NEGATIVE") for r in scored)/len(scored) if scored else None,
            "calibration": [{
                "probability": p, "n": sum(r["probability_up"] == p for r in mature),
                "actual_up_fraction": mean([int(r["net_return"] > 0) for r in mature if r["probability_up"] == p]),
                "mean_net_label": mean([r["net_return"] for r in mature if r["probability_up"] == p]),
            } for p in (.4, .5, .6)],
        }
        assert sum(out[h]["classification_counts"].values()) == len(mature)
        assert sum(wait_counts.values()) == sum(r["exposure"] == 0 for r in mature)
    return out


def missing_comparison(rows):
    primary = [r for r in rows if r["horizon"] == "12m" and r["mature"]]
    groups = {
        "ERROR_FP_FN": [r for r in primary if r["classification"] in ("FALSE_POSITIVE", "FALSE_NEGATIVE")],
        "CORRECT_TP_TN": [r for r in primary if r["classification"] in ("TRUE_POSITIVE", "TRUE_NEGATIVE")],
        "ABSTAIN": [r for r in primary if r["classification"] == "ABSTAIN"],
        "ALL": primary,
    }
    return {k: {"n": len(group), "missing_context": {
        c: {"n_missing": sum(r["missing_context"][c] for r in group),
            "fraction_missing": mean([int(r["missing_context"][c]) for r in group])}
        for c in CONTEXT}, "latest_observation_age_days": {
        c: {"n_observed": len(v), "mean_days": mean(v), "max_days": max(v) if v else None}
        for c in CONTEXT for v in [[r["context_latest_observation_age_days"][c] for r in group
                                   if r["context_latest_observation_age_days"][c] is not None]]}}
        for k, group in groups.items()}


def feature_diagnostics(rows):
    primary = [r for r in rows if r["horizon"] == "12m" and r["mature"]]
    return {c: {"n": len(g), "mean_r63": mean([r["r63_known_at_t"] for r in g]),
                "mean_r252": mean([r["r252_known_at_t"] for r in g]),
                "mean_past_annual_volatility": mean([r["annual_volatility_known_at_t"] for r in g]),
                "mean_net_label": mean([r["net_return"] for r in g]),
                "mean_gross_mae": mean([r["max_adverse_excursion_gross"] for r in g])}
            for c in ("TRUE_POSITIVE", "FALSE_POSITIVE", "TRUE_NEGATIVE", "FALSE_NEGATIVE", "ABSTAIN")
            for g in [[r for r in primary if r["classification"] == c]]}


def select_audit_examples(rows, evidence):
    """Six outcome-selected diagnostics, NOT new neutral test episodes."""
    primary = [r for r in rows if r["horizon"] == "12m" and r["mature"]]
    examples = []
    for market in ("US", "HK", "JP"):
        for tag in ("FALSE_POSITIVE", "FALSE_NEGATIVE"):
            matches = [r for r in primary if r["market"] == market and r["classification"] == tag]
            assert matches, (market, tag)
            example = min(matches, key=lambda r: (r["net_return"], r["episode_id"])) if tag == "FALSE_POSITIVE" else max(matches, key=lambda r: (r["net_return"], r["episode_id"]))
            examples.append({
                "selection": "POST_REVEAL_DIAGNOSTIC_EXTREME_PER_MARKET_AND_ERROR_CLASS_NOT_CONFIRMATORY",
                "known_at_t": {k: example[k] for k in (
                    "episode_id", "asset_id", "market", "cutoff_at", "probability_up", "exposure",
                    "r63_known_at_t", "r252_known_at_t", "annual_volatility_known_at_t",
                    "input_path", "input_sha256", "prediction_path", "prediction_sha256")},
                "known_at_t_price_evidence": evidence[example["episode_id"]],
                "known_only_after_t": {k: example[k] for k in (
                    "classification", "no_trade_class", "net_return", "actual_scenario", "entry_date", "exit_date",
                    "max_adverse_excursion_gross", "max_favorable_excursion_gross", "label_path", "label_sha256")},
                "cause_status": "UNIDENTIFIED_CAUSE_CREDIT_VALUATION_EXPECTATIONS_NOT_OBSERVED_AT_T",
            })
    return examples


def percent(value):
    return "—" if value is None else f"{100*value:.2f}%"


def markdown(result):
    lines = [
        "# Phase 2：错误分类与不能识别的遗漏变量", "",
        "结论：**NO EVIDENCE OF GENERIC TIMING EDGE** 仍是当前固定规则的研究状态；本分类没有修复规则、改写预测或识别出错误的实际原因。原282个成熟12m标签与扩展374个标签分别报告。它们是历史遮蔽重构，不能称真正前瞻盲测。", "",
        "## 分类口径", "",
        "TP/FP使用已锁 p(up)>0.5，TN/FN使用p(up)<0.5；上涨事件为假设费用后的本币标签>0，非上涨为≤0。p=0.5单列ABSTAIN。方向预测与决策分开：负趋势给p=0.4且WAIT；混合趋势给p=0.5且WAIT，所以四分类与NO-TRADE分类可以重叠，不能相加当总案例数。", "",
        "Correct No-Trade / Missed Opportunity只能评估为**outcome proxy**：WAIT且未来不超过锁定Bull band / WAIT且未来超过Bull band。每个band在Stage A按过去波动与固定持有期锁定，没有事后改阈值。这不证明等待在T时具有最高Expected Value，也不证明后来大涨曾是可识别的高赔率机会。", "",
        "期限是5/21/63/126/252/504个观察交易时段，12m是原规则主要期限，其他五个是次要诊断。指数为不可直接交易的PRICE_ONLY本币标签，ETF为供应商公司行动重构总回报；50bp为冻结假设，MAE/MFE为gross路径。跨币种标签均值不是组合收益或CAGR。", "",
        "## 原282与扩展374", "",
        "|集合 / 期限|成熟N|TP|FP|TN|FN|Abstain|正确WAIT proxy|错过Bull proxy|", "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cohort, title in (("original_282", "原5批"), ("expanded_374", "全部8批")):
        for h in HORIZONS:
            s = result["summaries"][cohort][h]
            c, w = s["classification_counts"], s["wait_outcome_proxy_counts"]
            lines.append(f"|{title} / {h}{'（primary）' if h == '12m' else ''}|{s['n_mature']}|{c['TRUE_POSITIVE']}|{c['FALSE_POSITIVE']}|{c['TRUE_NEGATIVE']}|{c['FALSE_NEGATIVE']}|{c['ABSTAIN']}|{w.get('CORRECT_NO_TRADE_PROXY', 0)}|{w.get('MISSED_OPPORTUNITY_PROXY', 0)}|")
    primary = result["summaries"]["expanded_374"]["12m"]
    lines += ["", f"扩展主要期限共享{primary['date_cluster_count']}个日期簇、{primary['year_cluster_count']}个日历年份，跨资产同日相关且持有期重叠，独立N未知。430个选择行中53行不足历史，3行12m未成熟；保持UNSCORED而非补零，不再重复Historical Replay。", "",
              "## 概率与决策的错误不同", "", "|集合|锁定p(up)|N|后来上涨比例|未来净标签均值|", "|---|---:|---:|---:|---:|"]
    for cohort, title in (("original_282", "原282"), ("expanded_374", "扩展374")):
        for c in result["summaries"][cohort]["12m"]["calibration"]:
            lines.append(f"|{title}|{c['probability']:.1f}|{c['n']}|{percent(c['actual_up_fraction'])}|{percent(c['mean_net_label'])}|")
    lines += ["", "这些比例是相关样本的描述性校准，没有新增独立校准资格。TP可能仅小幅盈利并经历很大MAE；TN也可能只是成本后微亏。是否值得下注必须另比较赔率、左尾与真实现金/短债机会成本。ABSTAIN错过Bull可以提示代价，但不能事后把0.5改成看涨。", "",
              "## 缺失变量：错误与正确案例都缺，不能当错误解释", "", "|锁定T时字段|FP+FN缺失 / N|TP+TN缺失 / N|Abstain缺失 / N|", "|---|---:|---:|---:|"]
    missing = result["missing_comparison"]["expanded_374"]
    for c in CONTEXT:
        groups = [missing[k] for k in ("ERROR_FP_FN", "CORRECT_TP_TN", "ABSTAIN")]
        cells = [f"{g['missing_context'][c]['n_missing']}/{g['n']} ({percent(g['missing_context'][c]['fraction_missing'])})" for g in groups]
        lines.append("|"+c+"|"+"|".join(cells)+"|")
    lines += ["", "Valuation、Earnings、Credit、Liquidity、Breadth与其他字段普遍缺失，故**缺失频率不是鉴别错误的变量**。尤其不能因为错误组100%缺信用就声称100%错误由信用造成：正确组同样缺。Rates/Inflation/Policy的可见性差异主要来自US 2016–2023官方公告覆盖与市场构成；未控制覆盖差异，不能转为因果结论。", "",
              "表中缺失仅指已锁context_state字段，没有事后用文本补填Macro、Industry或Capital Actions。行业ETF的mandate仍已知，分红/拆股仍用于价格回报口径；字段缺失不表示行业名称未知或公司行动未处理。KNOWN_AT_T表示过去公告确实已公开，不能自动等同于T时当前状态：例如2024年输入中的2023年公告已陈旧。机器输出保留各字段最近观测距T的天数，不能用旧值或可见性本身代替regime识别。", "",
              "ROIC、FCF、margin、资产负债表、盈利修正、库存、供给、CapEx、长期合同、insider、持仓/crowding、市场预期和policy implementation没有独立T时字段。本分析只登记DATA_REQUIRED，不能把它们记为已发生的遗漏解释。没有从数据得到‘估值太高导致FP’、‘强制卖出导致FN’等频次。", "",
              "## 已观察的失败结构", "", "|主要期限类别|N|T时63时段回报均值|T时252时段回报均值|T时年化波动均值|未来净标签均值|gross MAE均值|", "|---|---:|---:|---:|---:|---:|---:|"]
    for c, s in result["feature_diagnostics"].items():
        lines.append(f"|{c}|{s['n']}|{percent(s['mean_r63'])}|{percent(s['mean_r252'])}|{percent(s['mean_past_annual_volatility'])}|{percent(s['mean_net_label'])}|{percent(s['mean_gross_mae'])}|")
    lines += ["", "FP表明两段正趋势不能作为完整的风险过滤器；FN表明两段负趋势不排除后来上涨。正/负趋势由规则定义，均值差属于类别定义和结果分组，不是新发现的预测因素。波动是已观测字段，但这里按错误标签分组的均值只用于诊断；没有据此寻找或调整一个能‘救回’规则的波动阈值。", "",
              "## 六个可追溯反例", "",
              "事后固定选择US/HK/JP各一个净跌幅最大的FP和一个净涨幅最大的FN，只用于审计严重错误。不是新增独立样本，不能用这些极端案例证明一般规律。T时均为原价格来源重构而非原始供应商vintage。", ""]
    for example in result["audit_examples"]:
        a, z = example["known_at_t"], example["known_only_after_t"]
        lines += [f"### {a['episode_id']} / {a['asset_id']} / {z['classification']}", "",
                  f"**KNOWN_AT_T**：T={a['cutoff_at']}；r63={percent(a['r63_known_at_t'])}，r252={percent(a['r252_known_at_t'])}，过去年化波动={percent(a['annual_volatility_known_at_t'])}；已锁p(up)={a['probability_up']:.1f}，exposure={a['exposure']}。",
                  f"原判断：[prediction]({a['prediction_path']})；T时输入：[input]({a['input_path']})；input SHA256 `{a['input_sha256']}`。", "",
                  "|T时证据record_id|Observation date|available_at|Source SHA256|", "|---|---|---|---|"]
        for e in example["known_at_t_price_evidence"]:
            lines.append(f"|{e['record_id']}|{e['date']}|{e['available_at']}|`{e['source_sha256']}`|")
        lines += ["", f"**KNOWN_ONLY_AFTER_T**：{z['entry_date']}→{z['exit_date']}，12m净标签{percent(z['net_return'])}，gross MAE{percent(z['max_adverse_excursion_gross'])}，gross MFE{percent(z['max_favorable_excursion_gross'])}；scenario={z['actual_scenario']}；WAIT分类={z['no_trade_class'] or '不适用'}。",
                  f"未来标签：[label]({z['label_path']})；label SHA256 `{z['label_sha256']}`。",
                  "原因保持UNIDENTIFIED_CAUSE：没有T时估值、盈利预期或信用状态，不能填入模型记忆中的危机、产业故事或后来的政策名称。", ""]
    lines += ["## 最便宜的下一步", "",
              "为已经注册的条件问题建立少量真实发布时间证据，优先一个可区分负趋势延续与反转的信用变量，或一个可以分开盈利兑现与预期过满的估值/预期变量。现有错误案例只能作探索；定义、阈值、样本与失败条件必须在新独立标签前冻结。先证明变量增量信息，再讨论最小2–3条件组合。", "",
              "机器可核验输出：[summary](research/phase2/error_taxonomy.summary.v001.json)、[逐episode六期限CSV](research/phase2/error_taxonomy.rows.v001.csv)、[六反例与来源](research/phase2/error_taxonomy.examples.v001.json)。运行 `python3 scripts/phase2_error_taxonomy.py` 只读取已锁A和已揭晓B；核验原input/prediction/lock/selection/preregistration/source bundle/实现哈希以及每个T时证据的available_at。未更改旧规则与文件。"]
    return "\n".join(lines) + "\n"


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == data, f"append-only output differs: {path}"
    else:
        with path.open("xb") as stream:
            stream.write(data)


def main():
    rows, provenance, batch_counts, evidence = audit_rows()
    original = [r for r in rows if r["batch"] in BATCHES[:5]]
    summaries = {"original_282": summarize(original), "expanded_374": summarize(rows)}
    assert summaries["original_282"]["12m"]["n_mature"] == 282
    assert summaries["expanded_374"]["12m"]["n_mature"] == 374
    result = {
        "analysis_status": "POST_REVEAL_ERROR_AUDIT_NOT_NEW_CONFIRMATORY_TEST",
        "rule_sha256": RULE_HASH, "primary_horizon": "12m", "no_parameter_search": True,
        "hash_and_cutoff_assertions": "PASS", "independent_sample_size": "UNKNOWN_DEPENDENT_OVERLAPPING_EPISODES",
        "causal_attribution_status": "UNIDENTIFIED", "wait_scoring": "FROZEN_BULL_BAND_OUTCOME_PROXY_NOT_EX_ANTE_EXPECTED_VALUE",
        "batch_counts": batch_counts, "provenance": provenance, "summaries": summaries,
        "missing_comparison": {"original_282": missing_comparison(original), "expanded_374": missing_comparison(rows)},
        "feature_diagnostics": feature_diagnostics(rows), "audit_examples": select_audit_examples(rows, evidence),
    }
    save(ROOT / "research/phase2/error_taxonomy.summary.v001.json", payload(result))
    save(ROOT / "research/phase2/error_taxonomy.examples.v001.json", payload(result["audit_examples"]))
    fields = list(rows[0])
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, dict) else v for k, v in row.items()})
    save(ROOT / "research/phase2/error_taxonomy.rows.v001.csv", buffer.getvalue().encode("utf-8"))
    save(ROOT / "ERROR_TAXONOMY.md", markdown(result).encode("utf-8"))
    print(json.dumps({"status": "PASS", "12m_original": summaries["original_282"]["12m"],
                      "12m_expanded": summaries["expanded_374"]["12m"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
