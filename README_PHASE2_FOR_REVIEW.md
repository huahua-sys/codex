# Phase2 审查入口

研究内容：延续已有Investment Research Lab，冻结失败通用择时规则，分类原282与扩展374成熟12m结果；两个经济条件、固定配置残差、placebo/扰动、Price-In与行业逻辑。

最重要结论：NO EVIDENCE OF GENERIC TIMING EDGE；NO CONDITIONAL EDGE ESTABLISHED。C1脆弱（2触发），C2只有1触发；random-date条件N0，PLACEBO_NOT_EVALUABLE。没有A级/B-/C晋升，没有新增操作性投资原则。

失败结论：原趋势先验未稳定优于固定概率；weeklySPY/BIL没有证明优于50/50、60/40、70/30。相对全股票减回撤不能冒充增量择时能力。原失败锁与记录保留。

当前候选：RETURN EDGE候选0；RRC-001只是D级相对全股票风险观察，固定50/50构成重要反证。资料不足的盈利、估值、信用、资本周期机制尚未被验证或证伪。

人工优先阅读：

1. CONDITIONAL_EDGE_REPORT.md（17个核心回答）
2. ERROR_TAXONOMY.md（False Positive / False Negative与真实缺口）
3. SURVIVING_CANDIDATES.md、FAILED_HYPOTHESES.md
4. research/phase2/conditional.interpretation.v001.md（脆弱性与发布时间边界）
5. research/phase2/benchmarks.results.v002.md（主与敏感性费用、固定配置残差）
6. REGIME_DEPENDENCE_REPORT.md、PRICE_IN_FRAMEWORK.md、INDUSTRY_SPECIFIC_RULES.md
7. SELL_FRAMEWORK.md、NO_TRADE_FRAMEWORK.md
8. NIGHT_RESEARCH_REPORT.md、research/status/LATEST.md
9. research/audit/PHASE2_QUALITY_SCIENTIFIC_REVIEW.v001.md（独立QC）

下一步：小连续信用/融资、原财务与历史预期/估值序列；固定下跌起点和负对照；补足随机日期之前的原宏观发布，不重抽直到好看。不继续调整失败通用规则。

数据/证据边界：430选择记录、377有效预测、374成熟12m、53不足历史、3待成熟12m；43日期/23年份，独立N未知。Phase2没有新增Historical Replay/概率预测。报价是当前供应商的历史重构，非原始quote vintage或真正前瞻盲测；原公告与两SEC filings另有发布时间证据。合成工程资料不算投资证据。

可复现性：本包包含全部重要报告、源字节、源清单、脚本、原预测/锁/标签、案例报告及checkpoint。避免重复存储约1.6GB行政bundle/输入，每个原文件以无损blueprint引用同一份canonical历史；所有原哈希保持不变。DATA_RESTORE_BLUEPRINTS.json不是新数据或修改过的输入。

在包根目录运行 `python3 scripts/restore_export_inputs.py --verify-only`，可不联网重构并核对全部原SHA而不写重复大文件；要恢复完整研究文件运行 `python3 scripts/restore_export_inputs.py`。已有文件只核验不覆盖。120个不合格pilot始终不准入，即使恢复也不成为合法案例。默认审查无需恢复大文件；需要运行原A/B程序前恢复，并按各原selection/prereg路径操作，原A重跑只核验不得改预测。

EXPORT_MANIFEST.json记录复制文件哈希；EXPORT_RESTORE_VERIFICATION.json记录重构验证；根目录保留原研究布局，历史ROUND001零数据快照是归档，不是当前状态。原供应商快照下载/公司行动局限详见DATA_SOURCE_CATALOG与DATA_INVENTORY。
