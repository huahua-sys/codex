> 当前Phase3指令优先（2026-10-09）：按已锁SAMPLE_EXPANSION_PROTOCOL、design和新端点假设推进固定季度扩样。原282及所有旧A/B/锁不可改，失败择时不重跑；跨时间重构不能称未来OOS。先全特征锁，再development标签/统计锁，最后later holdout；记录RAW与有效样本边界。LIVE前瞻首次2026-10-30，尚未到时PENDING，不造预测。

# Investment Research Lab 的工作指引

本仓库的唯一研究任务依据用户 master prompt；本文件落实该要求，用户后续明确指令优先。先读 `RESEARCH_CONSTITUTION.md`、`DATA_INVENTORY.md`、`PROJECT_AUDIT.md` 和 `research/status/LATEST.md`，再查看 `HYPOTHESIS_REGISTRY.md`、`CURRENT_FRAMEWORK.json` 及相关协议，避免重复试验和忘记失败。

## 当前状态

2026-10-09：用户新 Phase2 Conditional Edge 指令优先。冻结所有已失败的简单趋势/择时参数及结果，不再优化或重新跑旧Historical Replay。先按错误分类与经济机制检验少量2–3条件；旧282与扩展374成熟12m分别报告。新增基准60/40与70/30、条件性检验、placebo和扰动只追加，新结果不得救活旧规则。完成8份Phase2报告、永久记忆、夜间总结后导出 `/workspace/outputs/Investment_Research_Lab_Phase2.zip`；原指令副本在sources。

最新任务为 `AUTONOMOUS NIGHT RESEARCH MODE`，总研究轮次 ROUND_002。用户已授权网络公开来源与连续循环：完成原24例后继续反例、相似案例、跨行业/市场/时期、Price-In、卖出和WAIT研究；不要按旧首轮停止边界结束。每一主要cycle立即更新永久记忆，最终保存 `NIGHT_RESEARCH_REPORT.md`。最多每次新增3条候选，保留旧15条出处；无独立证据不得晋升。自然停止须记录平台限制、DATA EXHAUSTED、重要数据阻塞、经多轮仍 NO ROBUST PATTERN YET 或存活候选及未完成验证。

首轮历史状态（保留供追溯）：

2026-10-08 UTC：首轮 `ROUND_001` 为 `BLOCKED_DATA_REQUIRED`。只有任务文本，未完成真实历史 replay；预测、结果、校准及已验证规律均不存在。候选仅为待检验研究方向，不是从已完成复盘发现的规律。

## 执行规则

1. 先核验现有资料；不联网、不新增外部数据，除非用户后续扩展授权。目录创建和协议文档不能称为历史实证完成。
2. 使用 `research/protocols/DATA_CONTRACT.md` 建立来源、发布时间、版本及可交易性证据。未知 `available_at` 不能用 mtime、财期末、下载日期或未经验证的日期替代。
3. 使用 `research/protocols/HISTORICAL_REPLAY.md`；先锁定抽样、T、特征和判断，再揭晓未来。明确模型记忆风险；不得把遮蔽历史样本称作真正盲测。
4. 不从赢家榜、危机榜或已知结局选择确认样本；保留普通资产、无信号资产、失败、退市与不可判定记录。探索案例可以标注事后发现，但不能计入独立检验。
5. 模板中的 `null`、空数组和待填字段不是事实。缺数据时禁止填入真实资产的伪概率、伪收益或“示例”支持案例。
6. 已锁判断和失败记录逻辑只追加；新版本引用旧哈希，并登记理由。文件哈希不证明真实盲性，不证明可信历史时间戳。
7. 最快计划决策周期一周；截止之后的下一可交易执行时点、总回报、基准、成本、FX、退市、停牌和公司行动必须明确。
8. 治理纪律不等于投资结论；不能把未经验证的行业框架、新闻优先级或候选机制写入 `validated_principles`。
9. 没有数据不推荐证券、不宣布规律成立。允许 `NO-TRADE / WAIT`，允许 `INSUFFICIENT EVIDENCE`。
10. 用中文保存解释，保留状态代码。优先简单可证伪实验；禁用参数暴力搜索。完成一次研究后更新五个记忆文件并停止本轮。

## 模板与职责

`research/templates/` 保存 episode、prediction、preregistration 与 failed hypothesis 模板。`research/episode_library/ROUND_001_PLAN.md` 是计划，`research/replays/ROUND_001_BLOCKED.md` 是执行阻塞记录；两者均不可登记为已完成案例或预测。没有实证时 `EPISODE_INDEX.md`、`PREDICTION_LEDGER.md` 保持零执行记录。
