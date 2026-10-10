# 同季度、同类资产反证

H-P3-MATCHED-CONTROLS-v001；主面板结果已知后的探索性反证，不是新OOS，不改原门槛/结果。

RAW OBSERVATIONS：复用2087成熟12m/1995成熟24m候选行（准确口径以主报告为准）；新增决策点/预测=0。EFFECTIVE SAMPLE ASSESSMENT：独立N未知；同季度成对去部分共同时间影响，但行业beta、风险与共同全球周期未识别。

|类层|变量|期限|双方季度|组间净收益差|两年块区间|gross MDD差|
|---|---|---|---:|---:|---|---:|
|EQUITY|H-P3-TREND|12m|58|-0.74pp|[-6.44,5.10]pp|5.19pp|
|EQUITY|H-P3-TREND|24m|55|-1.80pp|[-13.76,8.00]pp|5.96pp|
|EQUITY|H-P3-DRAWDOWN|12m|39|3.66pp|[-6.30,12.98]pp|-7.88pp|
|EQUITY|H-P3-DRAWDOWN|24m|38|6.09pp|[-15.60,28.86]pp|-9.87pp|
|EQUITY|H-P3-VOL|12m|43|7.66pp|[2.34,11.12]pp|0.57pp|
|EQUITY|H-P3-VOL|24m|41|14.24pp|[4.82,24.86]pp|1.45pp|
|EQUITY|H-P3-CREDIT|12m|0|UNKNOWN|UNKNOWN|UNKNOWN|
|EQUITY|H-P3-CREDIT|24m|0|UNKNOWN|UNKNOWN|UNKNOWN|
|TREASURY_DURATION|H-P3-TREND|12m|24|-3.59pp|[-7.70,0.37]pp|6.78pp|
|TREASURY_DURATION|H-P3-TREND|24m|21|-5.72pp|[-11.94,0.77]pp|9.01pp|
|TREASURY_DURATION|H-P3-DRAWDOWN|12m|5|-3.24pp|[-8.25,6.82]pp|-12.93pp|
|TREASURY_DURATION|H-P3-DRAWDOWN|24m|5|-9.86pp|[-12.55,0.09]pp|-18.54pp|
|TREASURY_DURATION|H-P3-VOL|12m|26|-2.41pp|[-8.27,3.50]pp|1.47pp|
|TREASURY_DURATION|H-P3-VOL|24m|26|-2.59pp|[-9.41,4.27]pp|1.99pp|
|TREASURY_DURATION|H-P3-CREDIT|12m|0|UNKNOWN|UNKNOWN|UNKNOWN|
|TREASURY_DURATION|H-P3-CREDIT|24m|0|UNKNOWN|UNKNOWN|UNKNOWN|

所有市场/类层/失败与无对组格保存在RESULTS.v001.json，不删除singleton。美国SLOOS同一季度复用于全部US资产，无法在同date横截面识别其独立作用；这不把原数据门槛失败当作信用理论被证伪。
SPY残差不是严格beta/risk-matched alpha；这里不提出持仓或买卖规则，不把一次正区间升级原则。
源码、方法、来源及结果各有独立锁。
