# 首轮研究状态

研究轮次：ROUND_001；日期：2026-10-08 UTC；框架版本：0.1.0。

总体状态：**BLOCKED_DATA_REQUIRED / INSUFFICIENT EVIDENCE**。第一轮在完成盘点、建档、方案和文件核验后停止。真实历史复盘尚未执行。

## What was studied? 研究了什么？

核查工作区和用户附件能否支持 point-in-time 历史研究。将主提示词落实为长期档案、来源登记、研究纪律、行业 / 决策框架、案例方案、假设与验证协议。

## What was learned? 学到了什么？

原工作区有 0 个普通文件；附件是 27,597 字节的研究指令，不含历史观测。当前资料不能产生任何市场有效性判断。生成的研究文件、模板及理论机制也不提供投资证据。

## What failed? 什么失败了？

真实首轮复盘未通过数据就绪门槛：没有 PIT 输入、证券池、执行价格或未来标签。没有实验被运行，因此没有假设被经验否定。该阻塞保存在 [ROUND_001_BLOCKED.md](../replays/ROUND_001_BLOCKED.md)，不计为失败投资假设。

## What remains uncertain? 哪些仍不确定？

市场、年份、数据版本、首次公开时间、可交易性、退市覆盖、成本、基准及现金机会成本均未提供。模型记忆历史结果的污染不能只靠隐藏文件解除；历史掩码回放不能自动视作真正盲测。

## What new candidate rules appeared? 新候选是什么？

建立了 **15 个待检验候选和 15 个轻量实验方案**，来源为 `MASTER_PROMPT_DERIVED_UNTESTED`。它们是提示词衍生研究设计，**不是从已完成复盘中发现的规律**。正式预登记、独立样本定义和实证检验均待数据到位。

见 [候选索引](../../CANDIDATE_PRINCIPLES.md)、[假设登记](../../HYPOTHESIS_REGISTRY.md)、[路线图及排序](../../RESEARCH_ROADMAP.md)。排序表示研究价值、资料负担、可证伪性、计算成本和过拟合风险的启发式判断，不表示成功概率。

## Which old rules weakened / strengthened? 哪些规则变弱或变强？

无。既有已验证原则为 0，没有独立证据支持任何晋升、强化或降级。治理纪律不计为市场规律。

## What is the next highest-value question? 下一步最有价值的问题？

**能否从一个连续样本区间取得可核验当时公开时间、历史版本和真实交易覆盖的最小数据包？** 先回答数据可用性，再选择排名靠前且字段满足的实验；不因排名而强行补齐不存在的数据。

## What data is missing? 缺少哪些数据？

首先需要历史证券池及退市信息、交易日历、价格 / 公司行动 / 总回报基准、现金 / 短债、费用和至少一种原始历史披露（含时间、时区及当时版本）。专项实验再增加历史一致预期、订单、库存、资金流或宏观 vintage 等字段。详见 [资料清单](../../DATA_INVENTORY.md) 与 [数据合同](../protocols/DATA_CONTRACT.md)。

## 完成边界与计数

| 项目 | 本轮数量 / 状态 |
|---|---|
| 初始观测数据文件 | 0 |
| 已执行真实 episode / 历史回放 | 0 |
| 已锁定 ex-ante 预测 | 0 |
| 已揭晓 / 计分结果 | 0 |
| 已完成统计实验 | 0 |
| 从复盘发现的候选 | 0 |
| 提示词衍生候选设计 | 15；DATA REQUIRED |
| 实验方案 | 15；正式预登记待定 |
| 已验证投资原则 | 0 |

审计与基础设施完成；案例体系已设计；历史盲测、基于复盘的发现和统计验证仍阻塞。没有产生收益、概率、命中率或校准成绩。

核验依据保存于 [ARTIFACT_VERIFICATION.json](../audit/ARTIFACT_VERIFICATION.json) 与 [独立复核记录](../audit/INDEPENDENT_REVIEW.md)。机器可读状态见 [CURRENT_FRAMEWORK.json](../../CURRENT_FRAMEWORK.json)。
