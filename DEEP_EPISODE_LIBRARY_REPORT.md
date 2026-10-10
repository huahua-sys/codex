# Phase3深度案例库验收

RAW OBSERVATIONS：273个规则预选dossier，八行业每年Q2及五宽基偶数年Q4。价格feature可用249、缺历史/源24；249个成熟12m，236个成熟24m。原信用+价格且缺基本面184；仅重构价格且缺基本面65；缺历史24。187篇存在原信用上下文，其中3篇价格不合格，不能把187当184完整可用案例。详见 `research/phase3/deep/dossiers.manifest.v001.json`。

EFFECTIVE SAMPLE ASSESSMENT：独立N未知；同一行业周期/美国信用报告/全球事件复用，273篇不等于273个独立世界。已识别因果机制=0，完整原估值/经营/预期/融资链机制案例=0。满足150–300篇固定起点资料整理，尚未满足150–300个完整高质量经济机制案例。

每篇严格分KNOWN_AT_T和KNOWN_ONLY_AFTER_T；A特征先统一锁、B标签后来一次揭晓，六期限保留缺失/待成熟。`labels_available=true`仅说明B容器已经生成，不说明六期限全部成熟，不说明缺价格案例有合法收益。

这些dossier是有来源的研究上下文，不是273次新Bear/Base/Bull预测；本阶段没有创造主观概率。模型历史记忆与供应商重构风险仍在，不声称真实未见未来盲测。原282与扩展374不改；新dossier与旧相同资产季度可能重合，有单独暴露标记，不能相加为独立样本。

案例入口：`research/phase3/deep/index.v001.json`和`research/phase3/deep/dossiers/`。行业解释库见INDUSTRY_MECHANISM_LIBRARY。下一批优先补原连续经营与再融资披露，而非再把同一价格状态扩写成更多故事。
