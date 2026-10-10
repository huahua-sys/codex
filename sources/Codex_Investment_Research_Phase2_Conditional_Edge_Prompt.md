# Investment Research Lab — Next Research Prompt
## Phase: Conditional Edge, Regime Dependence, and Investment Philosophy Extraction

继续当前 Investment Research Lab。

不要重新开始。
不要重建已有目录。
不要重复之前已经完成的Historical Replay。
不要重新优化已经失败的简单择时规则。

首先读取并理解当前项目状态，至少包括：

- RESEARCH_CONSTITUTION.md
- RESEARCH_LEDGER.md
- HYPOTHESIS_REGISTRY.md
- CANDIDATE_PRINCIPLES.md
- FAILED_HYPOTHESES.md
- OPEN_QUESTIONS.md
- CURRENT_FRAMEWORK.json
- PREDICTION_LEDGER.md
- EPISODE_INDEX.md
- INDUSTRY_SIGNAL_DIFFERENCES.md
- research/status/LATEST.md
- 已完成的282个Historical Replay结果
- 已有所有benchmark、卖出规则和组合结果

从现有研究状态继续。

==================================================
一、本阶段的核心问题
==================================================

当前重要事实是：

1. 已经完成大量历史盲测；
2. 简单趋势/择时规则未稳定击败简单固定股债组合；
3. 某些规则可能降低回撤，但尚未证明能提高长期收益；
4. 目前还没有足够证据证明存在“万能择时规则”。

不要试图把失败的通用择时规则救回来。

本阶段目标改为：

> 找到“条件性优势（Conditional Edge）”，并逐渐提炼真正有用的投资哲学。

我们要回答的不是：

“哪个指标最好？”

而是：

> 在什么环境、什么行业、什么基本面、什么估值和什么市场状态组合下，某类信号才真正提高未来1周—24个月的赔率？

最终目标不是复杂模型。

最终目标是：

INVESTMENT DECISION ARCHITECTURE

即：

什么情况下应该买，
什么情况下应该持有，
什么情况下应该卖，
什么情况下应该等待，
什么情况下应该保护资本。

==================================================
二、冻结失败结果
==================================================

把当前已经测试过但没有稳定超过benchmark的简单择时/趋势规则冻结。

禁止通过：

- 改参数
- 改时间窗口
- 改样本起点
- 删除失败年份
- 删除失败市场
- 删除异常值
- 只保留有效行业

来“救活”它们。

正式记录：

NO EVIDENCE OF GENERIC TIMING EDGE

如果某规则可以显著降低最大回撤或左尾风险，但不能提高收益：

单独记录为：

RISK-REDUCTION CANDIDATE

不要把风险控制能力误写成预测收益能力。

==================================================
三、先做错误分类，而不是继续加指标
==================================================

把282个episode按以下方式分类：

1. True Positive
预期上涨，后来上涨

2. False Positive
预期上涨，后来没有上涨或明显下跌

3. True Negative
预期风险高/下跌，后来确实表现差

4. False Negative
预期差，但后来明显上涨

5. Correct No-Trade
判断“不值得下注”，后来也没有明显错过高赔率机会

6. Missed Opportunity
判断“不操作”，但后来出现明显高赔率上涨

对每一类，尤其是False Positive和False Negative，研究：

当时遗漏了什么？

可能包括但不限于：

- valuation
- earnings revisions
- earnings quality
- ROIC
- free cash flow
- balance sheet
- credit
- liquidity
- rates
- inflation
- policy execution
- capital cycle
- industry supply
- inventory
- positioning
- crowding
- breadth
- volatility
- insider actions
- long-term contracts
- real CapEx
- market expectations
- price-in
- geopolitical shock
- forced selling

不要因为这里列出这些变量就默认它们重要。

统计：

哪些“遗漏解释”反复出现在错误案例中？

生成：

ERROR_TAXONOMY.md

==================================================
四、从“单因子”转向“条件性规律”
==================================================

不要继续问：

X 是否预测未来收益？

改问：

X 在什么条件下才有用？

例如仅作为研究结构：

趋势向上
+
盈利上修
+
估值不极端

可能比单独趋势更有意义。

但不要假设这个组合一定有效。

所有组合必须满足：

1. 有经济逻辑；
2. 条件数量尽可能少；
3. 事先登记；
4. 不允许自由组合几十个变量；
5. 必须找反例；
6. 必须做稳定性测试。

目标：

寻找“最小充分条件”。

优先研究2–3个条件的组合。

禁止构建10+变量的打分模型。

==================================================
五、优先研究以下8个条件维度
==================================================

不要一次全部组合。

按研究价值分批研究。

### 1. Valuation
便宜 / 中性 / 昂贵

问题：

- 估值本身是否有预测力？
- 是否只在长周期有效？
- 是否必须和盈利方向结合？

### 2. Earnings / Fundamental Direction
改善 / 平稳 / 恶化

重点：

- earnings revision
- FCF trend
- margin
- ROIC
- revenue growth
- balance sheet

### 3. Credit
宽松 / 中性 / 收紧

问题：

- 信用环境是否决定“抄底是否安全”？
- 信用恶化时低估值是否经常是价值陷阱？

### 4. Rates / Inflation
利率上升 / 平稳 / 下降
高通胀 / 低通胀
通胀上升 / 下降

### 5. Liquidity
宽松 / 中性 / 紧缩

### 6. Trend / Breadth
趋势向上/向下
上涨广度改善/恶化

### 7. Capital Cycle
供给不足 / 正常 / 过度扩产

### 8. Price-In / Expectations
低预期 / 中性 / 极端乐观

==================================================
六、重点研究交互效应
==================================================

优先研究以下问题，但不要假设答案：

Q1.
估值便宜 + 盈利改善
是否明显优于
单纯估值便宜？

Q2.
高估值 + 盈利持续上修
是否可能继续获得正收益？

Q3.
趋势向上本身没有优势，
但是否能作为基本面改善后的确认过滤器？

Q4.
信用环境改善
是否是“错杀后抄底成功”的必要条件之一？

Q5.
高估值 + 信用收紧 + 盈利修正转负
是否是较稳定的中期风险组合？

Q6.
行业资本开支快速增加
在不同产业中是否有完全不同的含义？

Q7.
极端悲观 + 基本面未恶化
是否比单纯低估值更有意义？

Q8.
长期合同 / 政策真实执行 / CapEx兑现
是否比“政策讲话/故事”具有更稳定的中期预测力？

每个问题先建立Hypothesis ID。

==================================================
七、必须做Residual Research
==================================================

很多所谓“规律”只是市场beta。

因此：

对所有候选信号问：

它是否真的增加了相对于简单benchmark的信息？

Benchmark至少包括：

- Buy & Hold
- 50/50股票/短债
- 60/40股票/债券
- 70/30股票/债券
- 现金/短债

允许使用简单：

- matched sample
- simple regression
- conditional return table
- event study

目的：

研究“增量信息”。

不是建立复杂预测模型。

==================================================
八、必须做Placebo和扰动测试
==================================================

任何看起来有效的条件规则，都至少做：

### Placebo
- 随机日期
- 随机信号
- 随机打乱标签
- 随机持有期

### Perturbation
轻微改变：

- 起点日期
- 持有期
- 阈值
- 市场
- 行业

如果结果轻微变化就消失：

标记：

FRAGILE

真正有价值的规律应该允许合理扰动。

==================================================
九、分开研究“赚钱”与“避险”
==================================================

建立三类结果：

### RETURN EDGE
提高长期收益

### DOWNSIDE PROTECTION EDGE
减少大亏、左尾、最大回撤

### RETURN/RISK EDGE
风险收益比改善

不能因为一个规则降低回撤，
就说它“预测准确”。

也不能因为一个规则不提高CAGR，
就完全否定它的防御价值。

==================================================
十、研究上涨和下跌的不对称性
==================================================

禁止假设一个信号对上涨和下跌作用对称。

分别研究：

UP-SIDE SIGNALS

和

DOWN-SIDE WARNING SIGNALS

可能存在：

某个信号非常擅长避免暴跌，
但完全不会选牛股。

另一个信号很擅长发现趋势，
但不能预测危机。

这是允许的。

==================================================
十一、重点研究Underreaction
==================================================

我们主要做中期交易，最快周期一周。

因此重点寻找：

市场无法一次性处理的信息。

优先研究：

- earnings revision persistence
- long-term contracts
- policy implementation
- real government procurement
- repeated CapEx
- order growth
- industry penetration
- supply bottlenecks
- insider open-market buying
- repeated corporate capital allocation
- inventory normalization
- credit improvement

研究：

这些信息出现后，
市场是否仍然在未来数周到数月继续调整？

如果是：

可能存在

SLOW INFORMATION DIFFUSION

这是非常重要的候选机制。

==================================================
十二、重点研究Overreaction / Mispricing
==================================================

研究：

什么情况下短期下跌是错杀？

什么情况下其实是结构恶化？

优先研究事件：

- 战争
- 临时油价冲击
- liquidity shock
- forced selling
- fund redemption
- one-off regulation
- political event
- temporary earnings miss

尝试区分：

TEMPORARY MISPRICING

vs

STRUCTURAL DETERIORATION

重点寻找事前可以看到的区分变量，例如：

- credit condition
- balance sheet
- refinancing
- earnings revisions
- demand
- supply
- industry capacity
- pricing power
- policy response capacity

==================================================
十三、从预测“价格”转向预测“变化”
==================================================

尝试回答：

哪些基本面变化比股票涨跌更容易预测？

例如：

- 盈利修正方向
- ROIC变化
- margin变化
- credit deterioration
- inventory cycle
- CapEx cycle
- industry supply
- demand acceleration
- policy implementation

研究链条：

先预测：

FUNDAMENTAL CHANGE

再研究：

MARKET REACTION

最终问：

市场反应快还是慢？

这可能比直接预测价格更稳健。

==================================================
十四、行业必须分开
==================================================

利用当前行业代理，至少研究：

- 科技
- 半导体
- 金融
- 资源
- 工业
- 消费
- 医药
- 公用事业

重点回答：

同一个变量为什么意义不同？

例如：

CapEx上升：

科技：
可能意味着增长投入

资源：
可能意味着未来产能过剩

公用事业：
可能意味着rate base扩张

银行：
CapEx本身可能不是核心变量

逐渐建立：

INDUSTRY_SPECIFIC_RULES.md

不要建立“所有股票统一模型”。

==================================================
十五、Regime研究
==================================================

把现有episode尽可能分到：

- 牛市
- 熊市
- 高通胀
- 低通胀
- 加息
- 降息
- 高增长
- 衰退
- 信用宽松
- 信用紧缩
- 流动性宽松
- 流动性紧缩

然后研究：

同一个规则是否只在特定regime有效？

如果是：

不要降低为“失败”。

记录为：

REGIME_DEPENDENT

并继续研究：

如何事前识别regime？

==================================================
十六、Price-In必须成为正式模块
==================================================

任何利好或基本面改善必须问：

市场已经知道多少？

建立：

PRICE_IN_FRAMEWORK.md

至少研究：

- valuation
- historical percentile
- relative valuation
- implied growth
- analyst expectations
- earnings revision
- prior price move
- crowding
- positioning

如果方向判断正确，
但价格已经提前反映：

仍然不是好投资。

==================================================
十七、Sell Framework
==================================================

研究卖出，而不只是买入。

创建：

SELL_FRAMEWORK.md

区分：

1. Thesis-based sell
2. Valuation-based sell
3. Risk-based sell
4. Opportunity-cost sell
5. Price-only sell

重点研究：

哪些卖出逻辑在历史上真正有价值？

哪些只是：

“涨多了就卖”

导致长期收益下降？

==================================================
十八、No-Trade Framework
==================================================

建立：

NO_TRADE_FRAMEWORK.md

研究：

什么情况下：

“不操作”

是期望值最高的决定？

例如：

- 没有估值优势
- 没有趋势确认
- 基本面不确定
- 信用恶化
- 现金收益率高
- 风险收益不对称
- 市场已price in

现金/短债必须作为正式选择。

==================================================
十九、研究“投资钥匙”的来源
==================================================

对所有存活规律必须解释：

为什么市场没有把它套利掉？

可能来源：

- slow information diffusion
- institutional constraints
- career risk
- benchmark pressure
- mandate constraints
- forced selling
- leverage
- liquidity
- regulation
- capital cycle
- human behavioral bias
- complexity
- information processing difficulty

如果找不到持续机制：

降低可信度。

==================================================
二十、不要追求“一个圣杯”
==================================================

最终投资哲学可能不是一个指标。

更可能是少数原则组合：

宏观环境
+
基本面方向
+
估值
+
信用
+
趋势确认
+
行业结构
+
Price-In

我们寻找的是：

最少数量、
最有解释力、
最稳健的规则。

不是：

最大数量的指标。

==================================================
二十一、本阶段输出要求
==================================================

必须生成：

1. ERROR_TAXONOMY.md
2. CONDITIONAL_EDGE_REPORT.md
3. INDUSTRY_SPECIFIC_RULES.md
4. PRICE_IN_FRAMEWORK.md
5. SELL_FRAMEWORK.md
6. NO_TRADE_FRAMEWORK.md
7. REGIME_DEPENDENCE_REPORT.md
8. SURVIVING_CANDIDATES.md

并更新：

- RESEARCH_LEDGER.md
- HYPOTHESIS_REGISTRY.md
- CANDIDATE_PRINCIPLES.md
- FAILED_HYPOTHESES.md
- OPEN_QUESTIONS.md
- CURRENT_FRAMEWORK.json
- PREDICTION_LEDGER.md
- CHANGELOG.md
- research/status/LATEST.md

==================================================
二十二、SURVIVING_CANDIDATES要求
==================================================

最多保留5个当前最有希望的候选规律。

每个必须写：

Candidate ID

Statement

Economic Mechanism

Evidence For

Evidence Against

False Positives

False Negatives

Markets Tested

Industries Tested

Regimes Tested

Price-In Risk

Placebo Result

Parameter Stability

Benchmark Comparison

Expected Value Direction

Downside Risk

Why It May Persist

Why It May Fail

Confidence

Next Cheapest Falsification Test

本轮最高可信度：

B-

禁止A。

==================================================
二十三、研究优先级
==================================================

优先研究：

1. 能解释大量错误案例的变量
2. 能改变实际投资决策的变量
3. 有经济机制的变量
4. 能以低计算成本证伪的假设
5. 能跨市场/跨行业验证的规律

降低优先级：

1. 仅提高回测Sharpe
2. 需要大量参数优化
3. 只能在单一时期有效
4. 无法解释为什么存在
5. 依赖不可获得数据

==================================================
二十四、不要立即增加海量数据
==================================================

先充分利用现有282个episode。

只有当一个高价值问题：

无法使用当前数据回答，

才明确写：

DATA REQUIRED

然后只新增解决该问题所需的数据。

不要为了“更多数据”而无限抓数据。

==================================================
二十五、完成本阶段后的核心回答
==================================================

最终报告必须明确回答：

1. 简单择时为什么没有稳定优势？
2. 趋势到底是预测工具，还是确认工具？
3. 估值什么时候有用？
4. 盈利修正有没有独立预测价值？
5. 信用是否决定什么时候可以安全抄底？
6. Capital Cycle能否解释“好行业为什么是差投资”？
7. 哪些信号主要用于防大亏？
8. 哪些信号主要用于抓上涨？
9. 哪些规律只在特定行业有效？
10. 哪些规律只在特定regime有效？
11. 什么信息最容易被市场反应不足？
12. 什么事件最容易造成市场过度反应？
13. 什么条件最能区分错杀与结构恶化？
14. 什么情况下“不投资”是最优决策？
15. 目前最接近“投资钥匙”的1–3条是什么？
16. 为什么这1–3条仍然可能是错的？
17. 还需要什么证据才能升级？

==================================================
二十六、最后必须导出文件
==================================================

本轮完成后，不要只在聊天里总结。

创建：

/workspace/outputs/investment_research_phase2/

把本轮所有重要输出复制进去。

创建：

README_FOR_REVIEW.md

说明：

- 本轮研究了什么
- 最重要结论
- 失败结论
- 当前候选规律
- 下一步问题
- 建议人工优先阅读哪些文件

然后压缩：

/workspace/outputs/Investment_Research_Lab_Phase2.zip

检查ZIP不为空。

如果当前界面支持附件/artifact发布：

请把ZIP作为可下载文件输出。

如果不支持：

明确告诉我ZIP路径，并保留文件。

==================================================
最终原则
==================================================

不要为了找到“钥匙”而制造钥匙。

我们要做的是：

让错误假设一个个死掉，
让真正有用的规律在反例、跨市场、跨行业、跨regime和placebo测试中活下来。

如果最终只剩：

“资产配置 + 少数条件性错杀机会 + 风险控制”

也完全接受。

如果最终发现：

“很多投资理论没有稳定预测能力”

也接受。

真正的目标不是复杂。

而是：

找到少数在真实世界里能持续提高期望值的原则。

现在继续执行。
