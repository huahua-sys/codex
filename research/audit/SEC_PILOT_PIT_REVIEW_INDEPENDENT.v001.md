# SEC 原始披露 pilot 独立核验

核验状态：`PASS_NARROW_ORIGINAL_FACT_EXTRACTION`。离线复核两份 MSFT 原始10-K accession，八条金额全部达到本次窄范围 `VERIFIED` 门槛；没有新增投资案例、预测或原则。

| 原始财年 | 2016 | 2023 |
|---|---:|---:|
| 原始披露收入（USD） | 85,320,000,000 | 211,915,000,000 |
| 原始净利润（USD） | 16,798,000,000 | 72,361,000,000 |
| 原始营业利润（USD） | 20,182,000,000 | 88,523,000,000 |
| 现金 PP&E 支付（USD） | 8,343,000,000 | 28,107,000,000 |
| EDGAR accepted（UTC） | 2016-07-28 20:12:18 | 2023-07-27 20:01:56 |
| 保守 available_at（UTC） | 2016-07-29 04:00:00 | 2023-07-28 04:00:00 |

这两组事实可以供各自 9月30日 cutoff 使用。`published_at` 是原始EDGAR accepted时间的代理，并有下一本地日午夜的保守可用性延迟；没有证明更早的 earnings release 时点。因此不能用于精确公告时刻交易的事件研究。

核验覆盖全部八个下载来源哈希、同一原始accession、USD单位、发行人CIK、无维度合并报表context、原始起止期、概念namespace、数值scale/sign、2023 inline XBRL的 `ixt:num-dot-decimal` 格式、nil标记以及 `观察期 < accepted < available_at <= T`。2023重复事实节点金额和context一致，未重复计数。

公司facts今天的API只作locator与同accession交叉核验。FY2016净利润在2018年后续accession出现20.539bn、营业利润出现26.078bn，与原始16.798bn和20.182bn不同。后续API值被记录为 `KNOWN_ONLY_AFTER_T_LOCATOR_NOT_ORIGINAL_DOCUMENT_VERIFIED`；没有读取2018原始文档核实重述原因，也没有替换2016事实。这个例子说明，仅按财年取今天companyfacts可能把后来版本带回过去。

复用限制：这不是通用XBRL解析器认证。新的concept、inline transformation、context、unit或accepted来源必须重新核验，歧义则 `POINT_IN_TIME_UNCERTAIN`。2016与2023收入concept和会计口径不同，不能从表格直接计算可比增长。现金PP&E支付也不等于总投资承诺、融资租赁或全部AI投入。

单个幸存发行人、两份年报不能证明盈利修正、CapEx、ROIC、FCF、行业资本周期或price-in的预测价值。需要独立的事前预期、口径一致财务序列、价值分母和原始发布时间。八条事实是数据工程成果，投资假设检验数仍为零。

机器可核查证据：[独立核验JSON](SEC_PILOT_PIT_REVIEW_INDEPENDENT.v001.json)、[提取记录](SEC_PILOT_PIT_REVIEW.json)、[来源清单](../../data/manifests/ROUND_002_SEC_PILOT_SOURCES.json)。
