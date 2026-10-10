# 研究总账

> 当前Phase2状态：374成熟12m、377有效预测；没有通用/条件性优势证据，原15机制仍未测试。以下首段零资料/零执行等陈述为ROUND_001历史快照；本文件末尾是最新追加记录。
账目追加记录；更正以新记录引用旧 ID，不能删除失败或覆盖旧预测。

| 记录 ID | 日期 UTC | 范围 | 使用来源 | 已完成 | 未完成及原因 | 结果等级 |
|---|---|---|---|---|---|---|
| RL-001 | 2026-10-08 | ROUND_001；Phase 0–1；后续协议设计 | SRC-001 研究指令；AUD-001 工作区扫描 | 数据盘点、基础设施、案例与验证设计、15 个理论候选 | 真实复盘及统计验证未执行；无观测 / PIT 数据 | INSUFFICIENT EVIDENCE；BLOCKED_DATA_REQUIRED |

本轮新增的是档案和研究方案，非市场观察。不存在 ex-ante 预测、锁定文件、结果标签、收益、统计支持、校准结果或已验证原则。15 个候选来源为 `MASTER_PROMPT_DERIVED_UNTESTED`，不是 `REPLAY_DISCOVERED`。

档案层面的独立复核见 [INDEPENDENT_REVIEW.md](research/audit/INDEPENDENT_REVIEW.md)，完整性验收输出见 [ARTIFACT_VERIFICATION.json](research/audit/ARTIFACT_VERIFICATION.json)。文件验收不计入市场统计实验。

首轮执行边界：完成盘点、建档、设计及核验后停止。状态见 [LATEST.md](research/status/LATEST.md)，详细顺序见 [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md)。

## RL-002A — 2026-10-08 — 夜间研究启动

用户授权公开来源及连续循环。保留首轮记忆，锁定24例日历网格；引擎合成核验通过，真实输入尚在获取。原15设计未测试，尚未形成新投资结论。根环境HTTP已实测可用；旧子代理网络受限由root执行下载。该进度记录不是已完成Historical Replay。

## CYCLE_001_60_REPLAY — 2026-10-08T16:21:32.547848+00:00

更新时间 2026-10-08T16:21:32.547848+00:00；60 个选择行，60 个成熟12m价格标签，0 个不足资料行；20 个共享日期簇。固定规则、宽概率先验、费用与现金假设均未经校准。原15假设仍未测试。

状态 AUTONOMOUS_NIGHT_RESEARCH_RUNNING；全锁先于B，V003已独立QA。工程失败见PIT_METADATA_LEAK_PILOT_INVALID；未修改旧预测。证据：[checkpoint](research/checkpoints/CYCLE_001_60_REPLAY.json)。投资结论 NO ROBUST PATTERN YET；继续反例与现金研究。

## CYCLE_002_CROSS_DOMAIN_282 — 2026-10-08T16:21:59.203600+00:00

更新时间 2026-10-08T16:21:59.203600+00:00；330 个选择行，282 个成熟12m价格标签，48 个不足资料行；20 个共享日期簇。固定规则、宽概率先验、费用与现金假设均未经校准。原15假设仍未测试。

状态 AUTONOMOUS_NIGHT_RESEARCH_RUNNING；全锁先于B，V003已独立QA。工程失败见PIT_METADATA_LEAK_PILOT_INVALID；未修改旧预测。证据：[checkpoint](research/checkpoints/CYCLE_002_CROSS_DOMAIN_282.json)。投资结论 NO ROBUST PATTERN YET；继续反例与现金研究。

## CYCLE_003_CALENDAR_EARLY_RECENT — 2026-10-08T16:29:09.086967+00:00

更新时间 2026-10-08T16:29:09.086967+00:00；430 个选择行，374 个成熟12m价格标签，56 个不足资料行；43 个共享日期簇。固定规则、宽概率先验、费用与现金假设均未经校准。原15假设仍未测试。

状态 AUTONOMOUS_NIGHT_RESEARCH_RUNNING；全锁先于B，V003已独立QA。工程失败见PIT_METADATA_LEAK_PILOT_INVALID；未修改旧预测。证据：[checkpoint](research/checkpoints/CYCLE_003_CALENDAR_EARLY_RECENT.json)。投资结论 NO ROBUST PATTERN YET；继续反例与现金研究。

## CYCLE_004_CASH_SELL_COMPLETE — 2026-10-08T16:35:12.074800+00:00

更新时间 2026-10-08T16:35:12.074800+00:00；430 个选择行，377 条有效预测，374 个成熟12m价格标签，53 个不足历史行，3 个12m尚未成熟行；43 个共享日期簇、23 个日历年份。日期和期限重叠，独立N未知。固定规则、宽概率先验、费用与现金假设均未经校准。原15假设仍未测试。

状态 AUTONOMOUS_NIGHT_RESEARCH_RUNNING；全锁先于B，V003已独立QA。工程失败见PIT_METADATA_LEAK_PILOT_INVALID；未修改旧预测。证据：[checkpoint](research/checkpoints/CYCLE_004_CASH_SELL_COMPLETE.json)。投资结论 NO ROBUST PATTERN YET；继续反例与现金研究。

## RL-P2-FINAL — 2026-10-09T00:23:18.757120+00:00

复用原282与扩展374结果，未新增Historical Replay/概率预测。完成错误分类、2经济组合、固定配置残差、601placebo条目/9扰动、8报告与night总结。16原宏观档+2原SEC报告/8facts已核；金融与CSI/Chi指数不足保留。C1脆弱、C2N1、随机日期条件N0，未晋升原则。

更正CYCLE_003“56不足资料行”：实际53不足历史+3待成熟；原snapshot保留，CYCLE_004与本checkpoint已分开。

[最终checkpoint](research/checkpoints/PHASE2_FINAL.v001.json)。下一步需要小连续信用/财务/预期序列；没有宣称全球DATA EXHAUSTED。
