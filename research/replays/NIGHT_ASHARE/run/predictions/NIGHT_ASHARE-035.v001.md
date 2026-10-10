# NIGHT_ASHARE-035 — Stage A

Cutoff: `2022-09-30T23:59:59+00:00`；信息集 `KNOWN_AT_T`；`EXPLORATORY_RULE_BASED_MASKED_REPLAY`。

资产：CSI300 / CN；动作：WAIT；置信度 D。

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

## 正面证据（不足处明确为空）


## 反面证据 / 限制（限制不是反向观察）


## 概率与风险

|期限|方向|上涨概率区间 / 固定代表值|Bear/Base/Bull固定代表值|模型EV|
|---|---|---|---|---|

模型EV是未校准情景假设；不是已估计预期收益。三类情景概率不直接等于上涨概率。

Price-in: UNKNOWN: only lagged market behavior observed; no historical valuation/expectation source, cannot identify expectations already reflected

最大未知：缺少盈利、估值、信用初值和可验证政策执行；趋势延续与反转均可能发生。

Kill Thesis：

- 每周复核；若最近63或252个完整已公开时段总回报不再同时为正，则原趋势买入理由失效。
- 若数据来源、公司行动、时间证据或可交易性被否定，则暂停，不以未来结果重写原判断。

本轮终值用固定持有，Kill Thesis只作每周诊断，未模拟动态止损。原生指数仅价格标签，不等于可交易净总回报；现金0%是模型假设。
