# Phase 4 独立 QA 的含义与边界

本检查程序是 `scripts/phase4_independent_qa.py`，只读研究输入和结果，另建版本化审计收据。不导入事件研究计算器，不改原预测、事件集、原报价或未来标签。

- `INDEPENDENT_PHASE4_QA.v001.json`：preflight，9,558项通过。核验4,771个pre-Phase4文件：4,761个严格原字节、9个仅可追加文档前缀、1个framework元数据；框架9项操作字段及原完整ZIP保持原SHA。
- `INDEPENDENT_PHASE4_QA.v002.json`：events阶段，12,019项中的8项失败，原样保留。QA假定每条flow必须有独立`scope`键；日本8条回购记录其实已在`flow_duration`、单一JPX主体、`PERIOD_ACTUAL_REPURCHASE_VALUE`中明确期间/范围。这是QA adapter问题，不是金额错误、投资假设失败或原记录修改。
- `INDEPENDENT_PHASE4_QA.v003.json`：source/events/labels/statistics阶段，64,449项通过；尚未验最终ZIP。新版adapter读取上述原字段。检查115条事件、145份原字节源、原发布日期摘录与保守日期界、2,760个事件/对照价格反应，以及102个统计格和305个非正matched反例；没有修改数据。
- 最终package阶段需要新收据，另检查当时的append前缀/操作字段、补充参考源、美国公司语义errata版本链、ZIP大小/CRC与每个manifest项。不能以v003代替最终交付验收。

价格核验从原canonical报价中独立找严格晚于T的首次open与日历期限后首次close，检查close路径最大回撤/MAE/MFE；不是只用结果声明的日期回算。对照从季度首交易日、固定窗口与63-session两变量重新计算最近邻排序。统计核验重算全格分布、真正unique parent/年度簇门槛和bootstrap，保留缺失/失败格；不寻找最佳参数。

工程PASS不等于因果PASS。哈希不证明当时公开；日期证据不证明今日托管字节在历史时点完全相同；模型可能已记得历史；原报价是今日重构。宽基同资产不同时点对照不是参与者微观反事实，未控制原估值、信用与预期；不能据此声称forced sale错杀、慢反应、价格未计入或可交易alpha。RAW N、parent、date、year和nonoverlap覆盖均不等于独立N。

美国公司现金行与实际公开市场回购量尤其需要区分。2009现金流行$22m与原文无常规季度回购并存，交易类别桥接未识别；v002语义补记只收窄说明，不改事件日期、金额、抽样、原全局v001或价格标签。
