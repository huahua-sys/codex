# NIGHT_XTIME_V002-003 — Stage A

Cutoff: `2005-09-30T23:59:59+00:00`；信息集 `KNOWN_AT_T`；`EXPLORATORY_RULE_BASED_MASKED_REPLAY`。

资产：SPY / US；动作：HYPOTHETICAL_LONG；置信度 D。

只运行冻结的匿名比值规则，没有按日期/资产调用历史记忆作判断。规则设计本身仍可能受先验知识影响，不能称真实事前盲测。

## 当时信息

- Macro: None；DATA_REQUIRED；记录 无
- Rates: None；DATA_REQUIRED；记录 无
- Inflation: None；DATA_REQUIRED；记录 无
- Credit: None；DATA_REQUIRED；记录 无
- Liquidity: None；DATA_REQUIRED；记录 无
- Valuation: None；DATA_REQUIRED；记录 无
- Breadth: None；DATA_REQUIRED；记录 无
- Industry: None；DATA_REQUIRED；记录 无
- Earnings: None；DATA_REQUIRED；记录 无
- Policy: None；DATA_REQUIRED；记录 无
- Capital Actions: None；DATA_REQUIRED；记录 无
- News: None；DATA_REQUIRED；记录 无
- Sentiment: None；DATA_REQUIRED；记录 无
- Trend: POSITIVE_TREND；KNOWN_AT_T；记录 YAHOO_CHART_SPY:PRICE:2005-09-29,YAHOO_CHART_SPY:PRICE:2005-06-30,YAHOO_CHART_SPY:PRICE:2004-09-30

## 正面证据（不足处明确为空）

- OBSERVED_SIGNAL: 63-session历史已知行动经济总回报=0.033550；YAHOO_CHART_SPY:PRICE:2005-06-30,YAHOO_CHART_SPY:PRICE:2005-09-29
- OBSERVED_SIGNAL: 252-session历史已知行动经济总回报=0.119544；YAHOO_CHART_SPY:PRICE:2004-09-30,YAHOO_CHART_SPY:PRICE:2005-09-29
- NO_ADDITIONAL_POSITIVE_EVIDENCE: 可靠正面证据不足；不得用故事补足。；无

## 反面证据 / 限制（限制不是反向观察）

- LIMITATION_NOT_OBSERVED_NEGATIVE_SIGNAL: 估值/盈利/信用缺失；不能排除价格已反映预期或状态改变。；无
- LIMITATION_NOT_OBSERVED_NEGATIVE_SIGNAL: 估值/盈利/信用缺失；不能排除价格已反映预期或状态改变。；无
- LIMITATION_NOT_OBSERVED_NEGATIVE_SIGNAL: 估值/盈利/信用缺失；不能排除价格已反映预期或状态改变。；无

## 概率与风险

|期限|方向|上涨概率区间 / 固定代表值|Bear/Base/Bull固定代表值|模型EV|
|---|---|---|---|---|
|1w|Bull|[0.45, 0.75] / 0.6|0.2/0.4/0.4|0.002876|

1w 情景概率区间：Bear [0.05000000000000002, 0.35]; Base [0.25, 0.55]; Bull [0.25, 0.55]；中性带 ±0.007191。

|1m|Bull|[0.45, 0.75] / 0.6|0.2/0.4/0.4|0.005895|

1m 情景概率区间：Bear [0.05000000000000002, 0.35]; Base [0.25, 0.55]; Bull [0.25, 0.55]；中性带 ±0.014737。

|3m|Bull|[0.45, 0.75] / 0.6|0.2/0.4/0.4|0.010210|

3m 情景概率区间：Bear [0.05000000000000002, 0.35]; Base [0.25, 0.55]; Bull [0.25, 0.55]；中性带 ±0.025525。

|6m|Bull|[0.45, 0.75] / 0.6|0.2/0.4/0.4|0.014439|

6m 情景概率区间：Bear [0.05000000000000002, 0.35]; Base [0.25, 0.55]; Bull [0.25, 0.55]；中性带 ±0.036098。

|12m|Bull|[0.45, 0.75] / 0.6|0.2/0.4/0.4|0.020420|

12m 情景概率区间：Bear [0.05000000000000002, 0.35]; Base [0.25, 0.55]; Bull [0.25, 0.55]；中性带 ±0.051050。

|24m|Bull|[0.45, 0.75] / 0.6|0.2/0.4/0.4|0.028878|

24m 情景概率区间：Bear [0.05000000000000002, 0.35]; Base [0.25, 0.55]; Bull [0.25, 0.55]；中性带 ±0.072196。


模型EV是未校准情景假设；不是已估计预期收益。三类情景概率不直接等于上涨概率。

Price-in: UNKNOWN: only lagged market behavior observed; no historical valuation/expectation source, cannot identify expectations already reflected

最大未知：缺少盈利、估值、信用初值和可验证政策执行；趋势延续与反转均可能发生。

Kill Thesis：

- 每周复核；若最近63或252个完整已公开时段总回报不再同时为正，则原趋势买入理由失效。
- 若数据来源、公司行动、时间证据或可交易性被否定，则暂停，不以未来结果重写原判断。

本轮终值用固定持有，Kill Thesis只作每周诊断，未模拟动态止损。原生指数仅价格标签，不等于可交易净总回报；现金0%是模型假设。
