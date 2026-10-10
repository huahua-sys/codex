# 不合格 pilot：只保留，不计入结果

2026-10-08 UTC，独立 QA 在 `ROUND_002` 24 个和 `NIGHT_XTIME` 36 个已锁 Stage A 输入发现完整 canonical metadata 被复制入事前输入，含未来覆盖日期、全历史数量及供应商未来错误行。规则不使用这些字段，但违反输入严格隔离要求。**两批 v001 均 INVALID_INPUT_METADATA_LEAK**，未揭晓 Stage B，不计为完成 replay、投资证据或校准样本。

保留全部原输入、预测、外置锁，不修改。工程失败不是市场假设被证伪。修复只在行政导入器采用 metadata allowlist；冻结核心 rule 与概率完全不变。新批次 `ROUND_002_V002` / `NIGHT_XTIME_V002` 采用相同资产、固定日期和原设计哈希。修复发生在任何未来收益揭晓之前。价格的原始 source URL / hash 是追溯信息，不是当时预测变量；today-retrieved 历史序列仍不是原始 vintage。

V002 独立复核发现 `filter_audit.excluded_context_reason_counts` 仍暴露未来公告数量。两批 V002 同样保留为 INVALID_INPUT_METADATA_LEAK；未揭晓收益。V003 移除被拒绝记录的数量，只保留T前样本数；这是最终准入版本。V001/V002共120个pilot锁不能计入真实已执行样本数。所有修复在任何收益揭晓前完成。
