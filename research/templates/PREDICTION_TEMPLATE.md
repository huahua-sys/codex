# 预测与概率校准模板

`TEMPLATE_ONLY`；不是真实预测。概率单位为 0–1，实际实例必须先定义可评分事件与 horizon，再锁定宽区间。`null` 表示未运行。缺失或未成熟结果不评分，不当作零收益或事件失败。

## 事前锁定记录

```json
{
  "record_type": "prediction_ex_ante",
  "status": "TEMPLATE_ONLY",
  "prediction_id": null,
  "episode_id": null,
  "round_id": null,
  "hypothesis_id": null,
  "research_stage": null,
  "replay_type": null,
  "asset_id": null,
  "market": null,
  "created_at": null,
  "cutoff_at": null,
  "cutoff_timezone": null,
  "horizon": null,
  "horizon_alignment_rule": null,
  "event_definition": null,
  "return_basis": null,
  "benchmark_id": null,
  "event_threshold": null,
  "direction": null,
  "probability_range": {"lower": null, "upper": null},
  "scoring_probability_rule": null,
  "scoring_probability": null,
  "expected_return_range": {"lower": null, "upper": null},
  "scenario_payoffs": [],
  "main_reason": null,
  "evidence_record_ids": [],
  "price_in_assessment": null,
  "kill_conditions": [],
  "decision": null,
  "execution_rule": null,
  "next_review_at": null,
  "cost_model_id": null,
  "cash_alternative_id": null,
  "pit_status": null,
  "model_memory_contamination": null,
  "input_manifest_sha256": null,
  "preregistration_sha256": null,
  "lock_path": null
}
```

`NO-TRADE / WAIT` 可以与独立方向预测并存，动作的现金/短债机会成本和事件预测分别评价。若用 Brier score，代表概率方法与分箱预登记；区间中点不是更精确的自信。不能在揭晓后调整概率或更换事件定义。

`prediction_sha256`、`locked_at`、操作者与见证保存在独立锁定记录，引用已经冻结的预测文件；不把文件自身哈希写入它自己。

## 独立事后评分记录

```json
{
  "record_type": "prediction_evaluation",
  "status": "TEMPLATE_ONLY",
  "prediction_id": null,
  "prediction_sha256": null,
  "lock_sha256": null,
  "evaluator_version": null,
  "revealed_at": null,
  "horizon_maturity": null,
  "actual_outcome": null,
  "actual_event": null,
  "gross_total_return": null,
  "net_total_return": null,
  "benchmark_total_return": null,
  "net_excess_return": null,
  "cash_alternative_return": null,
  "decision_opportunity_cost": null,
  "max_drawdown": null,
  "brier_score": null,
  "calibration_result": null,
  "exclusion_reason": null,
  "source_manifest_sha256": null
}
```

填写 `calibration_result` 需要足够独立预测和成熟标签；单次命中不等于概率校准。按日期/资产簇处理相关样本，记录覆盖、删失、污染与多个 horizon 的重复预测，避免夸大样本数。已锁版本只追加修正；修正不改原始评分基线。
