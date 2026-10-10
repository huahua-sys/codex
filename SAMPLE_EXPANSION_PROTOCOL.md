# Phase 3 固定扩样协议 v001

状态：先登记、后下载新历史、后生成特征锁、最后揭晓标签。用户Phase3指令优先。锁文件 `research/phase3/PROTOCOL.lock.v001.json`；机器契约 `research/phase3/design.v001.json`。任何改变须另立假设和版本，不能覆盖。

## RAW OBSERVATIONS / EFFECTIVE SAMPLE ASSESSMENT

登记时新增观察为0。计划26资产×26年×4季度=2704选择格，不承诺2704有效样本；历史不足、隔离和未成熟均保留。共同日期、市场/行业相关、12/24m重叠和全球冲击令独立N未知，禁止将记录数称独立实验。

## 1–3 市场、资产、行业

固定美国、中国A股、香港、日本、欧洲（欧元区/德国/英国）。固定资产：SPY、QQQ、HSI、N225、SSE、CSI300、CHINEXT；XLK、SOXX、XLF、KBE、XLI、XLY、XLV、XLE、XLU；IEF、TLT、SHY、BIL、GLD、UUP、DBC；STOXX50E、DAX、FTSE。不因结果换代理。XLF既有分拆未解决时全体隔离；KBE预先指定银行业窄代理，不声称金融全行业。CSI300/CHINEXT不足仍保留。行业映射写在design；只按固定工具mandate粗分类，没有历史成分/证券池推断。

## 4–6 年份、固定日期、期限

2000–2025所有季度末。每资产取该季度最后一个有完整OHLC的观察交易日，cutoff为该日之后当地00:00（保守地让最后收盘可见）；标签从cutoff后下一观察交易日开盘入场。该季度无价格仍保留calendar-quarter格为NO_SOURCE。来源只请求2000-01-01到2026-10-09，排除未完成当日。真实上市/数据开始前不得填值或虚构历史。1w/1m/3m/6m/12m/24m=5/21/63/126/252/504完整观察sessions；12m主、24m次，其余描述。不用未来结果移动日期。

## 7 变量与假设

仅三个价格变量：已知行动财富r252、252session波动、最近252session财富相对峰值回撤。r63保留为既有描述字段，不能进入新策略/组合。趋势分组r252>0 vs≤0；大跌≤−20% vs其余；波动当前252vol高于自身过去252个滚动252vol中位数 vs不高（需要504历史）。分别登记H-P3-TREND、H-P3-DRAWDOWN、H-P3-VOL；只检验变量分布稳定性，不运行原63/252概率/择时规则，不生成交易系统。

第四个高价值变量限定美国原SLOOS：大型/中型企业C&I贷款标准净收紧百分比，0为不净收紧，>0为净收紧，最新原发布距T≤180天。只用原发布表/明确同口径数值；季度调查日期不是发布日期；未知日期或数值隔离。原页面只有approximate措辞不能伪造精确值。SLOOS季度值不等于每日信用利差，也不能移植为海外本地信用。登记H-P3-CREDIT单变量。

H-P3-DD-CREDIT是用户优先的经济二元问题：回撤×信贷供给。先单变量；只有2000–09和2010–19各有至少8可用日期簇、信用两组均有观测，且12m收益组间方向一致，才运行探索性二元分组，门槛失败保留NOT_RUN_GATE_FAILED。不是择优调门槛。不得增加三变量组合。估值、盈利修正、广度、资本周期、市场隐含预期、地方政策若无PIT源均UNKNOWN；过去涨幅不冒充估值/Price-In。

## 8 Benchmark与执行

自身被动持有为主要分布对照，不把它当alpha；行业及QQQ与SPY比较，US利率/商品与BIL比较，仅在同币种同入/出session可对齐时。美国另保留50/50 SPY/BIL、60/40和70/30 SPY/IEF固定初始比例对照；只研究分布，不救活旧切换。海外宽基只报告当地价格指数，非可交易总回报，缺当地现金/FX时超额UNKNOWN，不用美元BIL伪造对照。固定每leg25bp假设，无费用优化。provider分红ex-date再投资是经济回报，非payment-date实盘；指数价格仅描述，最高LEVEL1。

## 9–10 缺失与排除

253已知历史价格以下不能计算r252/回撤/新决策feature；504以下vol相对组UNKNOWN但其余变量不删除。未成熟前瞻标签null，不当零/失败。原供应商vintage缺失标RECONSTRUCTED_NOT_ARCHIVED；只做遮蔽重构，不宣称真盲。未知公司行动、未验证拆分、重复日期、错误OHLC、特殊分拆、无可靠时间/价格单位时整个工具隔离，不能按赢家年份放行。新下载失败固定回退已有同工具冻结源（日期不延长），保留缺失起始年份；禁止用结果选数据源。

Yahoo chart为固定主源。指数可固定备用Stooq原指数数据或中国Sina官方指数展示接口；ETF不使用无行动证明备用价。每来源按原字节、URL、访问时间、SHA、频率、现值修订风险保存。不更改任何既有canonical、A/B、锁或282结果。可访问并非证明可靠。

## 11 Validation

逐资产/市场/行业、预定年代2000–09/2010–19/2020–25报告所有变量与六期限，坏结果与负对照全保存。每组N/均值/中位数/胜率/P25/P75/P10/P90/平均及最差MDD、同执行基准差（可用时）。联合按同季度、同年度聚类；500次固定seed20261009的两年calendar块重采样，全部资产同块，描述95%区间。组间差可用日期等权聚合；混合当地币收益不是可投资组合或alpha。样本少于4块区间标不可靠。

按实际entry/exit贪心取每资产最早起点的无重叠子样本，不读取收益选择；主12m、次24m。Q4只是辅助固定稀疏切片，不保证252session精确不重叠。N_effective保持null，同时列日期簇、年份、两年块、实际无重叠数与common global regime限制。不用p-value作唯一判断，不升级描述胜率。

## 12 Holdout / 暴露隔离

旧已看过2003–2025若干日期和2002以后的完整价格路径，见PRIOR_EXPOSURE_REVIEW；2000–15不能整体冒充external OOS。新季度feature在任何标签计算之前锁；2016–23为development/context，2000–15为PREREGISTERED_CROSS_TIME_RECONSTRUCTION，2024–25为COMPUTATIONAL_LATER_LABEL_HOLDOUT_WITH_PRIOR_PATH_EXPOSURE。先完成≤2023统计并锁结果，再一次揭晓2024–25，不能退回改协议。与旧asset/calendar-quarter重合单独标ALREADY_USED；只增加新面板，不修改旧结果。

真正LIVE FORWARD TEST：协议冻结日期2026-10-09起，第一次月末2026-10-30，后续每月最后完整观察交易日。月末未到时只有PENDING_DECISION记录，禁止填预测。框架无已验证edge，不临时造规则；记录冻结研究决策NO_RESEARCH_TRADE/benchmark-only、已知三个变量/合格发布及其源、后续六期限。需当月真实捕获源快照；缺当时捕获不后填为live。提供执行脚本，不宣称无人值守定时器已安装。

## LEVEL A / LEVEL B

A为2704固定格。B另以同一面板索引：八行业代理（XLK/SOXX/KBE/XLI/XLY/XLV/XLE/XLU）每年Q2，五宽基（SPY/SSE/HSI/N225/STOXX50E）偶数年Q4，共273预选案例。不看结果选择；缺失仍列索引。每dossier分KNOWN_AT_T/KNOWN_ONLY_AFTER_T、正反证、未知、失效边界、source/hash与所有六期限。价格完整dossier不自动叫完整经济机制案例；分别统计有原信用上下文/无基本面/缺历史的质量级别，不能用文本篇数宣称150条机制已识别。

## 停止与下一cycle

主面板后优先攻击候选：大跌后差异是否在共同日期/非重叠/同风险基准下存活，再检验信用能否区分；只加经济二元问题且服从上述门槛。无资格变量和关键资料不足时明确RESEARCH_BLOCKED_BY_DATA_REQUIREMENT，不调参。每主要阶段保存checkpoint、失败、多重检验与永久状态。最高投资结论LEVEL1/2，无独立未来证据不新增投资原则。
