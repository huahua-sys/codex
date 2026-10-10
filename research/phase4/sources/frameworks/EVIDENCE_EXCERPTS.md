# 机制文件取源摘录与用途

抓取日2026-10-10；由fetch_framework_sources.py与fetch_framework_source_addenda.py保存原bytes、提取文本、SHA。原始来源/URL见FRAMEWORK_SOURCE_LEDGER.v002.json。**本目录全部REFERENCE_ONLY；历史事件准入0；历史收益标签0；概率预测0。** 原网页当前出现2026内容不进入2008–2025的T。日期hint不是发布时间认证；原bytes哈希不是原年代第三方见证。

|来源ID|原证据最短摘录 / 核验|能支持的解释|不能支持|
|---|---|---|---|
|FW01 SEC T+1|“May 28, 2024”及“T+1”|证券结算那次制度变更与日期|所有资产统一T+1、历史收益机会|
|FW02 / FW03 SEC clearing|“Dec. 31, 2026”及“June 30, 2027”|当前核验到相关现金/repo合规期限|已经全部实施、旧事件当时已知新期限|
|FW04 SEC 13F|“45 days”及“short positions”|报告时滞/空头口径的边界|已披露完整净头寸或季度末实时交易|
|FW05 SEC insiders|“two business days”|多数相关交易法定披露期限|内部人全部交易时刻公开、真实方向必正确|
|FW06 CFTC|“previous Tuesday”及“Friday”|观察日与发布日区别|所有周五准时无特殊延发|
|FW07 / FW08 Dealer|OFR：“prior week”“Thursday”；NYFed静态页部分动态细节未显示|周频聚合、发布惯例与部分覆盖|当前全市场库存/逐户强卖；不能用空提取字段补数|
|FW09 Fed 2021回顾|“$148 billion”与“$173 billion”对应不同估计对象|现金美债/basis估计须区分对象，且是事后资料|2020-03当时已知量、唯一因果驱动|
|FW10 Fed 2025论文|“we do not find evidence”与“Treasury futures market”|对basis traders驱动期货扰动的强归因提出反证|现金市场未发生抛售、所有融资压力不存在|
|FW11 NBER fire-sales背景|“mutual fund transactions caused by capital flows”|外部既有机制研究；不是本项目重复验证|免费可执行alpha、今日本lab样本与成功率|
|FW12 BOJ2024|“discontinue these purchases”|停止新增ETF/J-REIT购买|立即出售所有持仓|
|FW13 BOJ2025|“330 billion yen per year”“book value”|宣布的出售节奏/账面口径，允许调节暂停|实际日净卖量、同量市场价值或方向预测|
|FW14 GPIF current|2025-04-01起适用；四项原表各25%，容忍带变化|目标/容忍带与实施日期；目标不变也有约束变化|25%AUM为新增订单、已越界或已成交|
|FW15 / FW16 JPX|cash investor类别周报与derivatives publication guide是不同产品|cash/derivatives范围不能互换|用期货release time回填cash发布时间|
|FW17 CSRC2024|“再贷款首期额度3000亿元”|政策额度/贷款与回购执行分层|3000亿实际买单或必然涨|
|FW18 CSRC2024|原发布日期2024-07-10；7月11转融券暂停，7月22融券保证金调整|历史业务/借券边界变更|今日全部融券禁令；当前完整法律确认|
|FW19 SSE2026|2026-01-19生效，“现行有效”，最低100%；旧合约及展期原规则|确认本交易所新融资边界及grandfathering|全部旧合约立即追保，等同维持担保最低比例|
|FW20 SSE2023|100%→80%；2023-09-08收市后|旧时点规则|今天新融资仍默认80%|
|FW21 / FW26 HKEX|FW21 PDF日期12/04/2024，季后第5北向交易日；FW26日期26 July 2024，19 August 2024实施|公布/实施/可观察数据分段|旧实时信息如今无间断；数据少了则没有交易|
|FW22 Treasury|当前page Last Updated 10/09/2026，auction announced/auctioned分开|定义页可以含未来券期而非未来结果；这是当前参考|每一历史拍卖发布时间、原vintage|
|FW23 FINRA / FW24 SLOOS|月度margin定义、季度贷款调查|余额/贷款调查各自覆盖/滞后|全账户杠杆或信用不收紧就安全|
|FW25 / FW27 BOJ2026|Jan16原PDF：“outstanding balance of ETF lending has reached zero”|ETF借出归零，废止其现金担保规则|持有ETF全卖光；2025-09当时已知2026余额|

工程失败保留：第一次执行脚本因系统Python没有requests退出，未写ledger；脚本改用标准库urllib后固定列表抓取成功，不影响任何研究值。FW21日期hint更正在v002追加，v001原文件完整保留；不是删除反例。先抓27参考来源不等于27实际投资行为事件，期货反证论文与火售论文不能计事件样本。
