#!/usr/bin/env python3
"""Render append-only episode reviews from locked A and already-revealed B.

This script never opens an administrative price bundle. It verifies the batch
lock sentinel before opening labels, and only transforms existing artifacts;
it neither changes predictions nor infers historical causal stories.
"""
import argparse
import json
import math
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lab.schema import CONTEXT_CATEGORIES, HORIZONS, json_bytes, read_json, sha256

RENDERER_VERSION = "episode-review-v002"


def percent(value):
    if value is None:
        return "N/A"
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("invalid numeric report field")
    return f"{value * 100:.2f}%"


def number(value):
    if value is None:
        return "N/A"
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("invalid numeric report field")
    return f"{value:.4f}"


def cell(value):
    if value is None:
        return "缺失；未填补"
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
    return value.replace("|", "\\|").replace("\n", "<br>")


def link(path, report_dir, label):
    target = Path(os.path.relpath(path, report_dir)).as_posix()
    return f"[{label}]({target})"


def context_value(state):
    value = state.get("value")
    if isinstance(value, dict):
        # Preserve parsed facts, while leaving the long original text in the
        # immutable A artifact linked at the top of every report.
        omitted = [k for k, v in value.items() if isinstance(v, str) and (len(v) > 400 or k.endswith("_evidence"))]
        compact = {k: v for k, v in value.items() if k not in omitted}
        summary = cell(compact) if compact else "原始发布文本见锁定 A"
        if omitted:
            summary += "; 原文/引文字段保留于 A：" + cell(", ".join(omitted))
        return summary
    return cell(value)


def direction_text(row):
    if row.get("status") != "REVEALED":
        return "未评分"
    if row.get("direction_correct") is None:
        return "ABSTAIN；未给单方向判断"
    return "方向正确；机制未识别" if row["direction_correct"] else "方向错误；机制未识别"


def diagnostics(prediction, evaluation):
    """Mechanical outcome facts, never causal attribution."""
    rows = [(h, x) for h, x in evaluation.get("horizons", {}).items() if x.get("status") == "REVEALED"]
    tags = []
    for horizon, row in rows:
        if row.get("false_negative_missed_winner"):
            tags.append((horizon, "MISSED_BULL_WHILE_WAITING", "WAIT，随后达到预登记 Bull 情景；这只是事后标签。"))
        if row.get("failed_long_signal"):
            tags.append((horizon, "LONG_DID_NOT_REACH_BULL_SCENARIO", "LONG，随后未达到 Bull；不必然代表净收益为负。"))
        if prediction.get("exposure") == 1 and row["net_return"] <= 0:
            tags.append((horizon, "NONPOSITIVE_NET_OUTCOME_AFTER_LONG_SIGNAL", "原 LONG 信号未取得正净收益；尚不识别原因。"))
        if prediction.get("exposure") == 0 and row["net_return"] < 0:
            tags.append((horizon, "WAIT_AVOIDED_ASSET_LOSS_VS_ZERO_CASH_ASSUMPTION", "WAIT 相对该资产避免亏损；0% 现金是假设。"))
        if row["gross_return"] > 0 and row["net_return"] <= 0:
            tags.append((horizon, "COST_MODEL_FLIPS_SIGN", "毛收益为正、假定费用后净收益非正；费用模型可识别。"))
    return tags


def render_episode(prediction, evaluation, lock, paths, report_dir, batch_id):
    eid = prediction["episode_id"]
    out = [f"# {eid} — 历史遮蔽复盘", "", f"批次 `{batch_id}`；资产 `{prediction['asset_id']}` / `{prediction['market']}`；Cutoff `{prediction['cutoff_at']}`。", "", "本报告在 Stage B 揭晓后生成，原 Stage A 未修改。它是冻结规则的历史重建，不是当年真实生成的预测；模型历史先验、今日供应商修订与逻辑隔离限制仍存在。", "", "## 原始锁定与信息边界", "", f"- 原始 A：{link(paths['prediction'], report_dir, '预测 JSON')} / {link(paths['prediction_md'], report_dir, '事前判断 Markdown')}。", f"- 外部锁：{link(paths['lock'], report_dir, '锁定记录')}；锁定时间 `{lock['locked_at']}`。", f"- A SHA-256：`{lock['prediction_sha256']}`。", f"- 输入 SHA-256：`{lock['input_sha256']}`；标签：{link(paths['label'], report_dir, 'Stage B JSON')}，SHA-256 `{sha256(paths['label'])}`。", f"- 抽样 SHA-256：`{lock['selection_sha256']}`；预登记 SHA-256：`{lock['preregistration_sha256']}`。", "- 哈希用于核对内容；它不证明可信历史时间戳、没有历史记忆或真正未知未来。", "", "## KNOWN_AT_T：原判断与已知事实", "", f"规则 `{prediction['rule_id']}`；决策 `{prediction['decision']}`；方向 `{prediction.get('direction')}`；置信度 `{prediction['confidence']}`。规则未拟合，未作参数搜索。", "", "|字段|T 时值|证据记录|", "|---|---|---|"]
    for name, key in (("63 交易时段历史回报", "r63"), ("252 交易时段历史回报", "r252"), ("252 时段年化波动", "annual_volatility_252")):
        out.append(f"|{name}|{percent(prediction.get('features', {}).get(key))}|{cell(prediction.get('features', {}).get('evidence_record_ids', []))}|")
    if not prediction.get("horizons"):
        out += ["", f"**本案例未形成有效预测。** 原 A 状态 `{prediction['status']}`，历史样本不足；`WAIT` 是数据不足时的占位状态。它不参加方向、概率或投资收益评分，不计为已完成 Historical Replay。保留本报告用于记录缺失与抽样覆盖，不能把缺失当作零收益。"]
    out += ["", "背景字段只重述 A。`DATA_REQUIRED` 表示没有可靠观测，不表示环境中性或信号为零。完整官方发布原文仍保存在上面的原始 A JSON。", "", "|背景字段|状态|当时信息|证据记录|", "|---|---|---|---|"]
    categories = list(CONTEXT_CATEGORIES) + ["Trend"]
    categories += sorted(set(prediction.get("context_state", {})) - set(categories))
    for cat in categories:
        state = prediction.get("context_state", {}).get(cat, {"value": None, "status": "DATA_REQUIRED", "evidence_record_ids": []})
        out.append(f"|{cat}|{cell(state.get('status'))}|{context_value(state)}|{cell(state.get('evidence_record_ids', []))}|")
    out += ["", f"历史财富链实际使用 {len(prediction.get('features', {}).get('actions_used', []))} 条已知公司行动记录，详见 A 的 `features.actions_used`。背景 `Capital Actions` 缺失不等于财富链没有公司行动。", "", "正面证据：", ""]
    out += [f"- `{r['type']}`：{r['statement']}；证据 {', '.join(r.get('evidence_record_ids', [])) or '无'}。" for r in prediction.get("positive_evidence", [])]
    out += ["", "反面证据与限制（限制不是反向事实）：", ""]
    out += [f"- `{r['type']}`：{r['statement']}；证据 {', '.join(r.get('evidence_record_ids', [])) or '无'}。" for r in prediction.get("negative_evidence", [])]
    out += ["", f"Price-In：{prediction.get('price_in_assessment', 'UNKNOWN')}。", "", f"最大未知：{prediction.get('biggest_unknown', 'DATA_REQUIRED')}。", "", "Kill Thesis（原样引用，未以未来结果更改）：", ""]
    out += [f"- {s}" for s in prediction.get("kill_thesis", [])]
    out += ["", f"执行状态 `{prediction.get('kill_thesis_execution', 'UNRESOLVED')}`；本轮固定持有标签不能回答动态卖出是否改善结果。", "", "## 原始概率判断", "", "|期限|方向|上涨概率区间 / 固定计分值|Bear / Base / Bull 概率区间|模型 EV|", "|---|---|---|---|---|"]
    for h in HORIZONS:
        row = prediction.get("horizons", {}).get(h)
        if not row:
            out.append(f"|{h}|未形成预测|N/A|N/A|N/A|")
            continue
        probs = "; ".join(f"{s['scenario']} {percent(s['probability_range'][0])}–{percent(s['probability_range'][1])}（计分 {percent(s['scoring_probability'])}）" for s in row["scenarios"])
        out.append(f"|{h}|{row['direction']}|{percent(row['p_up_range'][0])}–{percent(row['p_up_range'][1])} / {percent(row['p_up_scoring_probability'])}|{probs}|{percent(row['model_expected_value'])}|")
    out += ["", "模型 EV 来自未校准的情景回报假设，不是估计出的预期收益。Bear / Base / Bull 与上涨事件是两个评分定义；Base 不是收益为零。", "", "## KNOWN_ONLY_AFTER_T：Stage B 标签", "", f"标签状态 `{evaluation['status']}`；揭晓时间 `{evaluation.get('revealed_at', 'N/A')}`。主要期限固定为 12m；其余为次要描述，不能事后挑最优期限。", "", "|期限 / 完整交易时段|入场→退出|毛收益|净收益|MAE|MFE|收盘近似最大回撤|实际情景|方向评分|", "|---|---|---|---|---|---|---|---|---|"]
    for h, n in HORIZONS.items():
        row = evaluation.get("horizons", {}).get(h, {"status": "UNRESOLVED_DATA"})
        if row["status"] != "REVEALED":
            out.append(f"|{h} / {n}|{row['status']}|N/A|N/A|N/A|N/A|N/A|未评分|未评分|")
            continue
        out.append(f"|{h} / {n}|{row['entry_date']}→{row['exit_date']}|{percent(row['gross_return'])}|{percent(row['net_return'])}|{percent(row['max_adverse_excursion'])}|{percent(row['max_favorable_excursion'])}|{percent(row['max_drawdown'])}|{row['actual_scenario']}|{direction_text(row)}|")
    out += ["", "MAE / MFE 是毛财富的日频 OHLC 近似，退出日只取退出开盘；最大回撤基于收盘及入/出场开盘，不能声称重建盘中路径。期限使用 5 / 21 / 63 / 126 / 252 / 504 个完整时段，并非精确日历月。", "", "## 决策、校准与赔率评分", "", "|期限|Brier|情景 Brier|假设决策收益|相对同资产买入持有|上涨捕获率|下跌回避（收益差）|", "|---|---|---|---|---|---|---|"]
    for h in HORIZONS:
        row = evaluation.get("horizons", {}).get(h, {})
        if row.get("status") != "REVEALED":
            out.append(f"|{h}|N/A|N/A|N/A|N/A|N/A|N/A|")
            continue
        out.append(f"|{h}|{number(row['brier_score'])}|{number(row['scenario_brier_score'])}|{percent(row['hypothetical_decision_return'])}|{percent(row['hypothetical_excess_vs_buy_and_hold'])}|{number(row['upside_capture'])}|{percent(row['downside_avoidance'])}|")
    out += ["", "WAIT 在这份锁定模型中获得假设 0% 现金收益，尚未计真实短债机会成本。捕获率仅对同资产正净收益定义；下跌回避仅对负净收益定义，缺失值不是零。单案例不能判断概率是否校准，跨案例汇总还须处理同日市场依赖和期限重叠。", "", "## 判断是否正确，以及能够识别什么", ""]
    primary = evaluation.get("horizons", {}).get("12m", {})
    out.append(f"12m：{direction_text(primary)}。")
    if primary.get("status") == "REVEALED":
        out.append(f"原决策 `{prediction['decision']}`；12m 净标签 {percent(primary['net_return'])}，假设决策收益 {percent(primary['hypothetical_decision_return'])}。")
    out += ["", "无论方向对错，`UNRESOLVED_MECHANISM`：这组价格标签无法区分逻辑正确、风险溢价、偶然性或遗漏变量。趋势规则本身没有检验盈利、政策执行、供需或估值因果。", "", "由原规则与标签直接生成的诊断：", "", "|期限|机械标签|含义|", "|---|---|---|"]
    tags = diagnostics(prediction, evaluation)
    out += [f"|{h}|{tag}|{text}|" for h, tag, text in tags] or ["|全部|NO_ADDITIONAL_DIAGNOSTIC_TAG|没有额外机械标签；不等于机制成立。|"]
    out += ["", "尚待证据的错误类别（不作事后归因）：", "", "|可能类别|识别状态|", "|---|---|", "|missing variable|POSSIBLE_NOT_ESTABLISHED；背景缺失可确认，缺失变量是否决定结果不可确认。|", "|wrong causal story|NOT_TESTED；原匿名比值规则没有识别因果机制。|", "|price already reflected / valuation problem|NOT_TESTABLE；缺当时估值与一致预期。|", "|regime mismatch|POSSIBLE_NOT_IDENTIFIED；不按事后牛熊命名当时环境。|", "|liquidity shock / policy implementation failure|NOT_TESTABLE；缺资金流、融资约束与实际落地证据。|", "|false analogy|NOT_APPLICABLE_TO_RULE；规则没有按经典事件类比。|", "|capital cycle|NOT_TESTABLE；缺当时供给、库存与资本开支。|", "|randomness|UNRESOLVED；价格结果不能排除随机或不可预测冲击。|", "", "## 数据与适用范围", "", f"币种 `{prediction.get('currency')}`；回报口径 `{prediction.get('return_basis')}`；可交易性 `{prediction.get('tradability')}`；双边总成本假设 {prediction.get('cost_bps_roundtrip')} bp。FX 未评估，跨市场数字不能直接解释为同币种投资者收益。", "", "ETF 标签采用除息日现金权益在当日收盘再投资的经济总回报约定，不是支付日可执行交易路径。原生指数仅为价格标签及假设成本，不是可直接成交的基金总回报。", "", f"原始数据 vintage 状态：`{prediction.get('input_quality', {}).get('original_vintage_status', 'UNVERIFIED')}`。今日下载历史报价可能含后续更正；保守 session lag 是可观察性重建，不是归档供应商时间戳。当前存续资产样本没有退市证券与历史成分，不能外推至全部股票。", "", "本案例是证据记录，不构成投资原则；支持 / 反例需在完整抽样与独立扩样中共同评价。", ""]
    return "\n".join(out)


def write_or_verify(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError("existing report differs; append a version required: " + str(path))
    else:
        with path.open("xb") as output:
            output.write(payload)
    return sha256(path)


def render_batch(batch_dir, output_dir=None, batch_id=None):
    batch_dir = Path(batch_dir).resolve()
    batch_id = batch_id or batch_dir.name
    if not re.fullmatch(r"[A-Za-z0-9_-]+", batch_id):
        raise ValueError("unsafe batch ID")
    report_dir = Path(output_dir).resolve() if output_dir else ROOT / "research" / "episode_library" / batch_id
    run_dir = batch_dir / "run"
    # All A artifacts are checked before any future label is read.
    sentinel = read_json(run_dir / "all_locks.v001.json")
    if sentinel.get("status") != "ALL_EX_ANTE_LOCKED":
        raise ValueError("all A locks required")
    expected = sentinel["episode_ids"]
    if len(expected) != len(set(expected)):
        raise ValueError("duplicate episode IDs")
    checked = []
    for eid in expected:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", eid):
            raise ValueError("unsafe episode ID")
        paths = {"prediction": run_dir / "predictions" / (eid + ".v001.json"), "prediction_md": run_dir / "predictions" / (eid + ".v001.md"), "lock": run_dir / "locks" / (eid + ".v001.lock.json"), "label": run_dir / "labels" / (eid + ".v001.json")}
        lock = read_json(paths["lock"])
        prediction = read_json(paths["prediction"])
        if sentinel["lock_sha256"][eid] != sha256(paths["lock"]) or lock["prediction_sha256"] != sha256(paths["prediction"]) or lock["prediction_markdown_sha256"] != sha256(paths["prediction_md"]):
            raise ValueError("A lock integrity failure: " + eid)
        if prediction["episode_id"] != eid or lock["episode_id"] != eid:
            raise ValueError("A identity mismatch: " + eid)
        for key in ("selection_sha256", "preregistration_sha256", "input_manifest_sha256", "implementation_sha256"):
            if lock[key] != sentinel[key] or prediction[key] != lock[key]:
                raise ValueError("A batch provenance mismatch: " + eid)
        checked.append((prediction, lock, paths))
    # Evaluation summary exists only after evaluator produced the batch labels.
    summary_path = run_dir / "evaluation_summary.v001.json"
    summary = read_json(summary_path)
    if summary["episode_count"] != len(expected):
        raise ValueError("B summary does not cover locked batch")
    records = {}
    for prediction, lock, paths in checked:
        eid = prediction["episode_id"]
        evaluation = read_json(paths["label"])
        if evaluation.get("prediction_sha256") != lock["prediction_sha256"] or evaluation.get("lock_sha256") != sha256(paths["lock"]):
            raise ValueError("B does not reference locked A: " + eid)
        if evaluation.get("episode_id") != prediction["episode_id"]:
            raise ValueError("A/B episode identity mismatch: " + eid)
        insufficient = (prediction.get("status") == "INSUFFICIENT_HISTORY" and not prediction.get("horizons") and evaluation.get("status") == "UNRESOLVED_DATA" and evaluation.get("reason") == "exante_history_insufficient" and not evaluation.get("horizons"))
        for key in ("asset_id", "cutoff_at"):
            # The evaluator intentionally returns only episode_id when no A
            # forecast could be formed. Identity then comes from the locked A
            # referenced by both hashes, rather than fabricated B fields.
            if key not in evaluation and insufficient:
                continue
            if evaluation.get(key) != prediction[key]:
                raise ValueError("A/B identity mismatch: " + eid)
        text = render_episode(prediction, evaluation, lock, paths, report_dir, batch_id)
        target = report_dir / (eid + ".v001.md")
        records[eid] = {"report_path": str(target.relative_to(ROOT)) if target.is_relative_to(ROOT) else str(target), "report_sha256": write_or_verify(target, text.encode("utf-8")), "prediction_sha256": lock["prediction_sha256"], "lock_sha256": sha256(paths["lock"]), "label_sha256": sha256(paths["label"]), "asset_id": prediction["asset_id"], "market": prediction["market"], "cutoff_at": prediction["cutoff_at"], "outcome_status": evaluation["status"], "ex_ante_status": prediction["status"], "valid_forecast_formed": bool(prediction.get("horizons")), "mature_12m": evaluation.get("horizons", {}).get("12m", {}).get("status") == "REVEALED"}
    manifest = {"record_type": "episode_review_render_manifest", "renderer_version": RENDERER_VERSION, "batch_id": batch_id, "episode_count": len(records), "episode_count_means": "REPORT_RECORDS_INCLUDING_UNRESOLVED_NOT_COMPLETED_FORECASTS", "valid_forecast_count": sum(r["valid_forecast_formed"] for r in records.values()), "mature_12m_count": sum(r["mature_12m"] for r in records.values()), "insufficient_history_count": sum(r["ex_ante_status"] == "INSUFFICIENT_HISTORY" for r in records.values()), "date_cluster_count": summary.get("date_cluster_count"), "summary_sha256": sha256(summary_path), "all_locks_sha256": sha256(run_dir / "all_locks.v001.json"), "predictions_modified": False, "attribution": "UNRESOLVED_MECHANISM", "reports": records}
    write_or_verify(report_dir / "manifest.v001.json", json_bytes(manifest))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-dir", required=True, help="replay batch containing run/predictions, run/locks and run/labels")
    parser.add_argument("--batch-id")
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    manifest = render_batch(args.batch_dir, args.output_dir, args.batch_id)
    print(json.dumps({k: manifest[k] for k in ("batch_id", "episode_count", "valid_forecast_count", "mature_12m_count", "insufficient_history_count", "date_cluster_count", "predictions_modified", "attribution")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
