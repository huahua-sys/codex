# NIGHT_XASSET-065 — 历史遮蔽复盘

批次 `NIGHT_XASSET`；资产 `GLD` / `US`；Cutoff `2024-09-30T23:59:59+00:00`。

本报告在 Stage B 揭晓后生成，原 Stage A 未修改。它是冻结规则的历史重建，不是当年真实生成的预测；模型历史先验、今日供应商修订与逻辑隔离限制仍存在。

## 原始锁定与信息边界

- 原始 A：[预测 JSON](../../replays/NIGHT_XASSET/run/predictions/NIGHT_XASSET-065.v001.json) / [事前判断 Markdown](../../replays/NIGHT_XASSET/run/predictions/NIGHT_XASSET-065.v001.md)。
- 外部锁：[锁定记录](../../replays/NIGHT_XASSET/run/locks/NIGHT_XASSET-065.v001.lock.json)；锁定时间 `2026-10-08T16:19:07.300171+00:00`。
- A SHA-256：`4b7e36efadeb099a3bdebdcf140ab426ccc015c2b97c191955aae3f1c59895cd`。
- 输入 SHA-256：`77d940aee0cd85359483eea15a9a1c7c530b18af047c1dba8b57e40d33b7440e`；标签：[Stage B JSON](../../replays/NIGHT_XASSET/run/labels/NIGHT_XASSET-065.v001.json)，SHA-256 `f9760512221ff308f0db46af24afe78198b20504d0cfce347d9cde6d62cd5960`。
- 抽样 SHA-256：`fb646a4a1a3cd6de70ab652f870918d80b40c8fcdb1d557676d2b388d51f921e`；预登记 SHA-256：`6aec3a4d18aa85252feee57b3223a5bcdd1d000158977f1deb7de93e5f058dc5`。
- 哈希用于核对内容；它不证明可信历史时间戳、没有历史记忆或真正未知未来。

## KNOWN_AT_T：原判断与已知事实

规则 `R002-TREND-PRIOR-v001`；决策 `HYPOTHETICAL_LONG`；方向 `Bull`；置信度 `D`。规则未拟合，未作参数搜索。

|字段|T 时值|证据记录|
|---|---|---|
|63 交易时段历史回报|13.96%|["YAHOO_CHART_GLD:PRICE:2024-09-27", "YAHOO_CHART_GLD:PRICE:2024-06-28", "YAHOO_CHART_GLD:PRICE:2023-09-27"]|
|252 交易时段历史回报|40.74%|["YAHOO_CHART_GLD:PRICE:2024-09-27", "YAHOO_CHART_GLD:PRICE:2024-06-28", "YAHOO_CHART_GLD:PRICE:2023-09-27"]|
|252 时段年化波动|14.52%|["YAHOO_CHART_GLD:PRICE:2024-09-27", "YAHOO_CHART_GLD:PRICE:2024-06-28", "YAHOO_CHART_GLD:PRICE:2023-09-27"]|

背景字段只重述 A。`DATA_REQUIRED` 表示没有可靠观测，不表示环境中性或信号为零。完整官方发布原文仍保存在上面的原始 A JSON。

|背景字段|状态|当时信息|证据记录|
|---|---|---|---|
|Macro|DATA_REQUIRED|缺失；未填补|[]|
|Rates|KNOWN_AT_T|{"fed_funds_target_high_pct": 5.5, "fed_funds_target_low_pct": 5.25}; 原文/引文字段保留于 A：original_statement_text, rate_evidence|["FED-FOMC-20160921-RATES", "FED-FOMC-20170920-RATES", "FED-FOMC-20180926-RATES", "FED-FOMC-20190918-RATES", "FED-FOMC-20200916-RATES", "FED-FOMC-20210922-RATES", "FED-FOMC-20220921-RATES", "FED-FOMC-20230920-RATES"]|
|Inflation|KNOWN_AT_T|{"cpi_core_yoy_pct_first_release": 4.3, "cpi_headline_mom_sa_pct_first_release": 0.6, "cpi_headline_yoy_pct_first_release": 3.7}; 原文/引文字段保留于 A：core_yoy_evidence, headline_mom_evidence, headline_yoy_evidence, original_release_excerpt|["BLS-CPI-09162016", "BLS-CPI-09142017", "BLS-CPI-09132018", "BLS-CPI-09122019", "BLS-CPI-09112020", "BLS-CPI-09142021", "BLS-CPI-09132022", "BLS-CPI-09132023"]|
|Credit|DATA_REQUIRED|缺失；未填补|[]|
|Liquidity|DATA_REQUIRED|缺失；未填补|[]|
|Valuation|DATA_REQUIRED|缺失；未填补|[]|
|Breadth|DATA_REQUIRED|缺失；未填补|[]|
|Industry|DATA_REQUIRED|缺失；未填补|[]|
|Earnings|DATA_REQUIRED|缺失；未填补|[]|
|Policy|KNOWN_AT_T|{"fed_funds_target_high_pct": 5.5, "fed_funds_target_low_pct": 5.25}; 原文/引文字段保留于 A：original_statement_text, rate_evidence|["FED-FOMC-20160921", "FED-FOMC-20170920", "FED-FOMC-20180926", "FED-FOMC-20190918", "FED-FOMC-20200916", "FED-FOMC-20210922", "FED-FOMC-20220921", "FED-FOMC-20230920"]|
|Capital Actions|DATA_REQUIRED|缺失；未填补|[]|
|News|DATA_REQUIRED|缺失；未填补|[]|
|Sentiment|DATA_REQUIRED|缺失；未填补|[]|
|Trend|KNOWN_AT_T|POSITIVE_TREND|["YAHOO_CHART_GLD:PRICE:2024-09-27", "YAHOO_CHART_GLD:PRICE:2024-06-28", "YAHOO_CHART_GLD:PRICE:2023-09-27"]|

历史财富链实际使用 0 条已知公司行动记录，详见 A 的 `features.actions_used`。背景 `Capital Actions` 缺失不等于财富链没有公司行动。

正面证据：

- `OBSERVED_SIGNAL`：63-session历史已知行动经济总回报=0.139575；证据 YAHOO_CHART_GLD:PRICE:2024-06-28, YAHOO_CHART_GLD:PRICE:2024-09-27。
- `OBSERVED_SIGNAL`：252-session历史已知行动经济总回报=0.407352；证据 YAHOO_CHART_GLD:PRICE:2023-09-27, YAHOO_CHART_GLD:PRICE:2024-09-27。
- `NO_ADDITIONAL_POSITIVE_EVIDENCE`：可靠正面证据不足；不得用故事补足。；证据 无。

反面证据与限制（限制不是反向事实）：

- `LIMITATION_NOT_OBSERVED_NEGATIVE_SIGNAL`：估值/盈利/信用缺失；不能排除价格已反映预期或状态改变。；证据 无。
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
|1w|Bull|45.00%–75.00% / 60.00%|Bear 5.00%–35.00%（计分 20.00%）; Base 25.00%–55.00%（计分 40.00%）; Bull 25.00%–55.00%（计分 40.00%）|0.41%|
|1m|Bull|45.00%–75.00% / 60.00%|Bear 5.00%–35.00%（计分 20.00%）; Base 25.00%–55.00%（计分 40.00%）; Bull 25.00%–55.00%（计分 40.00%）|0.84%|
|3m|Bull|45.00%–75.00% / 60.00%|Bear 5.00%–35.00%（计分 20.00%）; Base 25.00%–55.00%（计分 40.00%）; Bull 25.00%–55.00%（计分 40.00%）|1.45%|
|6m|Bull|45.00%–75.00% / 60.00%|Bear 5.00%–35.00%（计分 20.00%）; Base 25.00%–55.00%（计分 40.00%）; Bull 25.00%–55.00%（计分 40.00%）|2.05%|
|12m|Bull|45.00%–75.00% / 60.00%|Bear 5.00%–35.00%（计分 20.00%）; Base 25.00%–55.00%（计分 40.00%）; Bull 25.00%–55.00%（计分 40.00%）|2.90%|
|24m|Bull|45.00%–75.00% / 60.00%|Bear 5.00%–35.00%（计分 20.00%）; Base 25.00%–55.00%（计分 40.00%）; Bull 25.00%–55.00%（计分 40.00%）|4.11%|

模型 EV 来自未校准的情景回报假设，不是估计出的预期收益。Bear / Base / Bull 与上涨事件是两个评分定义；Base 不是收益为零。

## KNOWN_ONLY_AFTER_T：Stage B 标签

标签状态 `REVEALED`；揭晓时间 `2026-10-08T16:21:42.465772+00:00`。主要期限固定为 12m；其余为次要描述，不能事后挑最优期限。

|期限 / 完整交易时段|入场→退出|毛收益|净收益|MAE|MFE|收盘近似最大回撤|实际情景|方向评分|
|---|---|---|---|---|---|---|---|---|
|1w / 5|2024-10-01→2024-10-08|-0.58%|-1.07%|-0.62%|0.73%|-0.76%|Bear|方向错误；机制未识别|
|1m / 21|2024-10-01→2024-10-30|4.71%|4.19%|-1.86%|4.71%|-1.88%|Bull|方向正确；机制未识别|
|3m / 63|2024-10-01→2024-12-31|-1.69%|-2.18%|-3.70%|5.10%|-8.12%|Base|方向错误；机制未识别|
|6m / 126|2024-10-01→2025-04-03|15.33%|14.75%|-3.70%|17.92%|-8.12%|Bull|方向正确；机制未识别|
|12m / 252|2024-10-01→2025-10-03|45.64%|44.92%|-3.70%|46.28%|-8.12%|Bull|方向正确；机制未识别|
|24m / 504|2024-10-01→2026-10-06|55.58%|54.80%|-3.70%|107.87%|-26.40%|Bull|方向正确；机制未识别|

MAE / MFE 是毛财富的日频 OHLC 近似，退出日只取退出开盘；最大回撤基于收盘及入/出场开盘，不能声称重建盘中路径。期限使用 5 / 21 / 63 / 126 / 252 / 504 个完整时段，并非精确日历月。

## 决策、校准与赔率评分

|期限|Brier|情景 Brier|假设决策收益|相对同资产买入持有|上涨捕获率|下跌回避（收益差）|
|---|---|---|---|---|---|---|
|1w|0.3600|0.9600|-1.07%|0.00%|N/A|0.00%|
|1m|0.1600|0.5600|4.19%|0.00%|1.0000|N/A|
|3m|0.3600|0.5600|-2.18%|0.00%|N/A|0.00%|
|6m|0.1600|0.5600|14.75%|0.00%|1.0000|N/A|
|12m|0.1600|0.5600|44.92%|0.00%|1.0000|N/A|
|24m|0.1600|0.5600|54.80%|0.00%|1.0000|N/A|

WAIT 在这份锁定模型中获得假设 0% 现金收益，尚未计真实短债机会成本。捕获率仅对同资产正净收益定义；下跌回避仅对负净收益定义，缺失值不是零。单案例不能判断概率是否校准，跨案例汇总还须处理同日市场依赖和期限重叠。

## 判断是否正确，以及能够识别什么

12m：方向正确；机制未识别。
原决策 `HYPOTHETICAL_LONG`；12m 净标签 44.92%，假设决策收益 44.92%。

无论方向对错，`UNRESOLVED_MECHANISM`：这组价格标签无法区分逻辑正确、风险溢价、偶然性或遗漏变量。趋势规则本身没有检验盈利、政策执行、供需或估值因果。

由原规则与标签直接生成的诊断：

|期限|机械标签|含义|
|---|---|---|
|1w|LONG_DID_NOT_REACH_BULL_SCENARIO|LONG，随后未达到 Bull；不必然代表净收益为负。|
|1w|NONPOSITIVE_NET_OUTCOME_AFTER_LONG_SIGNAL|原 LONG 信号未取得正净收益；尚不识别原因。|
|3m|LONG_DID_NOT_REACH_BULL_SCENARIO|LONG，随后未达到 Bull；不必然代表净收益为负。|
|3m|NONPOSITIVE_NET_OUTCOME_AFTER_LONG_SIGNAL|原 LONG 信号未取得正净收益；尚不识别原因。|

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

币种 `USD`；回报口径 `TOTAL_RETURN`；可交易性 `EXCHANGE_TRADED_ETF`；双边总成本假设 50.0 bp。FX 未评估，跨市场数字不能直接解释为同币种投资者收益。

ETF 标签采用除息日现金权益在当日收盘再投资的经济总回报约定，不是支付日可执行交易路径。原生指数仅为价格标签及假设成本，不是可直接成交的基金总回报。

原始数据 vintage 状态：`NOT_ARCHIVED_PROVIDER_CORRECTIONS_POSSIBLE`。今日下载历史报价可能含后续更正；保守 session lag 是可观察性重建，不是归档供应商时间戳。当前存续资产样本没有退市证券与历史成分，不能外推至全部股票。

本案例是证据记录，不构成投资原则；支持 / 反例需在完整抽样与独立扩样中共同评价。
