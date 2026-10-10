# 固定配置残差：本轮解释与可复核接口

旧结果已知后的新增比较，不是新增独立盲测。17年度日期簇、六个期限、两成本全部保留。102条year/horizon记录扩展为1632条portfolio/cost长表，不增加独立 N。

主结果见 [完整报告呈现v002](benchmarks.results.v002.md)、[机器结果](benchmarks.results.v001.json)、[逐年残差](benchmarks.residuals.v001.csv)、[冻结设计](benchmarks.preregistration.v001.json) 与 [外置锁](benchmarks.preregistration.v001.lock.json)。v001报告保留；v002只修正跨期限表格及CSV相对链接，引用原报告/JSON哈希，没有数值更改。

主50bp、12m：每周切换相对50/50 SPY/BIL均值 +0.074个百分点，配对年度重采样描述范围约 −4.41 至 +4.59个百分点；相对60/40 SPY/IEF −1.96个百分点，相对70/30 −3.00个百分点。每周 MDD相对50/50平均更深1.30个百分点，相对60/40更深0.15个百分点。样本没有支持通用收益择时优势；危机窗口的局部防御不能推导通用增量信息。

每周相对BIL超额对SPY相对BIL超额的描述性OLS，12m主成本 slope=0.403、样本截距1.28%、R²=0.227。这个截距不是causal alpha；17个年度共同冲击、动态暴露和不对称回报使线性模型非常粗糙。没有用拟合结果构造新权重，也没有选择最优配置。

50/50是股票/短债；60/40、70/30是股票/7–10年国债。后者在2021起点12m跌约15.36%，因为这两个经济标签中SPY与IEF均为负；这只是结果，不能用后来通胀/衰退标签替代T时regime。固定组合绝非一定防御或最优。

所有固定组合采用初始分配后buy-and-hold，漂移权重，不再平衡。逐日财富先加权再计算MDD；不能加权各资产的MDD。平均收益是重叠窗口的简单收益均值，不能冒充CAGR或Sharpe。

残差CSV字段：year、cutoff_at、horizon、common_sessions、entry_date、exit_date、cost、portfolio_id、asset_id、gross_return、net_return、net_max_drawdown、close_wealth_MAE、close_wealth_MFE、average_stock_exposure，以及residual_vs_各固定配置。单资产行asset_id为SPY/IEF/BIL；其他为PORTFOLIO。收益和excursion为小数；空值是真实缺失。MAE/MFE基于每日收盘财富及退出开盘，不是日内高低；旧每周规则只有保存过的收益/MDD，未重跑以补填excursion。

统一标签API：`scripts.phase2_benchmarks.evaluate_cutoff(assets, cutoff_at, horizon_sessions, leg_bps=25.0)`；assets必须为已验证SPY/IEF/BIL字典。返回同common-US-session进出时点、components与固定portfolios财富路径/收益/MDD/excursion。只供独立预登记实验的Outcome层；不能作为KNOWN_AT_T特征接口。调用方需自己先锁定实验设计，不宣称旧已知价格被重新盲化。

11项合成工程核验通过；1224次旧SPY/BIL/50/50收益与MDD同窗parity通过。前者不是投资证据，后者证明新会计没有改变这些旧baseline。支付日/原quote vintage/实际费用限制仍在。
