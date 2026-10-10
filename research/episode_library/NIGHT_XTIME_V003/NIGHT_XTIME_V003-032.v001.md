# NIGHT_XTIME_V003-032 — 历史遮蔽复盘

批次 `NIGHT_XTIME_V003`；资产 `N225` / `JP`；Cutoff `2015-09-30T23:59:59+00:00`。

本报告在 Stage B 揭晓后生成，原 Stage A 未修改。它是冻结规则的历史重建，不是当年真实生成的预测；模型历史先验、今日供应商修订与逻辑隔离限制仍存在。

## 原始锁定与信息边界

- 原始 A：[预测 JSON](../../replays/NIGHT_XTIME_V003/run/predictions/NIGHT_XTIME_V003-032.v001.json) / [事前判断 Markdown](../../replays/NIGHT_XTIME_V003/run/predictions/NIGHT_XTIME_V003-032.v001.md)。
- 外部锁：[锁定记录](../../replays/NIGHT_XTIME_V003/run/locks/NIGHT_XTIME_V003-032.v001.lock.json)；锁定时间 `2026-10-08T16:17:09.990559+00:00`。
- A SHA-256：`8a7974c03a9e28e0bdae4647b628779da57cb9577195db687e7e65f4f166547e`。
- 输入 SHA-256：`621099831279b9d282cee195abf1eacee0d16760de569231c9cd3c783d2e5a69`；标签：[Stage B JSON](../../replays/NIGHT_XTIME_V003/run/labels/NIGHT_XTIME_V003-032.v001.json)，SHA-256 `08542768b40933fdf26ec2e78edbfd4dbec99435e350f28c62d5f3a32c225bcb`。
- 抽样 SHA-256：`715f200ad4195917131a53e5f5b69633075e1b642aed0b61e33e38082ac3955e`；预登记 SHA-256：`1062e0117f2210c7217f341a433652bff067ab61c9ae3413adc491b3afdd2249`。
- 哈希用于核对内容；它不证明可信历史时间戳、没有历史记忆或真正未知未来。

## KNOWN_AT_T：原判断与已知事实

规则 `R002-TREND-PRIOR-v001`；决策 `WAIT`；方向 `Base`；置信度 `D`。规则未拟合，未作参数搜索。

|字段|T 时值|证据记录|
|---|---|---|
|63 交易时段历史回报|-13.53%|["YAHOO_CHART_N225:PRICE:2015-09-30", "YAHOO_CHART_N225:PRICE:2015-06-29", "YAHOO_CHART_N225:PRICE:2014-09-17"]|
|252 交易时段历史回报|9.44%|["YAHOO_CHART_N225:PRICE:2015-09-30", "YAHOO_CHART_N225:PRICE:2015-06-29", "YAHOO_CHART_N225:PRICE:2014-09-17"]|
|252 时段年化波动|22.44%|["YAHOO_CHART_N225:PRICE:2015-09-30", "YAHOO_CHART_N225:PRICE:2015-06-29", "YAHOO_CHART_N225:PRICE:2014-09-17"]|

背景字段只重述 A。`DATA_REQUIRED` 表示没有可靠观测，不表示环境中性或信号为零。完整官方发布原文仍保存在上面的原始 A JSON。

|背景字段|状态|当时信息|证据记录|
|---|---|---|---|
|Macro|DATA_REQUIRED|缺失；未填补|[]|
|Rates|DATA_REQUIRED|缺失；未填补|[]|
|Inflation|DATA_REQUIRED|缺失；未填补|[]|
|Credit|DATA_REQUIRED|缺失；未填补|[]|
|Liquidity|DATA_REQUIRED|缺失；未填补|[]|
|Valuation|DATA_REQUIRED|缺失；未填补|[]|
|Breadth|DATA_REQUIRED|缺失；未填补|[]|
|Industry|DATA_REQUIRED|缺失；未填补|[]|
|Earnings|DATA_REQUIRED|缺失；未填补|[]|
|Policy|DATA_REQUIRED|缺失；未填补|[]|
|Capital Actions|DATA_REQUIRED|缺失；未填补|[]|
|News|DATA_REQUIRED|缺失；未填补|[]|
|Sentiment|DATA_REQUIRED|缺失；未填补|[]|
|Trend|KNOWN_AT_T|MIXED_TREND|["YAHOO_CHART_N225:PRICE:2015-09-30", "YAHOO_CHART_N225:PRICE:2015-06-29", "YAHOO_CHART_N225:PRICE:2014-09-17"]|

历史财富链实际使用 0 条已知公司行动记录，详见 A 的 `features.actions_used`。背景 `Capital Actions` 缺失不等于财富链没有公司行动。

正面证据：

- `OBSERVED_SIGNAL`：252-session历史价格回报=0.094374；证据 YAHOO_CHART_N225:PRICE:2014-09-17, YAHOO_CHART_N225:PRICE:2015-09-30。
- `NO_ADDITIONAL_POSITIVE_EVIDENCE`：可靠正面证据不足；不得用故事补足。；证据 无。
- `NO_ADDITIONAL_POSITIVE_EVIDENCE`：可靠正面证据不足；不得用故事补足。；证据 无。

反面证据与限制（限制不是反向事实）：

- `OBSERVED_SIGNAL`：63-session历史价格回报=-0.135346；证据 YAHOO_CHART_N225:PRICE:2015-06-29, YAHOO_CHART_N225:PRICE:2015-09-30。
- `LIMITATION_NOT_OBSERVED_NEGATIVE_SIGNAL`：估值/盈利/信用缺失；不能排除价格已反映预期或状态改变。；证据 无。
- `LIMITATION_NOT_OBSERVED_NEGATIVE_SIGNAL`：估值/盈利/信用缺失；不能排除价格已反映预期或状态改变。；证据 无。

Price-In：UNKNOWN: only lagged market behavior observed; no historical valuation/expectation source, cannot identify expectations already reflected。

最大未知：缺少盈利、估值、信用初值和可验证政策执行；趋势延续与反转均可能发生。。

Kill Thesis（原样引用，未以未来结果更改）：

- 每周复核；若最近63或252个完整已公开时段总回报不再同时为正，则原趋势买入理由失效。
- 若数据来源、公司行动、时间证据或可交易性被否定，则暂停，不以未来结果重写原判断。

执行状态 `DIAGNOSTIC_ONLY_THIS_ROUND_FIXED_HOLDING_NO_DYNAMIC_EXIT_LABEL`；本轮固定持有标签不能回答动态卖出是否改善结果。

## 原始概率判断

|期限|方向|上涨概率区间 / 固定计分值|Bear / Base / Bull 概率区间|模型 EV|
|---|---|---|---|---|
|1w|Base|35.00%–65.00% / 50.00%|Bear 15.00%–45.00%（计分 30.00%）; Base 25.00%–55.00%（计分 40.00%）; Bull 15.00%–45.00%（计分 30.00%）|0.00%|
|1m|Base|35.00%–65.00% / 50.00%|Bear 15.00%–45.00%（计分 30.00%）; Base 25.00%–55.00%（计分 40.00%）; Bull 15.00%–45.00%（计分 30.00%）|0.00%|
|3m|Base|35.00%–65.00% / 50.00%|Bear 15.00%–45.00%（计分 30.00%）; Base 25.00%–55.00%（计分 40.00%）; Bull 15.00%–45.00%（计分 30.00%）|0.00%|
|6m|Base|35.00%–65.00% / 50.00%|Bear 15.00%–45.00%（计分 30.00%）; Base 25.00%–55.00%（计分 40.00%）; Bull 15.00%–45.00%（计分 30.00%）|0.00%|
|12m|Base|35.00%–65.00% / 50.00%|Bear 15.00%–45.00%（计分 30.00%）; Base 25.00%–55.00%（计分 40.00%）; Bull 15.00%–45.00%（计分 30.00%）|0.00%|
|24m|Base|35.00%–65.00% / 50.00%|Bear 15.00%–45.00%（计分 30.00%）; Base 25.00%–55.00%（计分 40.00%）; Bull 15.00%–45.00%（计分 30.00%）|0.00%|

模型 EV 来自未校准的情景回报假设，不是估计出的预期收益。Bear / Base / Bull 与上涨事件是两个评分定义；Base 不是收益为零。

## KNOWN_ONLY_AFTER_T：Stage B 标签

标签状态 `REVEALED`；揭晓时间 `2026-10-08T16:18:17.336683+00:00`。主要期限固定为 12m；其余为次要描述，不能事后挑最优期限。

|期限 / 完整交易时段|入场→退出|毛收益|净收益|MAE|MFE|收盘近似最大回撤|实际情景|方向评分|
|---|---|---|---|---|---|---|---|---|
|1w / 5|2015-10-01→2015-10-08|4.75%|4.23%|-0.52%|5.14%|-0.07%|Bull|ABSTAIN；未给单方向判断|
|1m / 21|2015-10-01→2015-11-02|7.71%|7.17%|-0.52%|9.85%|-2.97%|Bull|ABSTAIN；未给单方向判断|
|3m / 63|2015-10-01→2016-01-06|5.32%|4.80%|-0.52%|14.49%|-8.19%|Base|ABSTAIN；未给单方向判断|
|6m / 126|2015-10-01→2016-04-07|-9.96%|-10.41%|-14.96%|14.49%|-25.28%|Bear|ABSTAIN；未给单方向判断|
|12m / 252|2015-10-01→2016-10-13|-3.18%|-3.66%|-14.97%|14.49%|-25.29%|Base|ABSTAIN；未给单方向判断|
|24m / 504|2015-10-01→2017-10-20|22.37%|21.76%|-14.97%|23.02%|-25.29%|Bull|ABSTAIN；未给单方向判断|

MAE / MFE 是毛财富的日频 OHLC 近似，退出日只取退出开盘；最大回撤基于收盘及入/出场开盘，不能声称重建盘中路径。期限使用 5 / 21 / 63 / 126 / 252 / 504 个完整时段，并非精确日历月。

## 决策、校准与赔率评分

|期限|Brier|情景 Brier|假设决策收益|相对同资产买入持有|上涨捕获率|下跌回避（收益差）|
|---|---|---|---|---|---|---|
|1w|0.2500|0.7400|0.00%|-4.23%|0.0000|N/A|
|1m|0.2500|0.7400|0.00%|-7.17%|0.0000|N/A|
|3m|0.2500|0.5400|0.00%|-4.80%|0.0000|N/A|
|6m|0.2500|0.7400|0.00%|10.41%|N/A|10.41%|
|12m|0.2500|0.5400|0.00%|3.66%|N/A|3.66%|
|24m|0.2500|0.7400|0.00%|-21.76%|0.0000|N/A|

WAIT 在这份锁定模型中获得假设 0% 现金收益，尚未计真实短债机会成本。捕获率仅对同资产正净收益定义；下跌回避仅对负净收益定义，缺失值不是零。单案例不能判断概率是否校准，跨案例汇总还须处理同日市场依赖和期限重叠。

## 判断是否正确，以及能够识别什么

12m：ABSTAIN；未给单方向判断。
原决策 `WAIT`；12m 净标签 -3.66%，假设决策收益 0.00%。

无论方向对错，`UNRESOLVED_MECHANISM`：这组价格标签无法区分逻辑正确、风险溢价、偶然性或遗漏变量。趋势规则本身没有检验盈利、政策执行、供需或估值因果。

由原规则与标签直接生成的诊断：

|期限|机械标签|含义|
|---|---|---|
|12m|WAIT_AVOIDED_ASSET_LOSS_VS_ZERO_CASH_ASSUMPTION|WAIT 相对该资产避免亏损；0% 现金是假设。|
|1m|MISSED_BULL_WHILE_WAITING|WAIT，随后达到预登记 Bull 情景；这只是事后标签。|
|1w|MISSED_BULL_WHILE_WAITING|WAIT，随后达到预登记 Bull 情景；这只是事后标签。|
|24m|MISSED_BULL_WHILE_WAITING|WAIT，随后达到预登记 Bull 情景；这只是事后标签。|
|6m|WAIT_AVOIDED_ASSET_LOSS_VS_ZERO_CASH_ASSUMPTION|WAIT 相对该资产避免亏损；0% 现金是假设。|

尚待证据的错误类别（不作事后归因）：

|可能类别|识别状态|
|---|---|
|missing variable|POSSIBLE_NOT_ESTABLISHED；背景缺失可确认，缺失变量是否决定结果不可确认。|
|wrong causal story|NOT_TESTED；原匿名比值规则没有识别因果机制。|
|price already reflected / valuation problem|NOT_TESTABLE；缺当时估值与一致预期。|
|regime mismatch|POSSIBLE_NOT_IDENTIFIED；不按事后牛熊命名当时环境。|
|liquidity shock / policy implementation failure|NOT_TESTABLE；缺资金流、融资约束与实际落地证据。|
|false analogy|NOT_APPLICABLE_TO_RULE；规则没有按经典事件类比。|
|capital cycle|NOT_TESTABLE；缺当时供给、库存与资本开支。|
|randomness|UNRESOLVED；价格结果不能排除随机或不可预测冲击。|

## 数据与适用范围

币种 `JPY`；回报口径 `PRICE_ONLY`；可交易性 `NONTRADABLE_INDEX`；双边总成本假设 50.0 bp。FX 未评估，跨市场数字不能直接解释为同币种投资者收益。

ETF 标签采用除息日现金权益在当日收盘再投资的经济总回报约定，不是支付日可执行交易路径。原生指数仅为价格标签及假设成本，不是可直接成交的基金总回报。

原始数据 vintage 状态：`NOT_ARCHIVED_PROVIDER_CORRECTIONS_POSSIBLE`。今日下载历史报价可能含后续更正；保守 session lag 是可观察性重建，不是归档供应商时间戳。当前存续资产样本没有退市证券与历史成分，不能外推至全部股票。

本案例是证据记录，不构成投资原则；支持 / 反例需在完整抽样与独立扩样中共同评价。
