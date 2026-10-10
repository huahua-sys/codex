# 失败、局部失效或不可识别假设模板

`TEMPLATE_ONLY`；不是已经失败的实证。没有完成检验的假设应标阻塞/未检验，不能伪造失败案例。首次实例化后永久保留，不覆盖删除。

```json
{
  "record_type": "failed_hypothesis",
  "status": "TEMPLATE_ONLY",
  "failure_id": null,
  "hypothesis_id": null,
  "hypothesis_version": null,
  "experiment_ids": [],
  "recorded_at": null,
  "original_belief_and_economic_logic": null,
  "preregistration_paths": [],
  "input_manifest_sha256": [],
  "lock_paths": [],
  "test_method": null,
  "independent_sample_count": null,
  "market_industry_regime_coverage": null,
  "observed_results": null,
  "failure_class": null,
  "full_or_local_failure": null,
  "industries_where_failed": [],
  "regimes_where_failed": [],
  "evidence_against": [],
  "remaining_evidence_for": [],
  "transaction_cost_effect": null,
  "price_in_effect": null,
  "execution_failure": null,
  "hindsight_or_leakage": null,
  "model_memory_contamination": null,
  "survivorship_missingness_overlap_biases": null,
  "causal_identification_limit": null,
  "why_failure_not_merely_bad_luck": null,
  "what_was_learned": null,
  "whether_retest_is_justified": null,
  "specific_new_data_or_conditions_for_retest": null,
  "related_prior_failures_and_aliases": [],
  "downstream_principle_changes": [],
  "amendment_of": null,
  "prior_record_sha256": null
}
```

`failure_class` 可为经济机制未兑现、统计不稳定、跨期/市场/行业失败、成本吞噬、已计价、执行不可行、样本偏差、泄漏、无法识别或证据不足；数据缺失属于不可识别/阻塞，不能写成已证伪。保存原逻辑、全部结果和剩余适用边界，避免几年后改名重复失败。反证触发下调候选置信度；正式原则更改须留版本与理由。
