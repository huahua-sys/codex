# Phase 2：固定配置与残差基准

本次比较在旧 102 条 SPY/BIL 卖出结果已知之后设计，属于 EXPLORATORY。没有新增预测，没有重跑或优化失败规则，没有更改旧锁定判断。固定 2008–2024 年 9 月 30 日全部 17 个起点；六期限不是 102 个独立样本。

ETF 为今天供应商历史版本的经济重建。SPY、IEF、BIL 使用相同 US 观测 session 的下一开盘进场、经过 N 个完整 session 后开盘退出。分红按 ex-date close 再投资，支付日未知；这不是经过验证的历史可执行现金回报。基金费已包含；无税和 FX。

50/50 是 SPY/BIL；60/40 和 70/30 是 SPY/IEF。IEF 为 7–10 年美国国债 ETF，含久期风险，绝不能称短债。权重只在进场时固定，之后不再平衡。回撤由逐日组合财富重算；收益为各独立持有期简单收益，不是滚动长期 CAGR。

|期限/成本|组合|年簇|平均净收益|中位净收益|平均 MDD|最差 MDD|平均股票暴露|
|---|---|---|---|---|---|---|---|
|12m/primary_50bp_roundtrip|ALWAYS_SPY|17|13.03%|17.46%|-14.98%|-40.84%|100.0%|
|12m/primary_50bp_roundtrip|ALWAYS_BIL|17|0.60%|-0.43%|-0.45%|-1.09%|0.0%|
|12m/primary_50bp_roundtrip|ALWAYS_IEF|17|2.58%|4.59%|-6.68%|-17.80%|0.0%|
|12m/primary_50bp_roundtrip|FIXED_50_50_SPY_BIL|17|6.82%|9.04%|-7.79%|-20.65%|51.6%|
|12m/primary_50bp_roundtrip|FIXED_60_40_SPY_IEF|17|8.85%|9.76%|-8.94%|-21.53%|61.4%|
|12m/primary_50bp_roundtrip|FIXED_70_30_SPY_IEF|17|9.89%|11.63%|-10.41%|-26.36%|71.2%|
|12m/primary_50bp_roundtrip|WEEKLY_SWITCH|17|6.89%|4.20%|-9.10%|-20.99%|69.4%|
|12m/primary_50bp_roundtrip|FIXED_ENTRY_CHOICE|17|7.40%|3.94%|-9.57%|-33.70%|64.7%|
|12m/fixed_10bp_sensitivity|ALWAYS_SPY|17|13.48%|17.93%|-14.96%|-40.84%|100.0%|
|12m/fixed_10bp_sensitivity|ALWAYS_BIL|17|1.00%|-0.03%|-0.16%|-0.89%|0.0%|
|12m/fixed_10bp_sensitivity|ALWAYS_IEF|17|2.99%|5.01%|-6.66%|-17.80%|0.0%|
|12m/fixed_10bp_sensitivity|FIXED_50_50_SPY_BIL|17|7.24%|9.48%|-7.76%|-20.54%|51.6%|
|12m/fixed_10bp_sensitivity|FIXED_60_40_SPY_IEF|17|9.28%|10.20%|-8.92%|-21.53%|61.4%|
|12m/fixed_10bp_sensitivity|FIXED_70_30_SPY_IEF|17|10.33%|12.08%|-10.38%|-26.36%|71.2%|
|12m/fixed_10bp_sensitivity|WEEKLY_SWITCH|17|9.02%|6.91%|-8.23%|-18.76%|69.4%|
|12m/fixed_10bp_sensitivity|FIXED_ENTRY_CHOICE|17|7.83%|4.36%|-9.45%|-33.70%|64.7%|
|24m/primary_50bp_roundtrip|ALWAYS_SPY|17|30.12%|30.25%|-19.09%|-40.84%|100.0%|
|24m/primary_50bp_roundtrip|ALWAYS_BIL|17|1.99%|0.08%|-0.46%|-1.09%|0.0%|
|24m/primary_50bp_roundtrip|ALWAYS_IEF|17|5.09%|5.63%|-9.01%|-20.76%|0.0%|
|24m/primary_50bp_roundtrip|FIXED_50_50_SPY_BIL|17|16.06%|14.84%|-10.20%|-20.65%|53.2%|
|24m/primary_50bp_roundtrip|FIXED_60_40_SPY_IEF|17|20.11%|21.52%|-11.79%|-21.72%|62.7%|
|24m/primary_50bp_roundtrip|FIXED_70_30_SPY_IEF|17|22.61%|25.56%|-13.55%|-26.36%|72.3%|
|24m/primary_50bp_roundtrip|WEEKLY_SWITCH|17|15.87%|5.92%|-12.90%|-21.04%|72.1%|
|24m/primary_50bp_roundtrip|FIXED_ENTRY_CHOICE|17|17.44%|13.71%|-12.84%|-33.70%|64.7%|
|24m/fixed_10bp_sensitivity|ALWAYS_SPY|17|30.65%|30.78%|-19.09%|-40.84%|100.0%|
|24m/fixed_10bp_sensitivity|ALWAYS_BIL|17|2.40%|0.48%|-0.19%|-0.89%|0.0%|
|24m/fixed_10bp_sensitivity|ALWAYS_IEF|17|5.51%|6.06%|-8.99%|-20.75%|0.0%|
|24m/fixed_10bp_sensitivity|FIXED_50_50_SPY_BIL|17|16.52%|15.30%|-10.19%|-20.54%|53.2%|
|24m/fixed_10bp_sensitivity|FIXED_60_40_SPY_IEF|17|20.59%|22.01%|-11.79%|-21.72%|62.7%|
|24m/fixed_10bp_sensitivity|FIXED_70_30_SPY_IEF|17|23.11%|26.06%|-13.55%|-26.36%|72.3%|
|24m/fixed_10bp_sensitivity|WEEKLY_SWITCH|17|20.09%|12.02%|-11.50%|-18.76%|72.1%|
|24m/fixed_10bp_sensitivity|FIXED_ENTRY_CHOICE|17|17.91%|14.16%|-12.74%|-33.70%|64.7%|

## 每周切换规则的增量信息

以下为固定主成本（每 leg 25bp，简单进出共50bp）。差值按同年配对；正的 MDD 差值代表每周规则回撤较浅。

|期限|基准|平均收益残差|配对年重采样2.5–97.5%|平均 MDD 差值|
|---|---|---|---|---|
|12m|ALWAYS_SPY|-6.14%|-11.84%至-0.62%|5.88%|
|12m|ALWAYS_BIL|6.29%|1.42%至11.66%|-8.64%|
|12m|ALWAYS_IEF|4.31%|-2.70%至11.56%|-2.42%|
|12m|FIXED_50_50_SPY_BIL|0.07%|-4.41%至4.59%|-1.30%|
|12m|FIXED_60_40_SPY_IEF|-1.96%|-7.21%至3.43%|-0.15%|
|12m|FIXED_70_30_SPY_IEF|-3.00%|-8.14%至2.33%|1.31%|

12m 描述性 OLS：每周规则相对 BIL 收益对 SPY 相对 BIL 收益的 slope=0.403，样本截距=1.28%，R²=0.227。这些是样本拟合描述，不能称 alpha，也不生成新组合权重。

|24m|ALWAYS_SPY|-14.26%|-21.27%至-6.98%|6.19%|
|24m|ALWAYS_BIL|13.88%|6.54%至21.63%|-12.44%|
|24m|ALWAYS_IEF|10.77%|-0.79%至22.09%|-3.89%|
|24m|FIXED_50_50_SPY_BIL|-0.19%|-5.88%至6.17%|-2.70%|
|24m|FIXED_60_40_SPY_IEF|-4.24%|-11.22%至3.76%|-1.11%|
|24m|FIXED_70_30_SPY_IEF|-6.75%|-13.29%至0.49%|0.64%|

24m 描述性 OLS：每周规则相对 BIL 收益对 SPY 相对 BIL 收益的 slope=0.544，样本截距=-1.43%，R²=0.369。这些是样本拟合描述，不能称 alpha，也不生成新组合权重。

## 解释边界

RETURN EDGE：旧每周规则是否增加收益，必须看对固定配置的配对残差；相对全股票回撤较小本身不是择时信息。DOWNSIDE PROTECTION：可以单独保留防大亏研究问题，但若固定减少股票已提供相近或更低回撤，就不能将改善全归功于信号。RETURN/RISK EDGE：仍未用连续独立投资路径、风险预算匹配和现实资金约束证实；不能用这些重叠持有期的均值冒充 Sharpe 或 CAGR。

1000 次固定 seed 年簇重采样只描述本样本差值不确定性，不是确认性统计结论；24m 标签相互重叠，年份共享危机／政策环境。没有筛选最优权重、期限、费用或起点。所有六期限及两成本保存在 JSON/CSV。

工程核验：1224 次旧 SPY、BIL、50/50 收益及 MDD 对齐全部通过；合成会计测试只验证程序。原模型概率、原结论和原判断没有改变。

接口：[benchmarks.residuals.v001.csv](research/phase2/benchmarks.residuals.v001.csv) 包含 year/cutoff/horizon/cost/portfolio_id/asset_id、净收益、MDD、close-wealth MAE/MFE 和相对每一固定基准残差。MAE/MFE 来自收盘财富与退出开盘；不是日内极值。旧每周规则只复制已保存收益/MDD，未保存的 MAE/MFE 留空，禁止以0填补。
