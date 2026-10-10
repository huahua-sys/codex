# 资料清单

> 当前Phase2状态：374成熟12m、377有效预测；没有通用/条件性优势证据，原15机制仍未测试。以下首段零资料/零执行等陈述为ROUND_001历史快照；本文件末尾是最新追加记录。
审计 ID：AUD-001；审计日：2026-10-08（UTC）。初始证据见 [INITIAL_SCAN.json](research/audit/INITIAL_SCAN.json)，来源登记见 [SOURCE_MANIFEST.json](data/manifests/SOURCE_MANIFEST.json)。本文件只描述本轮开始前可访问的项目资料，后续生成的模板、方案和状态文件不计为历史证据。

## 范围与实际发现

完整遍历 `/workspace`，排除本轮新建的 `investment-research-lab/`；检查明确附带的文件。原工作区有 **0 个普通文件、8 个目录、0 个符号链接、0 个遍历错误**。目录为 `.agents`、`.aws`、`.codex`、`.git`、`library-files`、`scratch`、`shared`、`shared/downloads`；均无文件。没有读取凭据内容，也没有搜索未指明的外部账户或仓库。

| 来源 | 数量 / 大小 | 性质 | 市场 / 年份覆盖 | 历史公开时间 | PIT 可用性 |
|---|---|---|---|---|---|
| SRC-001：[主提示词副本](sources/Codex_Investment_Research_Lab_Master_Prompt_v3.md) | 1 文件；27,597 字节 | 研究指令，非观测数据 | 无 | 无 | 不能用于历史判断或标签 |
| 价格、成交、分红、复权、退市回报 | 0 文件；0 已观察记录 | 未提供 | 未知 | 未提供 | DATA REQUIRED |
| 历史新闻、政策与执行公告 | 0 文件；0 已观察记录 | 未提供 | 未知 | 未提供 | POINT-IN-TIME DATA REQUIRED |
| 财报、公告、盈利预测及其版本 | 0 文件；0 已观察记录 | 未提供 | 未知 | 未提供 | POINT-IN-TIME DATA REQUIRED |
| ETF、基金净值、费用、历史持仓 | 0 文件；0 已观察记录 | 未提供 | 未知 | 未提供 | DATA REQUIRED |
| 宏观数据初值 / 修订版本、利率、信用 | 0 文件；0 已观察记录 | 未提供 | 未知 | 未提供 | POINT-IN-TIME DATA REQUIRED |
| 退市证券、历史成分、交易日历、停牌信息 | 0 文件；0 已观察记录 | 未提供 | 未知 | 未提供 | DATA REQUIRED |

“0 已观察记录”表示本轮没有这些数据，不代表整个市场不存在数据。主提示词的 SHA-256 为 `4d165d66b77d021325b9c96909433d044f10b818b8cf74796bfb205c2e0c13bb`。本地修改时间、上传时间和审计时间均不证明历史公开时间。

## 质量与用途判断

SRC-001 可读取、UTF-8 编码、原文副本一致；仅能建立研究约束与待验证方向。没有可运行缺失率、重复率、收益分布或校准计算的结构化样本；这些质量指标是 **N/A，非 0%**。

无法核对任何历史信号的首次公开时间、当时版本、投资者可获得时间、实体历史、财报重述、宏观修订或退市覆盖。不能据此建立真实成功、失败、无结果或反向案例，也不能把常识、模型记忆或今天网页内容当作当时证据。

## 最小下一批资料

先补齐一个可核验市场、一个连续时间区间、一个公开来源，避免一次扩展所有资产。具体区间在实际文件到位后、查看结果前确定。

1. 当时可投资证券池及上市 / 退市 / 成分有效区间，稳定证券 ID、交易日历、币种、停牌与可交易性。
2. 同期价格、分红及公司行动、现金和市场基准；完整覆盖预登记前向期限，并有来源与调整方法。总回报标签可在锁定后由评估者读取。
3. 至少一类原始历史披露，含内容、首次发布时间与时区、当时版本和可获取时间证据；同一期历史估值与预期数据用于 Price-In 判断。
4. 已知资料缺口、退市处理、费用 / 滑点假设及适用范围。

基础回放不能因复杂字段缺失无限推迟，但必须缩小问题：没有历史一致预期则不检验盈利修正；没有资金流则不解释 forced selling；没有宏观 vintage 则不声称当时已识别经济拐点。各实验的附加字段见 [研究路线图](RESEARCH_ROADMAP.md)。

结论：**INSUFFICIENT EVIDENCE**；真实历史复盘需要 **POINT-IN-TIME DATA REQUIRED**。这是数据阻塞，不是投资假设被证伪。

## ROUND_002 当前真实小数据包（取代首轮零数据状态）

当前原始报价属于今天下载的重构历史，不是历史vendor快照。根HTTP200已实测，API没有凭据要求。19个固定ETF/指数source，下载范围按预先定义，不扩大证券池；CSI300/CHINEXT历史不可用，XLF分拆口径隔离。

|Asset|Market|Currency|Rows|Start|End|Conditional TR eligible|Provider splits|
|---|---|---|---:|---|---|---|---:|
|BIL|US|USD|4871|2007-05-30|2026-10-07|True|1|
|CHINEXT|CN|CNY|1|2026-10-08|2026-10-08|False|0|
|CSI300|CN|CNY|1|2026-10-08|2026-10-08|False|0|
|GLD|US|USD|5505|2004-11-18|2026-10-07|True|0|
|HSI|HK|HKD|6104|2002-01-02|2026-10-07|False|0|
|IEF|US|USD|6087|2002-07-30|2026-10-07|True|0|
|N225|JP|JPY|6060|2002-01-04|2026-10-07|False|0|
|QQQ|US|USD|6231|2002-01-02|2026-10-07|True|0|
|SOXX|US|USD|6231|2002-01-02|2026-10-07|True|1|
|SPY|US|USD|6231|2002-01-02|2026-10-07|True|0|
|SSE|CN|CNY|4063|2010-01-04|2026-09-30|False|0|
|UUP|US|USD|4933|2007-03-01|2026-10-07|True|0|
|XLE|US|USD|6231|2002-01-02|2026-10-07|True|1|
|XLF|US|USD|6231|2002-01-02|2026-10-07|False|1|
|XLI|US|USD|6231|2002-01-02|2026-10-07|True|0|
|XLK|US|USD|6231|2002-01-02|2026-10-07|True|1|
|XLU|US|USD|6231|2002-01-02|2026-10-07|True|1|
|XLV|US|USD|6231|2002-01-02|2026-10-07|True|0|
|XLY|US|USD|6231|2002-01-02|2026-10-07|True|1|

16个官方原发布（8FOMC+8CPI，2016–23）带实际发布日/时刻与SHA，CPI观察期不是发布日。价格可用性采用明确保守会话推导，original vintage未验证；不得标为完整严格PIT。无AdjClose参与features/labels。ETF费用已嵌入价格；分红经济除息日再投资、非付款日执行。split单位已核，现金股息未逐笔对照，所有TR是CONDITIONAL_PROVIDER_REPORTED。

SEC companyfacts/submissions MSFT成功访问但未以filed/财年作为已验证原值；两原10-Kpilot正在逐原档核验，未准入研究。ALFREDvintagedates请求503；Treasury一个候选URL404，都不是整个来源耗尽。历史信用/估值/一致预期/宽度/资金流/历史成分仍DATA_REQUIRED。来源与偏差见DATA_SOURCE_CATALOG，分拆审计见research/audit/ROUND_002_PRICE_ADJUSTMENT_LIMITS.md。

## SEC pilot最终准入

两份MSFT2016/2023原10-K共8原事实核验完成，accepted时刻+次日本地00:00保守可用性，非earliest earnings release。原namespace/context/USD/scale/来源SHA可追溯；不是8个投资样本。companyfacts后续accession数值继续隔离，未核2018原文/原因。最小字段清单不是已验证JSON Schema，入engine还需要单独adapter。


## Phase3增量库存

24实际Yahoo市场源成功、26计划/23准入；2000–2025固定季度2704格/2113feature。CSI300/CHINEXT无完整历史，XLF全期隔离，STOXX50E起2007不补早期；DAXperformance口径明确。QQQ2000普通split有Nasdaq作者press wire证明但不是原托管历史快照。全部原响应、canonical、manifest/SHA单独在research/phase3/data/market与action_proof，旧source不改。

SLOOS104regular原表，85可确认发布时间/19uncertain隔离；78PDF精确release ET/7官方calendar date-only，v002统一published_at精度但value/available保持，原人数推net非当年FRED修订series。原字节293+derived98全部来源引用与hash核验；2000–2003不能准入信用。变量仅US，不移植海外。

273deep dossier中249price、184price+原credit且均缺fundamentals。新增估值/原一致预期revision/行业CapEx与融资链0；独立N未知，不将273文本当机制证据。
