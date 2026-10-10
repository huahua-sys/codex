# 美国边际玩家地图（Phase 4 v001）

这十类是“若其约束绑定，会改变定价机制”的研究优先对象，**不是按美元规模/净flow/预测胜率排序的实证Top 10**。最大持有人不自动是边际交易者；本轮缺每类同时点净交易数据，没有推算剩余资金、主观概率或建议仓位。全22类20约束字段见MARKET_ECOLOGY_US.md。

|候选边际玩家|约束|何时主导/成为forced|可能时间尺度|机会与危险边界|原源|
|---|---|---|---|---|---|
|开放式基金赎回|现金缓冲与可日赎回负债|现金不足后的资产出售；需先看持有资产是否坏|天到周；公开flow有滞后|暂无真实净赎回/被卖篮子，不可交易|[SEC_OPENEND](https://www.sec.gov/newsroom/press-releases/2016-215)|
|杠杆Hedge/Basis投资者|repo/prime融资、haircut、margin与risk budget|抵押跌/借款不续作→减仓，非看空判断|小时到周；周级持续性需证明|leveraged holder可能与发行人共同credit恶化|[FED_FSR_2025_PDF](https://www.federalreserve.gov/publications/files/financial-stability-report-20251107.pdf)|
|Dealer/做市资产负债表|库存、交割、融资及杠杆约束|无法承接库存时，价格影响同样卖量可放大|日到周|dealer统计滞后，不能推各桌风险空间|[NYFED_DEALERS](https://www.newyorkfed.org/markets/pridealers_policies)|
|ETF/AP与被动调仓|跟踪/创建赎回篮子与AP资金分开|基准变更有执行期限，in-kind链条需识别|日到月，公开日程可能早price-in|ETF二级成交非基金净flow|[SEC_ETF](https://www.sec.gov/newsroom/press-releases/2019-190)|
|Fed融资执行|法定工具/抵押品/资格、政策职责|授标支持资金，但未证明现金已进股市|隔夜到数月期限|工具使用是风险响应；TDF方向与TAF相反|[FED_SRF](https://www.federalreserve.gov/monetarypolicy/standing-overnight-repurchase-agreement-facility.htm)|
|商业银行贷款供给|存款、资本、实际借款人风险|收缩传融资和现金流，可能是结构恶化|季度报告/贷款到期更长|SLOOS不识别强卖，更不证明资产fine|[FED_FSR_2025_PDF](https://www.federalreserve.gov/publications/files/financial-stability-report-20251107.pdf)|
|公司资本分配|现金流、债务、实际资本支出与回购授权|已执行和未执行要区分；净稀释影响利润capture|季度到多年|贵买、薪酬抵消和capex供给膨胀|[SEC_10B18](https://www.sec.gov/rules-regulations/2003/11/purchases-certain-equity-securities-issuer-others)|
|DB养老金再平衡|养老金给付/负债久期、政策配置带|权重偏离可迫使反向交易，也可被给付抵消|月到多年|持仓存量不等于再平衡买单；公共/公司分开|[PBGC](https://www.pbgc.gov/about/how-pbgc-operates)|
|寿险/年金资金|ALM、资本/评级与退保负债|长期缴费支持慢配置；退保使慢钱加速卖|月到多年|买入是负债匹配而非方向alpha|[NAIC_RBC](https://content.naic.org/insurance-topics/risk-based-capital)|
|现金管理/MMF|每日可赎回负债与短期资产/费用规则|净赎回通过CP/资金市场传导；高利率也吸引申购|日到月|MMF增长不等于股票被动卖出|[OFR_MM](https://www.financialresearch.gov/money-market-funds/)|

## 需要读的实际脚印，而非聪明钱崇拜

本轮有时间来源的US动作42条；不存在实证排名。TAF/TDF只有2个操作parent，公司9记录只有1个issuer，23 parent也不等于23独立worlds。尚未采到原始公开时点净赎回、基金实际被卖证券、养老金实际再平衡/责任负债与每位发行人偿付的联立样本。

优先次序：①先验证是否真有holder被迫约束（净赎回/资金到期/抵押追缴）；②查融资方/资产现金流有没有同样坏；③识别尚未执行金额与规则持续性；④看公告前预期和估值；⑤只研究首次可交易open以后仍持续至少一周的反应。此路径是人类核查问题树，不是统一评分、股票买卖信号或已成立投资原则。

新线索：操作总额度、授标、交割、rollover与净增量是四种不同信息；真实执行也可能仅替换融资。**资金行为什么都发生了，但没有改变边际风险承受空间**是必须保留的失败路径。研究H-P4-004时应把“binding constraint是否真的解除”作为先于价格的机制证据；目前NOT_IDENTIFIED。

所有当前制度引用只用于生态地图。2025 FSR的历史回顾未用于2008/2020 cutoff。SEC2022 index-provider信息征询不是已通过的统一监管；TARP历史救助不是持续美国国家队；旧回购制度要另外核查今天修订状态。
