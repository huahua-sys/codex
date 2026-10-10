# Phase 4 行为事件抽样与分析协议 v001

锁定范围：美国、中国、日本。研究对象为参与者行为/约束，不是价格筛选。不更改旧研究结果。

1. MODE=EXPLORATORY_SOURCE_FIRST_EVENT_STUDY，不称历史盲测/因果识别/未来OOS。
2. 固定档期2008-01-01至2025-12-31；制度文献可涵盖更早/更晚，但不并入收益样本。
3. 每市场核心族：US=银行贷款标准、央行流动性执行、监管/资金约束、公司资本分配、被动/基金资金；CN=央行执行、保险配置、融资融券、政策性/国家资本、公司/产业资金；JP=BOJ、GPIF、外国投资者、治理/交叉持股、公司资本分配。
4. 每族优先用官方有日期原发布目录；按日期排序，最多10个事件，以等序位位置floor(i*(n-1)/9),i=0..9抽取；不足10全收。不按未来涨跌/知名度选。目录不完整时写PARTIAL_CATALOG，所有检索/失败候选保留。禁止用标题含危机/赢家筛选。
5. 行为事件=实际执行/持仓或融资变化/规则生效；语言、额度、目标配置另标ANNOUNCEMENT_ONLY或MANDATE_CHANGE，不能冒充已买入或现金流。相同项目不同发布可作进程记录但计同parent_episode，不能膨胀独立N。
6. 优先100–200条高信息密度记录；数量不是准入理由。每族3–10条为目标而非强制。若有日期/原源/行动不足，保存缺失槽，不填估计数。
7. 每个事件先保存source URL、原字节SHA、发布日期证据、available_at与已知/未知、主体、约束、实际行动、规模/持续性及其未知，再锁事件集，之后新计算价格反应。历史结果可能模型记忆已知，永久EXPLORATORY。
8. 不明发布时间=POINT_IN_TIME_UNCERTAIN；完全排除量化事件研究。仅日期有证据：available_at为当地公布日23:59:59的保守上界；下一交易日开盘买入，不冒充精确时刻。公告与生效日期分离，后者不能取代早已公开信息日期。
9. 预定关联资产：US央行/银行=SPY，国债流动性=TLT且SPY辅助；CN宽基政策=SHCOMP，HK为仅预定辅助HSI；JP=TOPIX(已有可靠源则用)，否则NIKKEI。只有同一实际可比价格定义可配对。不增新资产救结果，缺失保留。
10. 期限固定1w/1m/3m/6m/12m，24m仅slow-money辅助。日历周/月，入场为available_at之后第一当地有效交易日open，退出为入场+期限后首个有效close；无open则NOT_EXECUTION_IDENTIFIED，不偷偷改close入场。采用原现有价格源，不修改冻结数据。
11. 主要结果：3m本地价格反应(非总回报/非可执行alpha)，1w/1m/6m/12m辅助。记录before-T趋势、当地benchmark、统一20bp往返示意敏感性；无费用/FX/分红/可交易工具等不称净可交易优势。
12. 对照：同资产每季度首交易日候选，±1年时间范围，基于T前63session回报与63session波动的标准化欧氏距离；两变量且不优化。剔除距同族事件30天以内的控制日；选3近邻不重复，固定tie date升序。季度对照可能受未观测事件污染，不能当因果反事实。
13. 同日期/同政策项目/同global危机聚类；RAW记录、unique parent/date/year、实际whole-period nonoverlap子样本同时报告。年度簇bootstrap 2000次seed4102026，至少8年且8parent才出区间；否则INSUFFICIENT_CLUSTER_CI。
14. 预定义机制假说最多5：H-P4-001 holder-only liquidation；H-P4-002 slow mandate implementation；H-P4-003 actual spending vs statement；H-P4-004 collateral/funding reflexivity；H-P4-005 capital-cycle profit capture。缺发行预期/资产偿付/实流时NOT_IDENTIFIED，不能用涨跌倒推机制。
15. 所有反例/失败/零效果保留；success为正相对反应、failure负、neutral abs差<2pp仅描述，不用于选样。跨市场比较机制边界，不强求具体阈值可复制。
16. 只建立人工决策问题树，不统一评分/自动BUY，最高LEVEL2/3非操作；CURRENT_FRAMEWORK操作字段不因漂亮故事更新。
17. 首轮结束写全部核心文档、原始source索引、事件与evidence卡、代码/schema/QA/checkpoint；核心包尽量<10MB，原完整135MB ZIP与旧锁不可改。
