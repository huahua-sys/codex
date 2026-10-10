# Phase 2：Price-In 正式研究模块

更新：2026-10-09 UTC。状态：`TYPED_RESEARCH_MODULE / HISTORICAL_EXPECTATIONS_DATA_REQUIRED`。模块用于识别当前投资价格要求什么、当时市场预期了什么；尚未提供实证交易规则。当前374个成熟12m标签只有价格/行动修正财富特征，缺历史估值与一致预期快照，**不能判断某次涨跌是不是“已经Price In”**。

## 必须区分的三个问题

1. 产业或公司会发生什么？用当时已公开经营证据构成情景。
2. T时市场价格需要哪些经营与融资假设？用T时可得价格、财务和固定估值方法反推。
3. T时市场原先预期什么，新增信息相对它改变了多少？需要有时间戳的预期基线与实际披露。

三者有差距才形成待测价格反应问题。过去涨得多只能说明曾经发生价格变化；不能替代“隐含增长极端”“拥挤”“预期很高”。低PE不能替代便宜，尤其不能把峰值周期盈利或金融业不可比现金流当永久盈利。未来上涨或下跌只允许进入Outcome Label。

## Typed module 与准入

每个episode保存一个模块，资产、cutoff、币种与经济实体必须明确。全部字段都采用下列类型；`UNKNOWN`是一等状态，不取零、不使用均值填补、不触发卖出或WAIT。数值只有在来源、口径和T时可得性通过检查后出现。

```json
{
  "module_id": "PRICE_IN-v001",
  "episode_id": "required",
  "asset_id": "required",
  "cutoff_at": "ISO-8601 UTC",
  "module_status": "UNKNOWN | OBSERVED_PARTIAL | HYPOTHESIS_READY",
  "field_type": {
    "status": "KNOWN_AT_T | POINT_IN_TIME_UNCERTAIN | UNKNOWN | NOT_APPLICABLE",
    "value": null,
    "units": null,
    "economic_scope": null,
    "reference_period": null,
    "published_at": null,
    "available_at": null,
    "source_id": null,
    "source_sha256": null,
    "vintage_id": null,
    "definition_version": "required when observed",
    "missing_reason": "required when UNKNOWN",
    "known_limitations": []
  },
  "fields": {
    "valuation": "field_type",
    "historical_percentile": "field_type",
    "relative_valuation": "field_type",
    "implied_growth": "field_type",
    "analyst_expectations": "field_type",
    "earnings_revision": "field_type",
    "prior_price_move": "field_type",
    "crowding": "field_type",
    "positioning": "field_type"
  },
  "inference_status": "UNKNOWN | DESCRIPTIVE_GAP | EXPLORATORY_CONDITIONAL_ASSOCIATION",
  "price_in_conclusion": null,
  "operational_signal": null
}
```

这是字段类型契约的可读表示，九字段没有权重，没有加总分。不能因为只有一个观测通过就把模块标为完整；每个假设单独声明它需要哪2—3个字段，其他缺失保留。`published_at <= available_at <= cutoff_at`、原vintage可追溯、财务口径相容才准入。重述与今天修订值隔离；字段后续更正新建版本，旧判断和旧锁保持不变。

|字段|定义及最小当时证据|本轮状态|最常见误读|
|---|---|---|---|
|valuation|T价与当时已公开的每股盈利/股东现金/净资产；口径因行业而异。TTM与forward分开|`UNKNOWN / DATA_REQUIRED`|用今天重述盈利回填，或用财期末代替filing/release；指数估值须当时成分与权重|
|historical_percentile|只在T之前、同定义与同经济范围的历史估值分布计算；历史窗、缺失与负盈利处理预登记|`UNKNOWN / DATA_REQUIRED`|用包含未来的全样本percentile；把有限存活公司分布当全市场|
|relative_valuation|T时同口径可比公司/行业和跨资产融资成本；可比集事先冻结，不按后来赢家选|`UNKNOWN / DATA_REQUIRED`|比较不同增长、债务、资本需求却称便宜；今日同行分类回填|
|implied_growth|固定逆向估值情景；公开T价、最新可得现金/资本基础、折现率与终值假设，反求需要的经营路径|`UNKNOWN / DATA_REQUIRED`|反求值不是实际市场一致预期；多改折现/终值直到看似便宜|
|analyst_expectations|带时间戳的历史一致预期或分析师原报告；预测期间、估计人数、更新截止明确|`UNKNOWN / DATA_REQUIRED`|当前接口的历史EPS不等于当时consensus；公司guidance不能冒充独立市场预期|
|earnings_revision|同一目标财期、同口径、两次当时可得预期快照之差；区分roll-forward和真正修正|`UNKNOWN / DATA_REQUIRED`|财年滚动形成上修；样本分析师换人；股价上涨冒充上修|
|prior_price_move|T前63/252-session行动修正财富变化；不把当前复权价格当原quote vintage|`OBSERVED_PARTIAL`，377有效预测有趋势输入|涨幅不是Price-In程度；分红、split和币种变化须处理|
|crowding|当时可得持有人集中、基金暴露/资金流或借券信息；含发布日期、观察期与披露滞后|`UNKNOWN / DATA_REQUIRED`|13F季度末不等于市场当时已见；价格上涨不是拥挤|
|positioning|原始持仓/衍生品/融券报告的发布时间、报告期和经济范围；例如依法公布的聚合头寸|`UNKNOWN / DATA_REQUIRED`|非商业期货头寸不是股票全市场持仓；报告期末不是公开时点|

先预测经营变化再看市场反应能区分两种失败：经营判断错；经营判断对但价格相对benchmark没有增量。第二种仍不能直接归因为Price-In，须检查预期基线、融资、成本、市场beta与随机性。无法识别原因时记 `UNRESOLVED`，不以漂亮解释补空值。

## 三个最小组合：待测研究设计，全为D

以下本地设计ID不属于已验证候选，也不增加原CP-001—015的证据。没有用当前374标签搜索最佳阈值，没有自由组合九字段，没有强行救活旧趋势规则。

|设计|最少条件与经济逻辑|为何可能持续 / 为何可能消失|Kill与反证|下一项最便宜的数据|
|---|---|---|---|---|
|PIF-D01 盈利变化与价格要求|同一目标期盈利/现金预期上修 + 固定逆向估值所需经营路径仍可由当时公开的运营约束支持。逻辑是新增股东现金大于价格要求的提高；趋势只可在后续另项研究中作为确认，不能临时加入|信息处理慢或预期更新不齐；常见EPS上修可能已被算法迅速套利，真实资本需求还可能抵消盈利|无上修仍赢、上修后下跌；估值方法换小参数就翻向；上修来自周期峰值/稀释未算；对相同beta与固定配置无增量则收益假设失败|少量固定公司日历样本的原IR/filing + 两次同目标期时间戳consensus；若consensus取不到，降为公司guidance变化的另一设计，不能冒充同一变量|
|PIF-D02 执行与预期缺口|有约束长期合同/真实采购或政策执行 + 原预期基线尚未包含该现金量。区别可执行现金承诺与讲话，不假设讲话必然无效|合同会计转换慢、研究覆盖低、mandate限制；公告可能已经完全计价，合同可能可取消或无法获利|有执行但无margin/FCF兑现；公告前泄漏与预先上涨；未执行也表现好；找不到可信原预期基线则`UNKNOWN`而不是低预期|少量原合同/拨付/采购公告及取消条款、披露日期，再取同日之前guidance或原报告基线；不能仅凭公告日后走势认定underreaction|
|PIF-D03 估值要求与融资风险|固定逆向估值已要求事前上行情景 + 当时可见信用/再融资条件恶化。经济逻辑是容错空间小且融资约束使现金路径难兑现；这是防御研究，不自动等于做空收益|投资mandate、融资摩擦及职业风险阻碍卖出；广泛风险预警可能早被价格吸收，触发反弹漏判|昂贵且融资恶化仍大涨；信用proxy与公司债务不匹配；降风险反复错失上涨；左尾下降但收益变差须单列`RISK-REDUCTION CANDIDATE`|原债务到期/现金披露 + 有历史公开日期的本币信用或融资观测；原估值输入缺失则不能测试，不用美国利差替代各国信用|

三个组合的期望值方向、命中率、支持案例、placebo与独立验证现在均为 `NOT_TESTED`。不能把合理机制写成概率优势。

## 最小执行与失败标准

下一次只选一个设计。先按固定时间/客观披露条件确定样本与负对照，冻结两个条件的定义、数据准入、12m主终点及1w/1m/3m/6m/24m描述终点。先评估经营变化，再评估首次可执行价格之后的净总回报，相同标的Buy & Hold、现金/短债及固定股债配置是必要benchmark；不把本币平均标签当可执行组合。

随机信号或标签placebo须保留日期/市场簇结构；起点、持有期与估值假设只做预先小扰动，全部报告，不选最漂亮版本。若轻微扰动消失记 `FRAGILE`；若只预测经营而不增加证券回报信息，保留经营预测结论但收益候选不晋升。没有真正前瞻out-of-sample，不升高可信度。

本阶段[有限政策缺口实验](research/phase2/conditional.evidence.v001.md)说明必须保留这一区分：唯一2021触发点后来目标利率下限上升3个百分点，符合经营/政策变化方向假设，但1/1不是稳定预测；没有当时隐含政策路径与收益率结构，就无法判断变化是否早被市场预期。同期开盘执行后的股票/国债相对短债结果为未来标签，不能用它们倒推T时“尚未Price In”或“完全Price In”。

当前模块结论：`PRICE_IN_UNIDENTIFIED`。可观察的先涨先跌是市场行为；当时估值、预期与持仓缺失使“好消息已被完全反映”尚不可检验。
