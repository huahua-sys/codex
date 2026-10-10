# Phase 2：错误分类与不能识别的遗漏变量

结论：**NO EVIDENCE OF GENERIC TIMING EDGE** 仍是当前固定规则的研究状态；本分类没有修复规则、改写预测或识别出错误的实际原因。原282个成熟12m标签与扩展374个标签分别报告。它们是历史遮蔽重构，不能称真正前瞻盲测。

## 分类口径

TP/FP使用已锁 p(up)>0.5，TN/FN使用p(up)<0.5；上涨事件为假设费用后的本币标签>0，非上涨为≤0。p=0.5单列ABSTAIN。方向预测与决策分开：负趋势给p=0.4且WAIT；混合趋势给p=0.5且WAIT，所以四分类与NO-TRADE分类可以重叠，不能相加当总案例数。

Correct No-Trade / Missed Opportunity只能评估为**outcome proxy**：WAIT且未来不超过锁定Bull band / WAIT且未来超过Bull band。每个band在Stage A按过去波动与固定持有期锁定，没有事后改阈值。这不证明等待在T时具有最高Expected Value，也不证明后来大涨曾是可识别的高赔率机会。

期限是5/21/63/126/252/504个观察交易时段，12m是原规则主要期限，其他五个是次要诊断。指数为不可直接交易的PRICE_ONLY本币标签，ETF为供应商公司行动重构总回报；50bp为冻结假设，MAE/MFE为gross路径。跨币种标签均值不是组合收益或CAGR。

## 原282与扩展374

|集合 / 期限|成熟N|TP|FP|TN|FN|Abstain|正确WAIT proxy|错过Bull proxy|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|原5批 / 1w|282|64|90|33|29|66|91|37|
|原5批 / 1m|282|74|80|29|33|66|86|42|
|原5批 / 3m|282|108|46|29|33|66|75|53|
|原5批 / 6m|282|104|50|26|36|66|68|60|
|原5批 / 12m（primary）|282|118|36|23|39|66|67|61|
|原5批 / 24m|279|116|36|10|52|65|50|77|
|全部8批 / 1w|377|100|109|39|40|89|116|52|
|全部8批 / 1m|377|112|97|35|44|89|111|57|
|全部8批 / 3m|377|148|61|32|47|89|93|75|
|全部8批 / 6m|377|139|70|31|48|89|91|77|
|全部8批 / 12m（primary）|374|156|50|27|52|89|84|84|
|全部8批 / 24m|359|147|46|15|64|87|65|101|

扩展主要期限共享43个日期簇、23个日历年份，跨资产同日相关且持有期重叠，独立N未知。430个选择行中53行不足历史，3行12m未成熟；保持UNSCORED而非补零，不再重复Historical Replay。

## 概率与决策的错误不同

|集合|锁定p(up)|N|后来上涨比例|未来净标签均值|
|---|---:|---:|---:|---:|
|原282|0.4|62|62.90%|8.66%|
|原282|0.5|66|69.70%|11.26%|
|原282|0.6|154|76.62%|9.57%|
|扩展374|0.4|79|65.82%|10.92%|
|扩展374|0.5|89|71.91%|9.84%|
|扩展374|0.6|206|75.73%|10.39%|

这些比例是相关样本的描述性校准，没有新增独立校准资格。TP可能仅小幅盈利并经历很大MAE；TN也可能只是成本后微亏。是否值得下注必须另比较赔率、左尾与真实现金/短债机会成本。ABSTAIN错过Bull可以提示代价，但不能事后把0.5改成看涨。

## 缺失变量：错误与正确案例都缺，不能当错误解释

|锁定T时字段|FP+FN缺失 / N|TP+TN缺失 / N|Abstain缺失 / N|
|---|---:|---:|---:|
|Macro|102/102 (100.00%)|183/183 (100.00%)|89/89 (100.00%)|
|Rates|65/102 (63.73%)|120/183 (65.57%)|61/89 (68.54%)|
|Inflation|65/102 (63.73%)|120/183 (65.57%)|61/89 (68.54%)|
|Credit|102/102 (100.00%)|183/183 (100.00%)|89/89 (100.00%)|
|Liquidity|102/102 (100.00%)|183/183 (100.00%)|89/89 (100.00%)|
|Valuation|102/102 (100.00%)|183/183 (100.00%)|89/89 (100.00%)|
|Breadth|102/102 (100.00%)|183/183 (100.00%)|89/89 (100.00%)|
|Industry|102/102 (100.00%)|183/183 (100.00%)|89/89 (100.00%)|
|Earnings|102/102 (100.00%)|183/183 (100.00%)|89/89 (100.00%)|
|Policy|65/102 (63.73%)|120/183 (65.57%)|61/89 (68.54%)|
|Capital Actions|102/102 (100.00%)|183/183 (100.00%)|89/89 (100.00%)|
|News|102/102 (100.00%)|183/183 (100.00%)|89/89 (100.00%)|
|Sentiment|102/102 (100.00%)|183/183 (100.00%)|89/89 (100.00%)|

Valuation、Earnings、Credit、Liquidity、Breadth与其他字段普遍缺失，故**缺失频率不是鉴别错误的变量**。尤其不能因为错误组100%缺信用就声称100%错误由信用造成：正确组同样缺。Rates/Inflation/Policy的可见性差异主要来自US 2016–2023官方公告覆盖与市场构成；未控制覆盖差异，不能转为因果结论。

表中缺失仅指已锁context_state字段，没有事后用文本补填Macro、Industry或Capital Actions。行业ETF的mandate仍已知，分红/拆股仍用于价格回报口径；字段缺失不表示行业名称未知或公司行动未处理。KNOWN_AT_T表示过去公告确实已公开，不能自动等同于T时当前状态：例如2024年输入中的2023年公告已陈旧。机器输出保留各字段最近观测距T的天数，不能用旧值或可见性本身代替regime识别。

ROIC、FCF、margin、资产负债表、盈利修正、库存、供给、CapEx、长期合同、insider、持仓/crowding、市场预期和policy implementation没有独立T时字段。本分析只登记DATA_REQUIRED，不能把它们记为已发生的遗漏解释。没有从数据得到‘估值太高导致FP’、‘强制卖出导致FN’等频次。

## 已观察的失败结构

|主要期限类别|N|T时63时段回报均值|T时252时段回报均值|T时年化波动均值|未来净标签均值|gross MAE均值|
|---|---:|---:|---:|---:|---:|---:|
|TRUE_POSITIVE|156|7.45%|18.79%|18.25%|17.91%|-6.61%|
|FALSE_POSITIVE|50|6.87%|23.47%|16.74%|-13.08%|-19.87%|
|TRUE_NEGATIVE|27|-8.29%|-12.22%|18.26%|-9.49%|-22.68%|
|FALSE_NEGATIVE|52|-9.20%|-13.41%|22.75%|21.51%|-8.45%|
|ABSTAIN|89|-1.81%|9.40%|20.75%|9.84%|-10.30%|

FP表明两段正趋势不能作为完整的风险过滤器；FN表明两段负趋势不排除后来上涨。正/负趋势由规则定义，均值差属于类别定义和结果分组，不是新发现的预测因素。波动是已观测字段，但这里按错误标签分组的均值只用于诊断；没有据此寻找或调整一个能‘救回’规则的波动阈值。

## 六个可追溯反例

事后固定选择US/HK/JP各一个净跌幅最大的FP和一个净涨幅最大的FN，只用于审计严重错误。不是新增独立样本，不能用这些极端案例证明一般规律。T时均为原价格来源重构而非原始供应商vintage。

### NIGHT_SECTOR_V002-017 / SOXX / FALSE_POSITIVE

**KNOWN_AT_T**：T=2007-09-30T23:59:59+00:00；r63=2.63%，r252=10.21%，过去年化波动=19.56%；已锁p(up)=0.6，exposure=1。
原判断：[prediction](research/replays/NIGHT_SECTOR_V002/run/predictions/NIGHT_SECTOR_V002-017.v001.json)；T时输入：[input](research/replays/NIGHT_SECTOR_V002/ex_ante/NIGHT_SECTOR_V002-017.input.v001.json)；input SHA256 `f35a86fc57f6da2f0cdb392e2872d8884c5044b36929605c45dde6a3d7750563`。

|T时证据record_id|Observation date|available_at|Source SHA256|
|---|---|---|---|
|YAHOO_CHART_SOXX:PRICE:2006-09-27|2006-09-27|2006-09-28T04:00:00+00:00|`f38eab88e0591dce9cf74413c19264eff4944269a95f9059eb873b571372af56`|
|YAHOO_CHART_SOXX:PRICE:2007-06-29|2007-06-29|2007-06-30T04:00:00+00:00|`f38eab88e0591dce9cf74413c19264eff4944269a95f9059eb873b571372af56`|
|YAHOO_CHART_SOXX:PRICE:2007-09-28|2007-09-28|2007-09-29T04:00:00+00:00|`f38eab88e0591dce9cf74413c19264eff4944269a95f9059eb873b571372af56`|

**KNOWN_ONLY_AFTER_T**：2007-10-01→2008-09-30，12m净标签-43.49%，gross MAE-43.21%，gross MFE2.39%；scenario=Bear；WAIT分类=不适用。
未来标签：[label](research/replays/NIGHT_SECTOR_V002/run/labels/NIGHT_SECTOR_V002-017.v001.json)；label SHA256 `5c34632e6d96c7be0d9b151469e5d5393f3529789c2bae3ecaf0223b80130191`。
原因保持UNIDENTIFIED_CAUSE：没有T时估值、盈利预期或信用状态，不能填入模型记忆中的危机、产业故事或后来的政策名称。

### NIGHT_SECTOR_V002-122 / XLE / FALSE_NEGATIVE

**KNOWN_AT_T**：T=2020-09-30T23:59:59+00:00；r63=-19.28%，r252=-44.34%，过去年化波动=55.66%；已锁p(up)=0.4，exposure=0。
原判断：[prediction](research/replays/NIGHT_SECTOR_V002/run/predictions/NIGHT_SECTOR_V002-122.v001.json)；T时输入：[input](research/replays/NIGHT_SECTOR_V002/ex_ante/NIGHT_SECTOR_V002-122.input.v001.json)；input SHA256 `43452e74aedc93988956ebff13a0a3a90b19829be26611a0f9ffcf4c902ac98a`。

|T时证据record_id|Observation date|available_at|Source SHA256|
|---|---|---|---|
|YAHOO_CHART_XLE:PRICE:2019-09-30|2019-09-30|2019-10-01T04:00:00+00:00|`6a867d1836e7d0eac5ae6dd5a04cb3ea31045c0c47dc411187f2d7256f4ff050`|
|YAHOO_CHART_XLE:PRICE:2020-06-30|2020-06-30|2020-07-01T04:00:00+00:00|`6a867d1836e7d0eac5ae6dd5a04cb3ea31045c0c47dc411187f2d7256f4ff050`|
|YAHOO_CHART_XLE:PRICE:2020-09-29|2020-09-29|2020-09-30T04:00:00+00:00|`6a867d1836e7d0eac5ae6dd5a04cb3ea31045c0c47dc411187f2d7256f4ff050`|

**KNOWN_ONLY_AFTER_T**：2020-10-01→2021-10-01，12m净标签84.63%，gross MAE-8.91%，gross MFE95.94%；scenario=Bull；WAIT分类=MISSED_OPPORTUNITY_PROXY。
未来标签：[label](research/replays/NIGHT_SECTOR_V002/run/labels/NIGHT_SECTOR_V002-122.v001.json)；label SHA256 `20b316ef9e80d3d853bd583ae8b3e0ebc8569be1931279d3f096e98a0c8f8b3c`。
原因保持UNIDENTIFIED_CAUSE：没有T时估值、盈利预期或信用状态，不能填入模型记忆中的危机、产业故事或后来的政策名称。

### NIGHT_XTIME_V003-007 / HSI / FALSE_POSITIVE

**KNOWN_AT_T**：T=2007-09-30T23:59:59+00:00；r63=24.66%，r252=54.99%，过去年化波动=19.65%；已锁p(up)=0.6，exposure=1。
原判断：[prediction](research/replays/NIGHT_XTIME_V003/run/predictions/NIGHT_XTIME_V003-007.v001.json)；T时输入：[input](research/replays/NIGHT_XTIME_V003/ex_ante/NIGHT_XTIME_V003-007.input.v001.json)；input SHA256 `e389ac7d36f3d12171497aff674469f03abfb08d165e945f3a86c522e1979806`。

|T时证据record_id|Observation date|available_at|Source SHA256|
|---|---|---|---|
|YAHOO_CHART_HSI:PRICE:2006-09-20|2006-09-20|2006-09-20T16:00:00+00:00|`6ff81bd7c454cdb623557217714d8ced13ba93c2e6daae23458d4b33c6193900`|
|YAHOO_CHART_HSI:PRICE:2007-06-29|2007-06-29|2007-06-29T16:00:00+00:00|`6ff81bd7c454cdb623557217714d8ced13ba93c2e6daae23458d4b33c6193900`|
|YAHOO_CHART_HSI:PRICE:2007-09-28|2007-09-28|2007-09-28T16:00:00+00:00|`6ff81bd7c454cdb623557217714d8ced13ba93c2e6daae23458d4b33c6193900`|

**KNOWN_ONLY_AFTER_T**：2007-10-02→2008-10-14，12m净标签-38.69%，gross MAE-48.24%，gross MFE14.89%；scenario=Bear；WAIT分类=不适用。
未来标签：[label](research/replays/NIGHT_XTIME_V003/run/labels/NIGHT_XTIME_V003-007.v001.json)；label SHA256 `869f4ef1569d9985d44d64871682dfad85e1e9f03ea40aac287abc19f68e76cd`。
原因保持UNIDENTIFIED_CAUSE：没有T时估值、盈利预期或信用状态，不能填入模型记忆中的危机、产业故事或后来的政策名称。

### NIGHT_CALENDAR_CONTROL-013 / HSI / FALSE_NEGATIVE

**KNOWN_AT_T**：T=2009-03-31T23:59:59+00:00；r63=-4.29%，r252=-36.51%，过去年化波动=49.34%；已锁p(up)=0.4，exposure=0。
原判断：[prediction](research/replays/NIGHT_CALENDAR_CONTROL/run/predictions/NIGHT_CALENDAR_CONTROL-013.v001.json)；T时输入：[input](research/replays/NIGHT_CALENDAR_CONTROL/ex_ante/NIGHT_CALENDAR_CONTROL-013.input.v001.json)；input SHA256 `e03a5a6b85f416f58035c64f30f0873ffcd59da091e465e138a111ab6ad4781b`。

|T时证据record_id|Observation date|available_at|Source SHA256|
|---|---|---|---|
|YAHOO_CHART_HSI:PRICE:2008-03-18|2008-03-18|2008-03-18T16:00:00+00:00|`6ff81bd7c454cdb623557217714d8ced13ba93c2e6daae23458d4b33c6193900`|
|YAHOO_CHART_HSI:PRICE:2008-12-24|2008-12-24|2008-12-24T16:00:00+00:00|`6ff81bd7c454cdb623557217714d8ced13ba93c2e6daae23458d4b33c6193900`|
|YAHOO_CHART_HSI:PRICE:2009-03-31|2009-03-31|2009-03-31T16:00:00+00:00|`6ff81bd7c454cdb623557217714d8ced13ba93c2e6daae23458d4b33c6193900`|

**KNOWN_ONLY_AFTER_T**：2009-04-01→2010-04-08，12m净标签58.06%，gross MAE-2.43%，gross MFE68.04%；scenario=Bull；WAIT分类=MISSED_OPPORTUNITY_PROXY。
未来标签：[label](research/replays/NIGHT_CALENDAR_CONTROL/run/labels/NIGHT_CALENDAR_CONTROL-013.v001.json)；label SHA256 `8b4074313623b37fdcf966fa64cca133975760391192828cd0ab362a503f3356`。
原因保持UNIDENTIFIED_CAUSE：没有T时估值、盈利预期或信用状态，不能填入模型记忆中的危机、产业故事或后来的政策名称。

### NIGHT_CALENDAR_CONTROL-008 / N225 / FALSE_POSITIVE

**KNOWN_AT_T**：T=2007-03-31T23:59:59+00:00；r63=1.14%，r252=4.84%，过去年化波动=18.03%；已锁p(up)=0.6，exposure=1。
原判断：[prediction](research/replays/NIGHT_CALENDAR_CONTROL/run/predictions/NIGHT_CALENDAR_CONTROL-008.v001.json)；T时输入：[input](research/replays/NIGHT_CALENDAR_CONTROL/ex_ante/NIGHT_CALENDAR_CONTROL-008.input.v001.json)；input SHA256 `a3fc049c504a8049842e6cbe30845d34a01fb5b2a58c24485a5a3278fbb4d8e9`。

|T时证据record_id|Observation date|available_at|Source SHA256|
|---|---|---|---|
|YAHOO_CHART_N225:PRICE:2006-03-23|2006-03-23|2006-03-23T15:00:00+00:00|`1445f2785b5a54018f14ed35ae64b8efe6d7ff38eb6d2112a571a2f86b88e246`|
|YAHOO_CHART_N225:PRICE:2006-12-25|2006-12-25|2006-12-25T15:00:00+00:00|`1445f2785b5a54018f14ed35ae64b8efe6d7ff38eb6d2112a571a2f86b88e246`|
|YAHOO_CHART_N225:PRICE:2007-03-30|2007-03-30|2007-03-30T15:00:00+00:00|`1445f2785b5a54018f14ed35ae64b8efe6d7ff38eb6d2112a571a2f86b88e246`|

**KNOWN_ONLY_AFTER_T**：2007-04-02→2008-04-10，12m净标签-25.26%，gross MAE-32.60%，gross MFE5.48%；scenario=Bear；WAIT分类=不适用。
未来标签：[label](research/replays/NIGHT_CALENDAR_CONTROL/run/labels/NIGHT_CALENDAR_CONTROL-008.v001.json)；label SHA256 `72ca8869229a0e71563012acf160c1f7e8ac42e624317883d5c77b0198db7be7`。
原因保持UNIDENTIFIED_CAUSE：没有T时估值、盈利预期或信用状态，不能填入模型记忆中的危机、产业故事或后来的政策名称。

### NIGHT_CALENDAR_CONTROL-047 / N225 / FALSE_NEGATIVE

**KNOWN_AT_T**：T=2020-03-31T23:59:59+00:00；r63=-20.59%，r252=-11.15%，过去年化波动=21.65%；已锁p(up)=0.4，exposure=0。
原判断：[prediction](research/replays/NIGHT_CALENDAR_CONTROL/run/predictions/NIGHT_CALENDAR_CONTROL-047.v001.json)；T时输入：[input](research/replays/NIGHT_CALENDAR_CONTROL/ex_ante/NIGHT_CALENDAR_CONTROL-047.input.v001.json)；input SHA256 `a8f1421ffac428da3c7e680a0ab46d3eb0ed3e88ee9fc6b9ce23d851589aa96b`。

|T时证据record_id|Observation date|available_at|Source SHA256|
|---|---|---|---|
|YAHOO_CHART_N225:PRICE:2019-03-13|2019-03-13|2019-03-13T15:00:00+00:00|`1445f2785b5a54018f14ed35ae64b8efe6d7ff38eb6d2112a571a2f86b88e246`|
|YAHOO_CHART_N225:PRICE:2019-12-23|2019-12-23|2019-12-23T15:00:00+00:00|`1445f2785b5a54018f14ed35ae64b8efe6d7ff38eb6d2112a571a2f86b88e246`|
|YAHOO_CHART_N225:PRICE:2020-03-31|2020-03-31|2020-03-31T15:00:00+00:00|`1445f2785b5a54018f14ed35ae64b8efe6d7ff38eb6d2112a571a2f86b88e246`|

**KNOWN_ONLY_AFTER_T**：2020-04-01→2021-04-13，12m净标签57.65%，gross MAE-5.56%，gross MFE64.37%；scenario=Bull；WAIT分类=MISSED_OPPORTUNITY_PROXY。
未来标签：[label](research/replays/NIGHT_CALENDAR_CONTROL/run/labels/NIGHT_CALENDAR_CONTROL-047.v001.json)；label SHA256 `22fa44b58410867ebaf5517ba5daba3a41d52055868d666b2ad5fbdfc9956048`。
原因保持UNIDENTIFIED_CAUSE：没有T时估值、盈利预期或信用状态，不能填入模型记忆中的危机、产业故事或后来的政策名称。

## 最便宜的下一步

为已经注册的条件问题建立少量真实发布时间证据，优先一个可区分负趋势延续与反转的信用变量，或一个可以分开盈利兑现与预期过满的估值/预期变量。现有错误案例只能作探索；定义、阈值、样本与失败条件必须在新独立标签前冻结。先证明变量增量信息，再讨论最小2–3条件组合。

机器可核验输出：[summary](research/phase2/error_taxonomy.summary.v001.json)、[逐episode六期限CSV](research/phase2/error_taxonomy.rows.v001.csv)、[六反例与来源](research/phase2/error_taxonomy.examples.v001.json)。运行 `python3 scripts/phase2_error_taxonomy.py` 只读取已锁A和已揭晓B；核验原input/prediction/lock/selection/preregistration/source bundle/实现哈希以及每个T时证据的available_at。未更改旧规则与文件。
