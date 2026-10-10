# 失败假设索引

> 当前Phase2状态：374成熟12m、377有效预测；没有通用/条件性优势证据，原15机制仍未测试。以下首段零资料/零执行等陈述为ROUND_001历史快照；本文件末尾是最新追加记录。
更新：2026-10-08 UTC。

已证伪假设：**0**。已完成实验：**0**。

资料缺失、未运行或未达到样本门槛不等于假设失败。本轮阻塞记录在 [ROUND_001_BLOCKED.md](research/replays/ROUND_001_BLOCKED.md)，不计入投资假设失败样本。

未来失败记录永久保存在 `research/failed_hypotheses/`，索引列为：ID、原假设 / 版本、实验 / 样本、失败类型、行业 / regime、成本影响、PIT / 后见偏差、是否值得重测、记录路径。原结果不得覆盖；重测使用新版本与新 holdout。

使用 [失败记录模板](research/templates/FAILED_HYPOTHESIS_TEMPLATE.md)。在尚无实验结果时，本文件不填任何失败故事。

## CYCLE_001_60_REPLAY — 失败保存

ENGINEERING_FAILURE：120个v001/v002 pilot锁输入有未来metadata/counts，未揭晓、全部保留且排除。新V003同rule重锁后QA通过；详见[记录](research/audit/PIT_METADATA_LEAK_PILOT_INVALID.md)。市场规则的失效边界另在night分析中保留，不泛化为所有趋势无效。

## CYCLE_002_CROSS_DOMAIN_282 — 失败保存

ENGINEERING_FAILURE：120个v001/v002 pilot锁输入有未来metadata/counts，未揭晓、全部保留且排除。新V003同rule重锁后QA通过；详见[记录](research/audit/PIT_METADATA_LEAK_PILOT_INVALID.md)。市场规则的失效边界另在night分析中保留，不泛化为所有趋势无效。

## CYCLE_003_CALENDAR_EARLY_RECENT — 失败保存

ENGINEERING_FAILURE：120个v001/v002 pilot锁输入有未来metadata/counts，未揭晓、全部保留且排除。新V003同rule重锁后QA通过；详见[记录](research/audit/PIT_METADATA_LEAK_PILOT_INVALID.md)。市场规则的失效边界另在night分析中保留，不泛化为所有趋势无效。

## CYCLE_004_CASH_SELL_COMPLETE — 失败保存

ENGINEERING_FAILURE：120个v001/v002 pilot锁输入有未来metadata/counts，未揭晓、全部保留且排除。新V003同rule重锁后QA通过；详见[记录](research/audit/PIT_METADATA_LEAK_PILOT_INVALID.md)。市场规则的失效边界另在night分析中保留，不泛化为所有趋势无效。

## Phase2冻结失败

F-NIGHT-001：固定63/252组合及40/50/60先验未稳定增加主12m信息；八批均差于常数60%对照。F-NIGHT-002：weeklySPY/BIL未证明优于固定50/50及60/40/70/30；不能靠改费用/窗口/年份救活。仅记录NO EVIDENCE OF GENERIC TIMING EDGE，不证明所有趋势无效。

F-P2-C1：高通胀+年度加息久期组合FRAGILE，2023方向反例、2021大亏未触发；日期/阈值变动翻号并含发布时间边界。是否局部有效待新的独立数据，不调整旧门槛。Q-P2-C2 N1是证据不足、不是已证伪。随机日期placebo N0是数据不足、不是规则通过或失败。


## Phase3启动

原失败不撤销、原15候选未升级。新增单变量稳定性问题与信用原发布是预注册研究，不是策略救活或投资原则。新结果未揭晓，新增已验证原则0。


## Phase3失败、反例与未识别记录

FH-P3-001：大跌就是便宜/安全买入的叙事不成立为原则。US同季度差区间跨0且未来gross MDD更深；Treasury大跌后均值负，只有5 dates。局部反弹尚可描述，不知道估值/偿付/原预期，不能判断错杀机制真伪。

FH-P3-002：信用收紧/未收紧单一过滤器方向跨年代不稳定；预定H-P3-DD-CREDIT gate失败，交互未执行。记录NOT_RUN_GATE_FAILED，不当信用因果理论被证伪；不改规则/换起点。

FH-P3-003：正趋势提高收益均值/独立赔率未成立；同季度US股票12/24m差约−.74/−1.80pp且区间跨0。较浅回撤不等于配置以上alpha，原失败概率rule保持冻结。

FH-P3-004：相对高波动若作“必涨/普适”故事被负控限制：95个US高波动负12m，52个不高波动仍>30%12m；Treasury方向负、HK/DE/UK市场反例、早2000–09区间跨0。有限US横截面平均关联仍存活，不能写完全被推翻，也不能救活原任何策略。全部negative case index保存。

FH-P3-005：尚无法判断Underreaction/价值长期尺度/盈利revision增量/CapEx收益因果；属于DATA_REQUIRED或NOT_IDENTIFIED，不是实验失败收益，也不是被证实经济钥匙。
