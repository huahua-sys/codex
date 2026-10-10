# ROUND_002 价格和公司行动准入说明

本文件是数据管理员的口径检查，不是投资信号或未来收益分析。未计算任何 forward return。

Yahoo 历史表对 Close 的原文说明为“Close price adjusted for splits”。[Yahoo 原始表](https://finance.yahoo.com/quote/AAPL/history/)与[调整方法说明](https://help.yahoo.com/kb/SLN28256.html)说明必须区分拆股调整与含分红调整的 Adj Close。下载器不读取 Adj Close 作为信号。当前 OHLC 被当作拆股归一化的价格；普通已确认拆股可在管理员侧以之后拆股比例乘回当时经济单位，然后研究模块只看 cutoff 前价格和行动。

这类机械还原不会恢复当年供应商原始发布版本。供应商更正、回填和未披露调整仍可能存在。源 JSON 原样保存及哈希只固定此次下载版本。`KNOWN_MARKET_OBSERVATION_RECONSTRUCTED` 与 `KNOWN_CORPORATE_ACTION_RECONSTRUCTED` 不等于原始 vintage 已核验。

核心 SPY、恒生、日经在请求历史区间没有供应商报告的拆股，因此没有因之后拆股而改变其 OHLC；SPY 分红保留 ex-date 记录。指数标签只报告本币价格表现，不宣称可直接交易或总回报。SPY 的 `COMPLETE` 行动覆盖仅指 API 被要求返回整个价格区间的 dividend/split 事件，未由交易所档案独立核验。

SOXX 的普通 3:1 拆股有[SEC 原始 497 文件](https://www.sec.gov/Archives/edgar/data/1100663/000119312523298660/d611816d497.htm)与[发行人税务行动文件](https://www.ishares.com/us/literature/tax-information/form-8937-ishares-semiconductor-etf-3-6-2024.pdf)支持。交易单位变更发生在 2024-03-07 开盘；record date、支付执行日与交易单位变更日不同。该网页文档日期不被冒充为 filing timestamp，不用于新增历史新闻信号。普通股数调整可进入独立口径测试，现金分红还原仍需核对。

XLK、XLE、XLY、XLU 的普通 2:1 拆股于 2025-12-05 开盘生效，与[发行人官方公告](https://investors.statestreet.com/investor-news-events/press-releases/news-details/2025/State-Street-Investment-Management-Announces-Share-Splits-for-Five-Select-Sector-SPDR-ETFs/default.aspx)一致。Yahoo 事件的比例和交易单位变更日均匹配。管理员用这些事后行动还原原有股数单位，不能将未来事件本身交给 Stage A 当作消息或信号。普通拆股的比例与生效日核验通过后，允许 `CONDITIONAL_PROVIDER_REPORTED_TOTAL_RETURN_EXDATE_REINVESTMENT`：这仍依赖供应商分红额的拆股归一化惯例与行动覆盖，逐笔现金额和支付日没有独立核对，不升级成精确可实现账户回报。

XLF 在 2016 年向持有人分派 XLRE 股份，是 in-kind spin-off，见[SEC 原始文件](https://www.sec.gov/Archives/edgar/data/1064641/000119312516699787/d246445d497.htm)。供应商可能以 pseudo-split 表示价格调整，这不能解释为持有人 XLF 股数按同一比例增加。只删除 2016 附近交易日不能消除更早 OHLC 被倒调的风险。当前下载器将整个 XLF 资料包的价格和行动隔离为 `POINT_IN_TIME_UNCERTAIN` / `DATA_REQUIRED_XLF_SPINOFF_RECONCILIATION`，不纳入实证预测，也不以此制造金融行业验证。下一轮须核对原始未调整报价、分派现金等价或真实 XLRE 持仓，再限定可恢复区间。

BIL 有 2017-11-30 交易单位生效的 1:2 普通反向拆股，Yahoo ratio 为 0.5。[发行人撰写的 2017-11-15 新闻稿转载](https://www.streetinsider.com/Press%2BReleases/State%2BStreet%2BGlobal%2BAdvisors%2BAnnounces%2BETF%2BShare%2BSplits/13511071.html)明确交易生效日期；[基金正式 Financial Highlights 的银行镜像](https://www.feib.com.tw/upload/wealthmanagement/pdf/ETFs/Y444.pdf) PDF 第 169 页记录普通 1-for-2 reverse share split，法定执行日期 11 月 29 日，与次日交易单位变更一致。原始 Business Wire URL 在本工具不可访问，因此证据等级如实写发行人文件转载/镜像，不冒充已下载原始发行人网页。BIL 可作条件化的含分红短债总回报基准；它不是无风险零波动现金，费用在 ETF 价格中，不再重复扣管理费。股息 ex-date 收盘再投资与发行人支付日 NAV 再投资的账户结果会有差异。2007-05-30 之前本来源没有 BIL 交易数据，不用今天的基金回报补齐不存在的历史。

交易时钟按市场时区的正常时段构造。US/HK 半日的 close 字段采用正常全日收盘的保守上界，所有 available_at 为下一当地日 00:00，不把 Yahoo bar timestamp（通常为开盘）当作完整 OHLC 的公开时点。这个方法保守延迟已观察到的市场报价，但不证明完整的历史交易日历、停牌或精确执行条件。Volume 单位未独立核验，不用于信号。

上述链接于本轮经网页查询读取；正文保存的是管理员解释与来源定位，不是经逐字比对的完整原始公告副本。精确公告披露时刻与公司行动原始文件仍可继续下载核验，不补入未知时间。
