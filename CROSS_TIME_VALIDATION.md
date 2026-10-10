# 跨时期验证报告

## RAW OBSERVATIONS

开发选择格 2496；较晚计算holdout选择格 208。

## EFFECTIVE SAMPLE ASSESSMENT

较早年度与较晚年度也有全球共同regime及重叠收益，独立N未知。既有研究已读2003–2025若干起点及2002以后价格路径；2000–2015不是整体未见external OOS。

≤2023结果先保存并锁定，开发锁的全部SHA在holdout打开前核验。2024–2025只称COMPUTATIONAL_LATER_LABEL_HOLDOUT_WITH_PRIOR_PATH_EXPOSURE；不是严格未来OOS。没有看holdout后重新拟合、改阈值、改市场或择优期限。

## 固定年代：12m全资产组间日期等权差

|分区|年代|变量|组1 N|组0 N|组间差|95%区间|
|---|---|---|---:|---:|---:|---|
|development|2000-2009|H-P3-TREND|390|251|-2.83%|[-10.06%, 7.48%]|
|development|2000-2009|H-P3-DRAWDOWN|173|468|1.45%|[-13.13%, 9.00%]|
|development|2000-2009|H-P3-VOL|263|287|-3.12%|[-9.75%, 1.30%]|
|development|2000-2009|H-P3-CREDIT|165|168|-8.50%|[-28.38%, -3.19%]|
|development|2010-2019|H-P3-TREND|669|251|3.86%|[-0.01%, 7.65%]|
|development|2010-2019|H-P3-DRAWDOWN|57|863|-7.11%|[-12.38%, 0.72%]|
|development|2010-2019|H-P3-VOL|396|524|2.87%|[1.07%, 6.11%]|
|development|2010-2019|H-P3-CREDIT|153|527|1.37%|[-5.49%, 6.80%]|
|development|2020-2025|H-P3-TREND|218|150|-5.82%|不可推断（不足4块）|
|development|2020-2025|H-P3-DRAWDOWN|63|305|14.67%|不可推断（不足4块）|
|development|2020-2025|H-P3-VOL|201|167|7.85%|不可推断（不足4块）|
|development|2020-2025|H-P3-CREDIT|170|102|12.43%|不可推断（不足4块）|
|holdout|2000-2009|H-P3-TREND|0|0|UNKNOWN|不可推断（不足4块）|
|holdout|2000-2009|H-P3-DRAWDOWN|0|0|UNKNOWN|不可推断（不足4块）|
|holdout|2000-2009|H-P3-VOL|0|0|UNKNOWN|不可推断（不足4块）|
|holdout|2000-2009|H-P3-CREDIT|0|0|UNKNOWN|不可推断（不足4块）|
|holdout|2010-2019|H-P3-TREND|0|0|UNKNOWN|不可推断（不足4块）|
|holdout|2010-2019|H-P3-DRAWDOWN|0|0|UNKNOWN|不可推断（不足4块）|
|holdout|2010-2019|H-P3-VOL|0|0|UNKNOWN|不可推断（不足4块）|
|holdout|2010-2019|H-P3-CREDIT|0|0|UNKNOWN|不可推断（不足4块）|
|holdout|2020-2025|H-P3-TREND|135|23|-3.95%|不可推断（不足4块）|
|holdout|2020-2025|H-P3-DRAWDOWN|2|156|32.03%|不可推断（不足4块）|
|holdout|2020-2025|H-P3-VOL|79|79|12.43%|不可推断（不足4块）|
|holdout|2020-2025|H-P3-CREDIT|102|17|-0.94%|不可推断（不足4块）|

## 保留下来的旧结论

Phase2失败的63/252概率规则、每周SPY/BIL切换和两个宏观组合不在本实验重新运行；本研究不能把单变量某一组高收益解释为旧策略复活。估值、盈利修正、Price-In和资本周期缺连续PIT值，不能下时间尺度或增量信息结论。

价格趋势只是一种可见状态：即使某年代组间收益差为正，也必须与被动、同风险和信用/基本面匹配才能判断独立预测贡献。大跌后的高平均回报也可能是风险溢价、尾部反弹或幸存者偏差；MDD与失败案例不能省略。

## 下一步隔离

真正LIVE FORWARD自2026-10-09冻结后启动；首月末2026-10-30尚未来到，应为PENDING_DECISION。不为历史已见价格重新贴live标签，不填月末未发生的预测。

## 人工统计核验与完整分布（presentation v002）

### RAW OBSERVATIONS

开发变量比较1929主12m/1929次24m；后期158主12m/66次24m。后期大跌组主12m只有2、次24m只有1，信用24m无不收紧组。

### EFFECTIVE SAMPLE ASSESSMENT

开发结果及本文开发解释先封存；随后一次正式揭晓2024/25。后期只有1两年块，开发前瞻收益已跨到2024/25，旧研究也已接触路径，因此后期只能称计算隔离，不能称真正未来OOS或全新全球regime。

### 主12m市场反例：日期等权组间差

|分区|变量|CN|DE|EU|HK|JP|UK|US|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|development|H-P3-TREND|-5.82pp|-1.23pp|-10.02pp|-4.28pp|-0.56pp|-0.81pp|+0.10pp|
|development|H-P3-DRAWDOWN|-3.11pp|+8.01pp|+13.74pp|+3.72pp|-2.37pp|+13.26pp|+4.04pp|
|development|H-P3-VOL|-9.57pp|+3.56pp|+6.83pp|+1.10pp|-5.29pp|+0.84pp|+4.11pp|
|development|H-P3-CREDIT|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|+1.26pp|
|holdout|H-P3-TREND|+3.22pp|UNKNOWN|UNKNOWN|-12.09pp|-35.22pp|UNKNOWN|-1.28pp|
|holdout|H-P3-DRAWDOWN|UNKNOWN|UNKNOWN|UNKNOWN|+1.47pp|UNKNOWN|UNKNOWN|+58.36pp|
|holdout|H-P3-VOL|UNKNOWN|-15.75pp|+9.29pp|-12.09pp|UNKNOWN|+2.84pp|+23.06pp|
|holdout|H-P3-CREDIT|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|-0.94pp|

美国信用只进入US字段，其他市场UNKNOWN；US包含股票、国债、资源和现金混合工具，不等于股票单独效应。EU指STOXX50E，2008Q2之后feature才合格；DE为DAX performance指数，不能按普通price-only统一归因。

12m开发趋势差在US约+0.10pp，其余市场负；24m七市场均负。该描述不证明反向策略可执行，也不代表趋势从不含信息。

大跌12m开发年代方向+1.45/−7.11/+14.67pp，后期+32.03pp只是2条；24m开发年代+36.99/−11.34/+27.78pp，后期+21.40pp只是1条。信用12m年代−8.50/+1.37/+12.43pp，后期−0.94pp。跨年代方向边界阻止通用原则成立。

高vol24m开发总池正差，但HK/DE/UK为负；后期总池正差只有1块、11条高组，对连续独立未来周期无确认能力。根协议门槛与旧JSON没有修改。

真正未来检验需每月捕获当时源快照；首月末2026-10-30仍PENDING_DECISION，不能补造未发生的预测。

## 直接对应先前2016–2023的固定分区比较（presentation v003）

RAW OBSERVATIONS：2000–2015合格主12m1193，2016–2023合格主12m736，2024–2025合格主12m158；信用变量仅限各分区US合格发布。

EFFECTIVE SAMPLE ASSESSMENT：旧路径均有曝光；先后分区有前瞻收益重叠，较晚只有1块。差异是边际日期等权相关，非独立未来OOS或matched因果结果。

|时期|变量|12m组1/组0 N raw|12m组间差|24m组间差|12m区间状态|
|---|---|---:|---:|---:|---|
|2000–2015|H-P3-TREND|798/395|+0.08pp|-7.52pp|DESCRIPTIVE_BLOCK_INTERVAL|
|2000–2015|H-P3-DRAWDOWN|212/981|-2.27pp|+18.04pp|DESCRIPTIVE_BLOCK_INTERVAL|
|2000–2015|H-P3-VOL|488/614|-0.09pp|+9.50pp|DESCRIPTIVE_BLOCK_INTERVAL|
|2000–2015|H-P3-CREDIT|199/542|-6.41pp|+0.62pp|DESCRIPTIVE_BLOCK_INTERVAL|
|2016–2023|H-P3-TREND|479/257|-1.31pp|-2.35pp|DESCRIPTIVE_BLOCK_INTERVAL|
|2016–2023|H-P3-DRAWDOWN|81/655|+9.27pp|+17.83pp|DESCRIPTIVE_BLOCK_INTERVAL|
|2016–2023|H-P3-VOL|372/364|+4.54pp|+8.30pp|DESCRIPTIVE_BLOCK_INTERVAL|
|2016–2023|H-P3-CREDIT|289/255|+7.43pp|+3.65pp|DESCRIPTIVE_BLOCK_INTERVAL|
|2024–2025|H-P3-TREND|135/23|-3.95pp|+0.98pp|UNRELIABLE_FEWER_THAN_4_BLOCKS|
|2024–2025|H-P3-DRAWDOWN|2/156|+32.03pp|+21.40pp|UNRELIABLE_FEWER_THAN_4_BLOCKS|
|2024–2025|H-P3-VOL|79/79|+12.43pp|+22.24pp|UNRELIABLE_FEWER_THAN_4_BLOCKS|
|2024–2025|H-P3-CREDIT|102/17|-0.94pp|UNKNOWN|UNRELIABLE_FEWER_THAN_4_BLOCKS|

2016–2023信用收紧组12m正差约+7.43pp，2000–2015则−6.41pp，较晚为−0.94pp；高相对vol的12m正差也没有在较早时期整体重现。不能将单一时期的回归/分组漂亮结果提升成通用条件。

趋势与大跌单变量不能验证原两个宏观组合、旧r63/r252概率判断或每周切换策略；这些旧结果不重跑、不覆盖。全部前瞻期限与负对照已经保存，不选最有利的时间尺度。

## 后续两轮反证checkpoint（presentation v004）

RAW OBSERVATIONS：主panel仍2704；两个后续study新增决策点和预测为0。

EFFECTIVE SAMPLE ASSESSMENT：同一开发/后来价格路径多次被复用，独立N未识别；后续探索研究登记晚于主结果，不允许称新的OOS。

|US股票相对vol同季度对照|2000–09|2010–19|2020–25|
|---|---|---|---|
|12m|+5.09pp; [-8.79, 12.58]pp; Q=19|+10.69pp; [9.35, 12.13]pp; Q=17|+7.32pp; UNRELIABLE（2块）；Q=7|
|24m|+5.18pp; [-11.95, 16.40]pp; Q=19|+21.23pp; [8.58, 35.52]pp; Q=17|+24.85pp; UNRELIABLE（2块）；Q=5|

早期点差正但区间跨0；2020以后只有少量双方quarter/时间块，不能根据窄bootstrap区间推断跨危机稳定。遗漏对照全时期正值不能替代独立非US风险匹配或未来验证。

国债久期类的相对vol12/24m点差负，说明产业/资产现金流与久期结构须分别建机制。US股票关联暂存PAC-P3-001（C，限定LEVEL2），不是通用规律；原操作性框架、旧预测和信用拒绝门槛不改。
