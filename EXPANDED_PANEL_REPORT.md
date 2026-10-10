# Phase 3 扩展面板报告

状态：主面板LEVEL 1 — DESCRIPTIVE；后续反证形成PAC-P3-001（C级、LEVEL 2限定关联候选），零LEVEL 3投资原则。没有运行或调参旧择时规则。

## RAW OBSERVATIONS

已分析固定选择格 2704；价格feature合格 2113；合格且成熟12m 2087。六期限记录是同一起点的重复标签，不是六次独立决策。

## EFFECTIVE SAMPLE ASSESSMENT

N_effective = null。按同季度、年度和固定两年块共同抽样；跨资产同一全球冲击、行业相关和12/24m持有期重叠仍存在。混合当地币的日期等权均值只描述分布，不是可交易组合、alpha或独立实验数。

价格源属于今天重构历史，非当时vendor vintage；当前存续ETF/指数无退市证券池。指数多为当地价格回报，DAX为performance index内含分红，不能当普通price-only指数横比。ETF股息是provider条件性除息日再投资，非真实付款日执行。

## 预登记变量及全部结果

r252正/非正、252session峰值回撤≤−20%、当前vol高于过去滚动vol中位数，以及合格原SLOOS收紧/未收紧。没有阈值优化；收益不冒充估值，回撤不证明便宜。相对vol采用H-P3-VOL-ENDPOINT-v001：252个此前rolling252vol严格排当前，需要505prices；只有504条时该比较UNKNOWN，其他features不删除。

### development：主12m全资产日期等权

|变量|组1 N raw|组0 N raw|组1均值|组0均值|日期等权差|95%两年块区间|区间状态|
|---|---:|---:|---:|---:|---:|---|---|
|H-P3-TREND|1277|652|6.95%|9.26%|-0.38%|[-4.62%, 4.06%]|DESCRIPTIVE_BLOCK_INTERVAL|
|H-P3-DRAWDOWN|293|1636|14.47%|6.52%|1.77%|[-6.46%, 8.98%]|DESCRIPTIVE_BLOCK_INTERVAL|
|H-P3-VOL|860|978|9.62%|7.29%|1.66%|[-1.66%, 4.87%]|DESCRIPTIVE_BLOCK_INTERVAL|
|H-P3-CREDIT|488|797|9.64%|7.99%|1.26%|[-6.61%, 8.57%]|DESCRIPTIVE_BLOCK_INTERVAL|

成熟标签六期限：{"12m": 2021, "1m": 2021, "1w": 2021, "24m": 2021, "3m": 2021, "6m": 2021}；只有价格feature合格起点进入变量比较。

所有 5136 分组槽位（含不可判定）、所有六期限/资产/市场/行业/年代交叉均保存于 `research/phase3/analysis/development.results.v001.json`，摘要CSV与完整逐行负对照旁置。

组内分布均值、中位数、正收益比例、P25/P75/P10/P90、平均及最差MDD与同执行基准差均保存；自身被动基准差恒为0，不能据此称edge。

### holdout：主12m全资产日期等权

|变量|组1 N raw|组0 N raw|组1均值|组0均值|日期等权差|95%两年块区间|区间状态|
|---|---:|---:|---:|---:|---:|---|---|
|H-P3-TREND|135|23|14.91%|22.74%|-3.95%|不可推断（不足4块）|UNRELIABLE_FEWER_THAN_4_BLOCKS|
|H-P3-DRAWDOWN|2|156|47.67%|15.64%|32.03%|不可推断（不足4块）|UNRELIABLE_FEWER_THAN_4_BLOCKS|
|H-P3-VOL|79|79|24.17%|7.93%|12.43%|不可推断（不足4块）|UNRELIABLE_FEWER_THAN_4_BLOCKS|
|H-P3-CREDIT|102|17|15.66%|16.60%|-0.94%|不可推断（不足4块）|UNRELIABLE_FEWER_THAN_4_BLOCKS|

成熟标签六期限：{"12m": 158, "1m": 184, "1w": 184, "24m": 66, "3m": 184, "6m": 184}；只有价格feature合格起点进入变量比较。

所有 5136 分组槽位（含不可判定）、所有六期限/资产/市场/行业/年代交叉均保存于 `research/phase3/analysis/holdout.results.v001.json`，摘要CSV与完整逐行负对照旁置。

组内分布均值、中位数、正收益比例、P25/P75/P10/P90、平均及最差MDD与同执行基准差均保存；自身被动基准差恒为0，不能据此称edge。

## 反例与稳定性边界

逐行负对照保留GROUP1_NONPOSITIVE、GROUP0_POSITIVE及其相反两类；不同市场/行业/年代的方向相反不被删去。波动和信用不自动假设组1看涨。

相对SPY/BIL或固定50/50、60/40、70/30只能在同执行日期和同币种可配对时报告，海外缺当地现金为UNKNOWN；这些比较仍不控制全部beta、风险/生存差异，不证明错误定价。

主12m、副24m，其余期限描述。统计区间是探索性依赖敏感区间，少于4块标不可靠；多重比较没有校正成确认性发现。

## 人工统计核验与完整分布（presentation v002）

**RAW OBSERVATIONS：2704固定选择格；2113合格价格feature；成熟且合格12m=2087、24m=1995。** 原始六期限行16224，不是16224个独立决策。≤2023有2021可计算价格label起点，但其中92历史feature不足，变量比较只纳入1929。

**EFFECTIVE SAMPLE ASSESSMENT：N_effective=null。** 开发93季度簇/24年份/12个两年块；后期7季度簇/2年份/1块。全池USA工具多、较早年代工具少，日期等权仍不能消除存续工具、类别构成、不同日期组与共同全球regime偏差。

后期只有一个两年块，机器bootstrap区间会退化为同一个点；这只是流程输出，不能解释为精确95%置信区间。2020–23开发年代只有两个块也不可推断。所有原数值保留在JSON，突出表格显示不可推断。

### 主12m与次24m组内分布

所有数值为未来同资产收益分布；P10/P90是分位点，不是尾部十分之一均值。正收益比例不是策略准确率。

#### development

|期限|变量|组|N raw|均值|中位数|正收益比例|P25|P75|P10|P90|
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
|12m|H-P3-TREND|POSITIVE|1277|6.95%|5.52%|67.82%|-2.21%|16.85%|-14.95%|28.14%|
|12m|H-P3-TREND|NONPOSITIVE|652|9.26%|7.12%|61.81%|-5.70%|22.94%|-20.60%|40.75%|
|12m|H-P3-DRAWDOWN|LARGE_DRAWDOWN|293|14.47%|15.34%|66.89%|-9.16%|31.67%|-26.54%|53.26%|
|12m|H-P3-DRAWDOWN|OTHER|1636|6.52%|4.89%|65.59%|-2.73%|16.51%|-16.01%|28.07%|
|12m|H-P3-VOL|HIGH|860|9.62%|8.33%|68.84%|-1.98%|22.40%|-18.41%|37.02%|
|12m|H-P3-VOL|NOT_HIGH|978|7.29%|5.44%|66.16%|-2.63%|16.73%|-13.86%|28.00%|
|12m|H-P3-CREDIT|TIGHTENING|488|9.64%|8.16%|68.03%|-0.74%|22.54%|-15.79%|40.00%|
|12m|H-P3-CREDIT|NOT_TIGHTENING|797|7.99%|5.38%|69.51%|-0.67%|17.45%|-11.40%|29.09%|
|24m|H-P3-TREND|POSITIVE|1277|14.32%|11.35%|72.98%|-0.61%|29.05%|-18.08%|48.57%|
|24m|H-P3-TREND|NONPOSITIVE|652|22.26%|15.58%|71.63%|-0.72%|40.73%|-15.92%|65.32%|
|24m|H-P3-DRAWDOWN|LARGE_DRAWDOWN|293|33.08%|28.69%|74.40%|-0.02%|53.29%|-19.33%|88.65%|
|24m|H-P3-DRAWDOWN|OTHER|1636|14.12%|11.00%|72.19%|-0.70%|27.83%|-17.08%|48.55%|
|24m|H-P3-VOL|HIGH|860|21.80%|16.46%|73.26%|-0.49%|39.94%|-16.78%|62.75%|
|24m|H-P3-VOL|NOT_HIGH|978|14.94%|11.87%|74.54%|-0.36%|27.71%|-12.48%|46.35%|
|24m|H-P3-CREDIT|TIGHTENING|488|21.13%|13.56%|75.61%|0.32%|38.83%|-11.90%|63.82%|
|24m|H-P3-CREDIT|NOT_TIGHTENING|797|16.83%|14.17%|76.54%|0.36%|31.41%|-13.86%|50.31%|

|期限|变量|组|平均gross-MDD|最差gross-MDD|SPY/BIL配对N|平均配对差|
|---|---|---|---:|---:|---:|---:|
|12m|H-P3-TREND|POSITIVE|-15.27%|-68.96%|937|+1.31pp|
|12m|H-P3-TREND|NONPOSITIVE|-18.96%|-77.49%|416|+2.01pp|
|12m|H-P3-DRAWDOWN|LARGE_DRAWDOWN|-23.81%|-77.49%|173|+3.95pp|
|12m|H-P3-DRAWDOWN|OTHER|-15.22%|-68.96%|1180|+1.17pp|
|12m|H-P3-VOL|HIGH|-17.67%|-77.49%|618|+1.91pp|
|12m|H-P3-VOL|NOT_HIGH|-14.58%|-60.60%|684|+1.13pp|
|12m|H-P3-CREDIT|TIGHTENING|-16.40%|-77.49%|488|+1.64pp|
|12m|H-P3-CREDIT|NOT_TIGHTENING|-13.66%|-60.98%|754|+1.32pp|
|24m|H-P3-TREND|POSITIVE|-21.72%|-82.89%|937|+1.95pp|
|24m|H-P3-TREND|NONPOSITIVE|-23.60%|-81.95%|416|+5.36pp|
|24m|H-P3-DRAWDOWN|LARGE_DRAWDOWN|-27.74%|-79.52%|173|+7.81pp|
|24m|H-P3-DRAWDOWN|OTHER|-21.40%|-82.89%|1180|+2.29pp|
|24m|H-P3-VOL|HIGH|-23.45%|-79.52%|618|+4.78pp|
|24m|H-P3-VOL|NOT_HIGH|-20.21%|-71.77%|684|+1.79pp|
|24m|H-P3-CREDIT|TIGHTENING|-21.57%|-81.95%|488|+3.94pp|
|24m|H-P3-CREDIT|NOT_TIGHTENING|-19.52%|-82.89%|754|+2.10pp|

|期限|变量|组|50/50 SPY/BIL配对N/平均差|60/40 SPY/IEF配对N/平均差|70/30 SPY/IEF配对N/平均差|
|---|---|---|---|---|---|
|12m|H-P3-TREND|POSITIVE|792 / +2.19pp|792 / +0.05pp|792 / -0.71pp|
|12m|H-P3-TREND|NONPOSITIVE|340 / +2.74pp|340 / +1.08pp|340 / -0.16pp|
|12m|H-P3-DRAWDOWN|LARGE_DRAWDOWN|126 / +9.67pp|126 / +7.71pp|126 / +5.80pp|
|12m|H-P3-DRAWDOWN|OTHER|1006 / +1.44pp|1006 / -0.56pp|1006 / -1.34pp|
|12m|H-P3-VOL|HIGH|560 / +3.26pp|560 / +1.18pp|560 / +0.18pp|
|12m|H-P3-VOL|NOT_HIGH|559 / +1.44pp|559 / -0.48pp|559 / -1.34pp|
|12m|H-P3-CREDIT|TIGHTENING|488 / +2.52pp|488 / +0.71pp|488 / -0.38pp|
|12m|H-P3-CREDIT|NOT_TIGHTENING|644 / +2.22pp|644 / +0.09pp|644 / -0.67pp|
|24m|H-P3-TREND|POSITIVE|792 / +3.89pp|792 / -0.29pp|792 / -2.26pp|
|24m|H-P3-TREND|NONPOSITIVE|340 / +7.80pp|340 / +3.91pp|340 / +1.24pp|
|24m|H-P3-DRAWDOWN|LARGE_DRAWDOWN|126 / +21.54pp|126 / +16.82pp|126 / +13.04pp|
|24m|H-P3-DRAWDOWN|OTHER|1006 / +3.00pp|1006 / -1.01pp|1006 / -2.99pp|
|24m|H-P3-VOL|HIGH|560 / +8.12pp|560 / +4.47pp|560 / +1.71pp|
|24m|H-P3-VOL|NOT_HIGH|559 / +2.43pp|559 / -2.10pp|559 / -3.78pp|
|24m|H-P3-CREDIT|TIGHTENING|488 / +6.05pp|488 / +2.92pp|488 / +0.53pp|
|24m|H-P3-CREDIT|NOT_TIGHTENING|644 / +4.32pp|644 / -0.50pp|644 / -2.52pp|

#### holdout

|期限|变量|组|N raw|均值|中位数|正收益比例|P25|P75|P10|P90|
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
|12m|H-P3-TREND|POSITIVE|135|14.91%|12.75%|87.41%|3.34%|21.85%|-1.39%|32.98%|
|12m|H-P3-TREND|NONPOSITIVE|23|22.74%|8.51%|95.65%|5.12%|26.48%|1.16%|51.96%|
|12m|H-P3-DRAWDOWN|LARGE_DRAWDOWN|2|47.67%|47.67%|100.00%|34.67%|60.66%|26.87%|68.46%|
|12m|H-P3-DRAWDOWN|OTHER|156|15.64%|12.39%|88.46%|3.35%|22.13%|-1.11%|33.67%|
|12m|H-P3-VOL|HIGH|79|24.17%|20.51%|93.67%|10.83%|28.13%|2.87%|47.25%|
|12m|H-P3-VOL|NOT_HIGH|79|7.93%|4.86%|83.54%|1.83%|13.98%|-3.04%|21.44%|
|12m|H-P3-CREDIT|TIGHTENING|102|15.66%|9.82%|86.27%|2.44%|22.96%|-2.18%|37.15%|
|12m|H-P3-CREDIT|NOT_TIGHTENING|17|16.60%|13.61%|94.12%|6.88%|20.40%|3.46%|33.74%|
|24m|H-P3-TREND|POSITIVE|56|34.26%|28.95%|96.43%|12.16%|46.76%|5.43%|61.31%|
|24m|H-P3-TREND|NONPOSITIVE|10|28.84%|31.62%|100.00%|8.45%|50.04%|1.97%|54.74%|
|24m|H-P3-DRAWDOWN|LARGE_DRAWDOWN|1|54.47%|54.47%|100.00%|54.47%|54.47%|54.47%|54.47%|
|24m|H-P3-DRAWDOWN|OTHER|65|33.11%|28.83%|96.92%|10.01%|46.29%|5.07%|58.78%|
|24m|H-P3-VOL|HIGH|11|55.85%|46.29%|100.00%|32.52%|59.73%|28.29%|81.05%|
|24m|H-P3-VOL|NOT_HIGH|55|28.95%|27.49%|96.36%|8.54%|39.77%|4.83%|55.63%|
|24m|H-P3-CREDIT|TIGHTENING|51|33.47%|28.83%|96.08%|8.44%|50.92%|4.80%|59.86%|
|24m|H-P3-CREDIT|NOT_TIGHTENING|0|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|

|期限|变量|组|平均gross-MDD|最差gross-MDD|SPY/BIL配对N|平均配对差|
|---|---|---|---:|---:|---:|---:|
|12m|H-P3-TREND|POSITIVE|-13.90%|-41.36%|101|+3.59pp|
|12m|H-P3-TREND|NONPOSITIVE|-12.74%|-20.15%|18|+11.66pp|
|12m|H-P3-DRAWDOWN|LARGE_DRAWDOWN|-19.11%|-19.95%|1|+56.96pp|
|12m|H-P3-DRAWDOWN|OTHER|-13.66%|-41.36%|118|+4.37pp|
|12m|H-P3-VOL|HIGH|-15.68%|-35.23%|51|+13.12pp|
|12m|H-P3-VOL|NOT_HIGH|-11.78%|-41.36%|68|-1.43pp|
|12m|H-P3-CREDIT|TIGHTENING|-13.20%|-41.36%|102|+4.81pp|
|12m|H-P3-CREDIT|NOT_TIGHTENING|-14.85%|-34.24%|17|+4.80pp|
|24m|H-P3-TREND|POSITIVE|-17.94%|-41.36%|45|+9.50pp|
|24m|H-P3-TREND|NONPOSITIVE|-14.60%|-20.15%|6|+8.45pp|
|24m|H-P3-DRAWDOWN|LARGE_DRAWDOWN|-19.95%|-19.95%|0|UNKNOWN|
|24m|H-P3-DRAWDOWN|OTHER|-17.39%|-41.36%|51|+9.38pp|
|24m|H-P3-VOL|HIGH|-21.81%|-35.23%|5|+45.86pp|
|24m|H-P3-VOL|NOT_HIGH|-16.55%|-41.36%|46|+5.41pp|
|24m|H-P3-CREDIT|TIGHTENING|-17.53%|-41.36%|51|+9.38pp|
|24m|H-P3-CREDIT|NOT_TIGHTENING|UNKNOWN|UNKNOWN|0|UNKNOWN|

|期限|变量|组|50/50 SPY/BIL配对N/平均差|60/40 SPY/IEF配对N/平均差|70/30 SPY/IEF配对N/平均差|
|---|---|---|---|---|---|
|12m|H-P3-TREND|POSITIVE|101 / +5.01pp|101 / +4.09pp|101 / +2.81pp|
|12m|H-P3-TREND|NONPOSITIVE|18 / +10.89pp|18 / +9.88pp|18 / +8.42pp|
|12m|H-P3-DRAWDOWN|LARGE_DRAWDOWN|1 / +63.56pp|1 / +62.39pp|1 / +61.04pp|
|12m|H-P3-DRAWDOWN|OTHER|118 / +5.41pp|118 / +4.48pp|118 / +3.17pp|
|12m|H-P3-VOL|HIGH|51 / +17.33pp|51 / +16.62pp|51 / +14.94pp|
|12m|H-P3-VOL|NOT_HIGH|68 / -2.68pp|68 / -3.77pp|68 / -4.80pp|
|12m|H-P3-CREDIT|TIGHTENING|102 / +5.88pp|102 / +5.27pp|102 / +3.91pp|
|12m|H-P3-CREDIT|NOT_TIGHTENING|17 / +6.02pp|17 / +3.16pp|17 / +2.14pp|
|24m|H-P3-TREND|POSITIVE|45 / +13.34pp|45 / +11.94pp|45 / +8.90pp|
|24m|H-P3-TREND|NONPOSITIVE|6 / -0.04pp|6 / -1.44pp|6 / -4.48pp|
|24m|H-P3-DRAWDOWN|LARGE_DRAWDOWN|0 / UNKNOWN|0 / UNKNOWN|0 / UNKNOWN|
|24m|H-P3-DRAWDOWN|OTHER|51 / +11.77pp|51 / +10.37pp|51 / +7.33pp|
|24m|H-P3-VOL|HIGH|5 / +55.00pp|5 / +56.02pp|5 / +51.96pp|
|24m|H-P3-VOL|NOT_HIGH|46 / +7.07pp|46 / +5.41pp|46 / +2.48pp|
|24m|H-P3-CREDIT|TIGHTENING|51 / +11.77pp|51 / +10.37pp|51 / +7.33pp|
|24m|H-P3-CREDIT|NOT_TIGHTENING|0 / UNKNOWN|0 / UNKNOWN|0 / UNKNOWN|

### 口径、机制和可执行性

主MDD来自既有lab.evaluate的gross经济财富；固定配置helper使用after-cost净NAV和明确应收股息计价。固定配置残差字段采用同helper资产可比净收益减配置净收益，另保存与主label的delta。不能把gross-MDD与after-cost配置MDD直接相减；配对差也不是alpha。

大跌组12m开发raw均值14.47%对6.52%，日期等权差却只有+1.77pp，区间跨0，平均MDD−23.81%对−15.22%。回撤后尾部和样本构成对漂亮平均数很重要。后期大跌只有2条12m和1条24m，不能承担独立确认。

相对vol开发24m日期等权+9.00pp、区间[+1.74,+16.94]pp是值得反证的观察；但香港/德国/英国24m方向反例、2000年代12m负方向、较高平均MDD与跨行业差异均保留。后期正差仍只有一个全球时间块，不能升级。

信用净收紧水平的主12m年代差从−8.50pp变为+1.37pp，二元门槛失败；不运行被拒绝交互，也不把信用水平改成变化率救结论。估值、盈利修正与信用利差、借款人现金流仍缺连续原时点数据，因此不能将价格反弹归因为错杀或Underreaction。

没有重跑旧63/252策略、旧概率预测或切换配置。本面板未推翻Phase2“尚未建立edge”的证据边界，但不能冒称重新验证了旧规则全部性能。趋势可见状态的关联存在，独立预测作用与确认工具的增量价值均未建立。

## 后续两轮反证checkpoint（presentation v004）

**RAW OBSERVATIONS：复用2704固定格、2087成熟12m/1995成熟24m；两轮新增决策点/预测=0。**

**EFFECTIVE SAMPLE ASSESSMENT：N_effective=null。** 同季度同币种同类对照去除了部分共同日期影响，但行业beta、风险溢价、资本周期、估值、金融基本面和全球环境尚未匹配。所有后续研究是看过主结果之后另预登记的探索性反证，不是独立未来OOS。

### 同季度同类对照：104槽位只有12可识别

|市场/类层|变量|期限|双方季度|净收益差|两年块区间|gross-MDD差|
|---|---|---|---:|---:|---|---:|
|US/EQUITY|H-P3-TREND|12m|58|-0.74pp|[-6.44, 5.10]pp|+5.19pp|
|US/EQUITY|H-P3-TREND|24m|55|-1.80pp|[-13.76, 8.00]pp|+5.96pp|
|US/EQUITY|H-P3-DRAWDOWN|12m|39|+3.66pp|[-6.30, 12.98]pp|-7.88pp|
|US/EQUITY|H-P3-DRAWDOWN|24m|38|+6.09pp|[-15.60, 28.86]pp|-9.87pp|
|US/EQUITY|H-P3-VOL|12m|43|+7.66pp|[2.34, 11.12]pp|+0.57pp|
|US/EQUITY|H-P3-VOL|24m|41|+14.24pp|[4.82, 24.86]pp|+1.45pp|
|US/TREASURY_DURATION|H-P3-TREND|12m|24|-3.59pp|[-7.70, 0.37]pp|+6.78pp|
|US/TREASURY_DURATION|H-P3-TREND|24m|21|-5.72pp|[-11.94, 0.77]pp|+9.01pp|
|US/TREASURY_DURATION|H-P3-DRAWDOWN|12m|5|-3.24pp|[-8.25, 6.82]pp|-12.93pp|
|US/TREASURY_DURATION|H-P3-DRAWDOWN|24m|5|-9.86pp|[-12.55, 0.09]pp|-18.54pp|
|US/TREASURY_DURATION|H-P3-VOL|12m|26|-2.41pp|[-8.27, 3.50]pp|+1.47pp|
|US/TREASURY_DURATION|H-P3-VOL|24m|26|-2.59pp|[-9.41, 4.27]pp|+1.99pp|

其余92槽位是无对组、singleton或不可识别，全部保存而不删除。美国SLOOS信用状态同一个美国季度复用于各工具，无法在同date横截面匹配收紧与不收紧；原H-P3-DD-CREDIT门槛仍失败，不另跑交互救结论。

美国股票的大跌对照12/24m差+3.66/+6.09pp，区间均跨0，gross-MDD更差约7.88/9.87pp。此前漂亮的大跌平均数没有变成同日期稳定优势。

美国股票相对vol的12/24m对照差+7.66/+14.24pp，当前描述区间暂未跨0；美国国债久期类的对应点差−2.41/−2.59pp且区间跨0。它不是跨资产通用信号，也不证明风险匹配后的alpha。

### 全部遗漏与实际无重叠反证

H-P3-VOL-FALSIFICATION-v001预先登记11个版本（ALL及逐个删去10个US股票ETF）×4年代×2期限=88槽位，全部结果保留，不按最好的删减选证券。全时期所有遗漏对照点差仍正；早期2000–09区间跨0，年代和行业边界没有消失。

|严格跨分区无重叠|双方季度|净差|描述块区间|gross-MDD差|
|---|---:|---:|---|---:|
|12m|14|+6.58pp|[0.13, 12.24]pp|-0.80pp|
|24m|10|+18.68pp|[6.14, 34.65]pp|+2.27pp|

14/10双方季度是按实际entry/exit严格贪心、共同限制全部US股票的日历起点；不是14/10个独立经济世界。部分年份没有可对照组、实际持有期仍可能同一全球regime，500bootstrap不会增加真实周期。

这两轮存活的有限观察登记为PAC-P3-001，最高C级、LEVEL2、PREDICTIVE_ASSOCIATION_ONLY，限定US股票相对自身过去vol状态与12/24m相对收益。没有识别causal mechanism或risk-matched alpha，没有买入/仓位/择时规则，也没有新LEVEL3投资原则。

最重要的未解决反证：更早年代区间跨0；非US市场/国债方向不一致；beta、行业风险和存续ETF池未匹配；共同路径已被看过；大量相关切片可能给出偶然正区间。下一步优先建立独立未来记录和风险/盈利/预期数据，不调阈值。

来源：`research/phase3/matched/PREREGISTRATION.v001.json`、`RESULTS.v001.json`、`REPORT.v001.md`及`research/phase3/vol_falsification/`同名三文件，原主统计JSON和旧282/374结果保持冻结。
