# 夜间扩展cohort与判断边界

原 `EPISODE_SELECTION_PROTOCOL.md` 及其SHA冻结，后续不覆盖。每批独立 selection/prereg/input/prediction 外置锁；全部A锁完成并经独立QA后才B读取标签。原始判断只追加，最终准入批如下。

|批|行政选择条件|选择行|预计可判别限制|
|---|---|---:|---|
|ROUND_002_V003|2016–2023 Sep30 × SPY/HSI/N225|24|8共享日历簇|
|NIGHT_XTIME_V003|2005–2015及2024 Sep30 × 同3标的|36|另12日历簇；非真正前瞻样本|
|NIGHT_SECTOR_V002|2005–2024 Sep30 × 8固定行业代理|160|XLF20保留不足资料；7ETF可评分|
|NIGHT_XASSET|2008–2024 Sep30 × QQQ/IEF/GLD/UUP|68|美元代理不同资产经济意义，不能混同股票|
|NIGHT_ASHARE|2011–2024 Sep30 × SSE/CSI300/CHINEXT|42|CSI300/CHINEXT各14不足历史；仅SSE可评分|
|NIGHT_EARLY|2003/2004 Sep30 × 原3市场+原8行业|22|2金融不足历史；不按结果选额外年份|
|NIGHT_RECENT|2025 Sep30 × 原18标的，BIL仅另作benchmark|18|金融/CSI300/CHINEXT不足；部分12/24m未成熟|
|NIGHT_CALENDAR_CONTROL|2005–2024 Mar31 × SPY/HSI/N225|60|固定另半年phase；没有选择表现最好的月份|

前五批均在首次收益揭晓前完成行政抽样和启动A；后三批是在看到前五批结果后设计的自适应反证，不能叫独立确认。新增日期、不同市场以及行业共同暴露于相同全球冲击；43个日期属于23个日历年份。March/Sep12m及全年24m相互重叠。后续重采样共享calendar-year或固定2year block，仍仅描述。

规则始终同一个63/252已知财富比率组合与未校准先验，没有换阈值、没有挑最优、没有删除失败。XLF因分拆与股数单位不清楚，行政输入不提供价格，不准以今日处理结果默认为当时可知。其他缺数据行均保留。

Stage A上下文只是已提供档案集合；2024/25最新提供的官方release仍是2023，不表示真正当时最新政策或通胀。其发布时间和参考期显式保留，规则不用此陈旧背景作预测权重。官方实际16unique releases，Policy/Rates双视图不算两份公告。普通样本与成功/失败分类只能事后由标签定义；没有历史消息/基本面不能替样本补一个故事。

卖出/现金另有 `CASH_SELL_PREREGISTRATION.json`：17固定年起点，weeklySPY/BIL与alwaysSPY/alwaysBIL/固定起点判断/50:50比较，50bp主成本与10bp单独敏感性均保留。它是回顾性walk-forward机械检验，不修改最初WAIT=0的旧锁分数。

校准诊断另行预登记：仅同asset、target T前已经完成的历史12m标签，Beta(1,1)固定先验；比较无条件概率与趋势分类条件概率，不做参数搜索。所有已揭晓历史结果在团队范围已知，所以只能是自适应诊断，不能冒充重新盲测或前瞻样本。
