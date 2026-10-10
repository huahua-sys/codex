# 历史案例模板

模板状态 `TEMPLATE_ONLY`；不是已执行案例，不加入 `EPISODE_INDEX.md` 的已完成计数。所有 `null` 与空数组表示尚未填写，不能解释为无信号、零概率、零回报或已通过质量检查。真实案例须先通过数据契约。

## A. 事前文件（锁定后不可覆盖）

```json
{
  "record_type": "episode_ex_ante",
  "status": "TEMPLATE_ONLY",
  "episode_id": null,
  "round_id": null,
  "hypothesis_ids": [],
  "research_stage": null,
  "replay_type": null,
  "asset_id": null,
  "asset_name": null,
  "instrument_type": null,
  "market": null,
  "industry_at_cutoff": null,
  "start_date": null,
  "cutoff_at": null,
  "cutoff_timezone": null,
  "cutoff_utc": null,
  "calendar_id": null,
  "forward_horizons": [],
  "primary_horizon": null,
  "source_manifest_path": null,
  "source_manifest_sha256": null,
  "preregistration_path": null,
  "preregistration_sha256": null,
  "sample_selection_rule": null,
  "selection_probability": null,
  "pit_status": null,
  "pit_uncertainties": [],
  "model_memory_contamination": null,
  "memory_contamination_details": null,
  "analyst_label_access_before_lock": null,
  "separation_status": null,
  "known_at_cutoff": {
    "macro": null,
    "industry": null,
    "company": null,
    "valuation": null,
    "policy": null,
    "news": null,
    "capital_flow": null,
    "insider_institutional_actions": null,
    "trend": null,
    "sentiment": null,
    "positioning": null
  },
  "source_record_ids_by_claim": {},
  "bullish_signals": [],
  "bearish_signals": [],
  "ambiguous_signals": [],
  "missing_information": [],
  "ex_ante_thesis": null,
  "economic_mechanism": null,
  "regime_definition_and_evidence": null,
  "capital_cycle_and_shareholder_cash_bridge": null,
  "price_in_checks": null,
  "plausible_scenarios": [],
  "predicted_event_definition": null,
  "probability_range": {"lower": null, "upper": null},
  "expected_return_range": {"lower": null, "upper": null, "basis": null},
  "decision": null,
  "kill_conditions": [],
  "sell_framework": null,
  "wait_release_conditions": [],
  "next_review_at": null,
  "earliest_executable_at": null,
  "execution_rule": null,
  "benchmark_id": null,
  "cash_alternative_id": null,
  "cost_model_id": null,
  "reporting_currency": null,
  "closest_analogues_known_before_cutoff": [],
  "core_similarities": [],
  "important_differences": [],
  "lock_record_path": null
}
```

填写事实时逐条引用 `source_record_id` 及 `available_at`，不补历史常识。类比只用 T 时已发生的案例，避免未来类比变成特征。判断方向、概率、仓位或动作无法建立时保持未运行，不能先锁空字段再宣称预测。

锁定元数据另存 `locks/<episode_id>.v001.lock.json`，避免文件包含自己的哈希而形成循环：

```json
{
  "record_type": "episode_lock",
  "status": "TEMPLATE_ONLY",
  "episode_id": null,
  "ex_ante_path": null,
  "ex_ante_sha256": null,
  "input_manifest_sha256": null,
  "preregistration_sha256": null,
  "locked_at": null,
  "locked_by": null,
  "label_access_before_lock": null,
  "model_memory_contamination": null,
  "separation_status": null,
  "witness_or_timestamp_evidence": null
}
```

## B. 独立标签文件（锁定后由评估者填）

不要把此区与真实事前输入一同提供给研究者。实例化时另存 `labels/<episode_id>.v001.json`，以下仅为字段模板。

```json
{
  "record_type": "episode_labels",
  "status": "TEMPLATE_ONLY",
  "episode_id": null,
  "ex_ante_sha256": null,
  "lock_sha256": null,
  "revealed_at": null,
  "evaluator_version": null,
  "label_source_manifest_sha256": null,
  "executed_at": null,
  "execution_unavailable_reason": null,
  "horizon_outcomes": [],
  "primary_result_category": null,
  "additional_result_categories": [],
  "signal_present_at_cutoff": null,
  "mechanism_realized": null,
  "outcome": null,
  "review_path": null
}
```

`horizon_outcomes` 每项须含 horizon、终点/成熟状态、毛/净总回报、本币/报告币种、基准/现金回报、超额回报、成本、FX、回撤、公司行动/退市处理和数据缺失。六个标准 horizon 尚未成熟时各项 outcome 均为 `null`，状态 `PENDING_HORIZON`；资料不足则 `UNRESOLVED_DATA`。

## C. 复盘文件（不重写原判断）

- 实际发生什么？机制和价格分别引用未来来源。
- 原信号哪些具有区分能力，哪些可能为噪音？没有对照不能判有效。
- 缺什么？什么误导了判断？是否存在市场已计价、模型记忆、数据泄漏、成本或执行偏差？
- 判对且理由对 / 判对但理由错 / 判错但过程合理 / 判错且可识别错误 / 随机或无法归因。
- 当时类比的相似与差异哪些是核心条件？
- 可以推广到哪里、在哪些行业/市场/regime失效？需哪些独立样本？
- 新观察只能成为 `EXPLORATORY` 候选；没有验证不能进入正式投资哲学。

以上目前均未填写，模板没有研究结果。
