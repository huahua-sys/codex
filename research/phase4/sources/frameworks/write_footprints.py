#!/usr/bin/env python3
"""Author a measurement catalogue, not a dataset or an investment score."""
from pathlib import Path
root=Path(__file__).resolve().parents[4]
rows=[
('ETF flows / 申赎','US/CN/JP；基金官网份额、申赎篮子；原持续历史快照尚未完整取得',[
'若原每日份额/篮子公开，可日频；须证明发布时间，不能用今日重构序列冒充旧快照',
'原基金披露较可靠于“份额”，不证明AP最终方向或全部底层成交',
'逐基金/逐share class；漏掉关闭工具与非挂牌资金需列明',
'按基金原发布时间；UNKNOWN不得假设当天收盘前',
'拆股、并类、公司行动、纠错；保留当日版本',
'低至中：披露有约束，但阶段申赎/套利/对冲可使方向解读失真',
'净份额变化×同日NAV仅是近似净申赎估值，非gross订单；in-kind赎回非自动现金卖股',
'适合研究残余边际需求；二级市场成交量不能替代净申赎']),
('Fund flows / 基金净流','US/CN/JP；原基金现金流、监管/行业统计；连续PIT数据DATA_REQUIRED',[
'机构可能周/月/季汇总，不假设实时', '会计核对后的现金流可强；行业估算另标估算', '覆盖披露基金，不含所有私募/托管与场外资产', '每份原报告release减观察期末；无证据则UNKNOWN', '估算、分类调整、补报/修订保留版本', '中：营销选择披露与现金调度，规模不直接等于证券净交易', 'AUM变化需拆收益/FX/申赎/合并；流入不等于已买股票', '研究资金压力/缓慢委托；不能直接推出资产价格方向']),
('Mutual fund redemptions / 共同基金赎回','主要US；原基金/监管报告；FW11为事后论文，不是赎回数据',[
'实际支付与赎回请求区分；公开及时性由原文件决定', '原现金支付/份额核对较强；危机媒体传闻弱', '逐基金/持仓/类别；季度持仓可能漏卖出过程', '赎回公布/支付/持仓披露各自时滞，不能互换', '后补报、调整与合并；不采用全样本修订来填T', '中：经营者选择报告；申赎也可能因信息交易', '赎回先用现金或流动资产，不能假设按比例卖所有持仓', 'holder-only强卖主要候选，但需资产未坏和卖压剩余证据']),
('Pension allocation/rebalancing / 养老金','US/CN/JP；原计划/托管披露；JP GPIF FW14',[
'目标公告可及时；实际配置报告可季/年滞后', '正式授权可信于目标，不是交易指令或聪明钱正确性', '逐制度/计划；总资产与可自由部署资金不同', '公告、生效、实际委托与持仓披露须分开', '估值、FX、策略分类、年度回顾；不倒填已执行', '低至中：官方目标难伪造，意图/净对冲仍未知', 'buffer、容忍带、现金流与衍生品允许偏离；越界才检查义务', '6–24m慢钱候选；目标不变/价变权重升不是新需求']),
('Insurance holdings / 保险持仓','US/CN/JP；保险原偿付/投资报告，完整PIT未取得',[
'通常定期报表；单公司即时公告另核', '审计/监管值较强但不可自动视为实时', '险种/主体/资产类别，隐藏对冲与受限资产', '原披露后才可用；观察期末不等于可知日', '估值/会计/分类与监管重述', '中：窗口调整和披露选择，保费并非股票下单', '负债久期/资本要求/退保决定买卖；投资上限不等于目标', '可解释低价接盘或危机卖压，必须检查负债侧']),
('Sovereign reserve changes / 储备变化','US/CN/JP；财政/央行/SAFE原发布；本轮无完整交易拆分',[
'月/季报告或公告；原发布时间待逐份核验', '官方库存可信，净交易分解不一定公开', '币种/证券覆盖有限；不含所有主权资金', '公布滞后与具体干预日分开；UNKNOWN保留', '估值、FX、再分类与更正', '低于传闻但中等解读风险；资产调仓/账面变动', '储备减少不自动为卖美元/卖美债；估值及汇率可能主导', 'FX/债券边际供需；官方非收益目标限制信念解读']),
('Treasury auctions / 国债发行与拍卖','US FW22；CN/JP需本地原拍卖公告，尚未完整取得',[
'公告、投标、结果各有时点；逐笔结果需原timestamp', '官方额度/中标结果强，投标兴趣非净需求', '具体券期、币种、发行人与primary/secondary市场', '结果在公布后使用，不能提前用issue或maturity date', 'reopening、补正与条件变更；初版保留', '低：官方结果；投标结构可被多投/策略投标影响', 'bid-to-cover不是未对冲真实需求；间接投标者≠全部外国央行', '发行改变供给/资金需求，须看现金管理、再融资与吸收能力']),
('Repo rates / 回购融资','US NYFed原操作/利率；CN/JP本地货币市场，需原发布',[
'可日频但非全部报价实时免费；历史T版本另核', '实际成交聚合较强；报价/均值不能代表每个借款人', 'overnight/term、担保品/对手方各不同；bilateral不全', '交易日与公布日区分；个别撤贷常只事后可知', '错误更正、基准方法/交易集合变化', '中：季度末窗口、交易构成改变，聚合掩盖尾部', '融资价格、可得数量、期限和haircut共同决定约束', '一周以上资金链压力；平均利率稳定不能否定追保危机']),
('Dealer inventories/financing / 券商库存','US FW07/FW08；CN/JP相同全覆盖数据未取得',[
'通常周频后公布；实际release逐期核验', '报送聚合；非完整逐笔独立审计，异常不可自动归行为', 'primary dealers而非全市场，资产分类而非全部单券', 'OFR说明通常周四发布前周；具体日历/修改另存', '补报、分类与方法变化，历史版本不可由当前表替代', '中：窗口资产调度/净额/分类，非一定故意操纵', '库存升可为吸收客户卖压或主动交易；净值变化非gross flow', '中介承接能力候选；非dealer全部资本或未来必买']),
('Credit spreads / 信用利差','三市场本地原券/指数供应商；连续原PIT spread DATA_REQUIRED',[
'报价可日频；公开/成交与历史vintage待核', '评级/期限/流动性与报价来源影响可比性', '券/行业/评级/币种；私募和银行贷款常未覆盖', '来源specific，不能凭FRED观察日期推定公开时刻', '指数成分、评级/模型和错误更正', '中：低成交/估值矩阵、成分迁移', '含违约/流动性/风险厌恶/期限，不能等同违约概率', 'holder+asset/融资反馈核验，不能统一阈值跨市场']),
('CDS / 信用保险','US/CN/JP；公开报价/成交覆盖不足，本轮DATA_REQUIRED',[
'专业源可高频，不追逐日内；原公开频率UNKNOWN', '成交较报价强；dealer报价未必可执行', '发行人、币种、期限、restructuring条款不同', '源specific并需接受/更新时间；原付费快照未取得', '合约roll、回收假设、交易修订', '中至高：稀疏报价与对手方/流动性影响', '价差可为债券对冲/套利，不直接给基本面恶化概率', '融资压力佐证；无法免费完整读取不阻止保留缺口']),
('Margin debt / 两融余额','US FINRA FW23；CN交易所原余额；JP逐券信用交易原发布',[
'US月度/CN与JP依当地报告，不能统一当日', '报送余额可靠于定义，账户内总杠杆未知', '制度覆盖账户；衍生品、场外融资、股票质押不同', '按当期原发布；FINRA月度值不是月末已知', '补报、定义变化与制度分段', '中：期末还款、净额、场外迁移', '余额下降可还款、到期、价跌；不能仅凭降余额认定forced', '压力/新杠杆供给候选；初始保证金≠维持追保比例']),
('Futures positioning / 期货持仓','三市场原交易所/OI/投资者类别，部分公共',[
'日/周依源；只研究公开后≥一周窗', 'OI/交易所聚合较强，策略意图不明', '合约/roll/账户分类；OTC和cross-hedge缺失', '交易日、settlement、公布时点分开', 'roll、重分类、纠错和OI算法', '中：跨期/跨市场套利、分类和窗口调仓', '总OI增加同时有多有空；gross不能当净看涨资金', '风险再平衡/对冲与保证金压力，需现金腿/融资腿匹配']),
('CFTC COT / 持仓分类','US FW06；不可当CN/JP所有期货参与者地图',[
'一般周五15:30 ET发布前周二snapshot；节假日/延发逐期查', '监管聚合；分类不等同真实逐笔策略', '覆盖报告门槛以上类别与指定合约，非全部现金/OTC', '通常周二→周五；用release calendar，不用周二当可知T', '更正、分类/账户转移、特殊延发', '中：策略对冲与分类误解；数据并非全部独立核验', 'leveraged funds短期货可对冲多现货；不是统一short view', 'basis/拥挤/保证金候选，季度回顾才知的识别不能提前用']),
('Short interest / 空头权益','三市场原交易所/FINRA/借贷披露；连续原档未完整取得',[
'周期snapshot与daily short-volume区分；每源待核', '报告净/毛持仓定义不同；成交量不是存量', '股票/交易所、场外/豁免和借贷可得性不全', '结算/快照与发布分开；UNKNOWN不推定', '补报/企业行动/规则与shares float更改', '中：对冲、做市、转借、可用券源变化', '高short可信息/风险对冲；short volume不能推还仓', '挤压或风险提示候选；借券约束改变套利边界']),
('Buybacks / 回购','US/CN/JP 原IR/监管；实际执行与授权分别录',[
'授权可即时；执行通常逐月/季度披露依当地规则', '实际成交/注销强于授权；公司报表仍需核对', 'gross现金与净股数、员工发行、block/ASR等', '交易/注销/披露各时点；不能在季度结束就知道全部', '更正、ASR结算与股份行动', '中：高位回购/补偿稀释/盈利指标动机', '授权是选择权；执行可政治/资本结构而非信念', '真实边际买方候选；需成本、融资、估值与净稀释']),
('Insider transactions / 内部人','US EDGAR FW05；CN/JP当地原披露，非全球同Form4',[
'US多数交易两工作日披露；真实accepted才进入T', '原交易字段较强，意图与总财富/对冲未知', '定义内officers/directors/10%等；家庭/私人仓位缺', '交易→accepted；季度SEC数据包不能代替原filing时点', 'Form4/A、transaction code、衍生品/10b5-1更正', '中：薪酬/期权/税、计划交易与信号化意图', '自费主动公开市场购股才更接近belief；仍非correctness', '周至月级候选；已公开且被套利/假信号失败必须保留']),
('Corporate issuance / 企业融资','三市场原证券/债券/IR、接受/交割披露',[
'计划、定价、交割各次信息；原时刻待核', '已完成交割/现金到账强于发行计划', '债/股/可转/担保与私募、上市主体不同', '公告与交割及资金用途披露分开', '修订条款、取消、退款与汇率', '中：融资意图包装、关联方循环与选择披露', '筹款可成长、续债或危机；摊薄影响股东回报', '资金延续和资本周期候选；融资成功不等于盈利增长']),
('CapEx / 资本支出','三市场原财报/IR/项目公告；本轮连续经营PIT缺',[
'项目宣布与季度/年度实际支付不同', '原现金/合同与施工证据较强，指引可变', '企业/资产类别、维持/成长、租赁/资产化不统一', '期末→真实财报发布日期；不能填财期末', '财报重述、分类、资产化与租赁标准', '中：指引/资本化会改善表面盈利；实际支付更难伪造', '需求强、保产或过剩都可高CapEx，行业差别关键', '6–24m供给/盈利归属；无订单与融资不能给利好结论']),
('Procurement / 政府采购','三市场原财政/采购平台/合同；完整母体DATA_REQUIRED',[
'预算/招标/授标/支付/验收分别public date', '原法律义务/支付较强，标题总额不强', '项目/受益主体、base/option、地方/中央覆盖', '每发布之后使用；签署未公开不等于可知', '变更、撤销、option未使用与退款', '中：执行选择、关联交易、虚假订单风险', '订单给谁、何时交付/收款、利润率与挤出须核', '复杂持久信息underreaction候选，不默认财政额度全利好']),
('Long-term contracts / 长约','三市场原IR/交易所/采购合同；完整原条款不足',[
'披露可能滞后签署；保密条款导致missing', '可执行最低采购/付款强于MOU或潜在额', '覆盖有披露义务合同，秘密失败合同可能漏', '首次公开/修改的timestamp；签约日不能代替', 'option、取消/违约、重谈、金额/FX修订', '中至高：MOU、关联客户/循环融资、营销标题', '名义总额×年数非当年收入；take-or-pay仍有对手方风险', '需求持久性候选，须现金兑现/资本需求/price-in']),
('Budget execution / 政府预算执行','US/CN/JP 原财政现金执行/项目披露',[
'月/季现金报告与项目支付；每源日期待核', '原现金执行强于预算意图；受益链仍待识别', '全国汇总不等于特定行业/公司增量', '观察期末到公开有lag；UNKNOWN不得用', '补报、会计口径/财政年与项目重新分类', '中：分类/预算腾挪；支出事实与受益解释分开', '授权、承诺、实际支付不同；既有预算替换可能无净增量', '政策执行H-P4-003，需要股东现金归属']),
('Strategic reserves / 战略储备','三市场能源/粮食/物资官方操作，完整量缺',[
'公告与实际释放/回补公布分别；非所有库存实时公开', '已交付/竞拍结果强于计划和传闻', '物资/地点/数量/可用质量；保密库存未覆盖', '公告后执行、库存报告后观测；UNKNOWN保持', '库存估算、质量/地点转换及更正', '中：政治目标、保密和预期管理', '库存变化也可估值/损耗；国家采购非一定price-insensitive', '资源供给/缓慢回补候选；一次政策未必长期需求']),
('Bank lending standards / 银行信贷标准','US SLOOS FW24/既有85原发布；CN/JP当地调查需各自定义',[
'季度调查；原实际release而非调查期末', '官方回答聚合可靠于样本定义，不是全信用风险', '银行、贷款类型、respondent，贷款量加权不同', '调查→发布；须原PDF/calendar，旧PIT不确定19隔离仍保留', '问卷/样本/修订；当前系列不得回填未知原期', '低至中：主观回答/样本变动，非实际全部贷款执行', '收紧代表供给/需求/风险多原因；不收紧≠安全', '融资环境背景；Phase3单变量年代翻转，不能当通用错杀过滤器']),
('Bank funding stress / 银行融资压力','US/CN/JP 原存款/融资/央行工具/银行披露',[
'操作可日/周；逐银行存款/资本报表更滞后', '实际借款/存款较强，传闻/聚合均值弱', '机构/币种/期限/抵押品，隐含担保与对手方不全', '操作/报告公布逐份可知，后验调查不能提前用', '重述、央行资产分类、并购和会计变化', '中：窗口融资/保密、tool使用有stigma或预防动机', 'backstop使用可能防御而非破产；未使用不等于无压力', '系统反身性核心候选；须存款流出/续债/抵押与经营桥梁']),
('Policy capital / 政策性及国家资本','主要CN；US/JP政府/央行用途异；原官方公告+执行',[
'意图可即时，实际净交易常部分披露或事后', '正式规则/实际交易较强，非官方“国家队”猜测弱', '工具/机构/市场边界；隐蔽托管/衍生品未知', '首公告、工具开放、取用、证券交易各日期', '额度变更、到期、资金用途与后补解释', '中：政治目标、支持预期、信号性少量行动', 'FW17额度≠实贷≠已回购；股票支持非所有公司救助', '规则影响约束更可预测，方向/正确性与退出未知']),
('Passive/index rebalancing / 指数调仓','US/CN/JP 原指数方法/变更与基金文件；完整原成分不足',[
'宣布与生效可明确；一般早知不等于剩余套利窗', '原方法/实际成分强，媒体估计净买量较弱', '具体index/fund、抽样、buffer与derivative替代', 'announcement生效前即为已知；别把effective日当首次消息', '方法/float/成分修正、缓冲与分阶段纳入', '中：front-running、指数套利/选择性估算', '纳入不等于所有跟踪者必须即时买现货；deletion仍可能主动持有', 'forced-buyer/seller机制需义务与执行量，不要求统一阈值']),
]
labels=['Timeliness / 及时性','Reliability / 可靠性','Coverage / 覆盖','Lag / 发布滞后','Revision Risk / 修订','Manipulation Risk / 操纵与策略影响','Interpretability / 可解释性','Market Relevance / 市场相关性']
intro='''# 市场脚印：看到的东西，究竟证明了什么？

Phase4 v001。以下是**27类测量定义与数据缺口**，不是28个已取得可交易信号；没有新增实盘值或主观概率。证据级别LEVEL 1。每一脚印都逐项记录八个质量维度，不能用统一分数混合。

`observation_period / action_at / published_at / available_at / fetched_at`五个字段不同。未知发布时间＝`POINT_IN_TIME_UNCERTAIN`并排除历史量化输入。只有日期，保守按当地23:59:59之后下一交易日执行；每个当前定义页不自动证明每一历史发布的可得性。

原始参考来源在`research/phase4/sources/frameworks/FRAMEWORK_SOURCE_LEDGER.v002.json`，全部标REFERENCE_ONLY、historical_event_admissible=false。FW06 CFTC、FW05 SEC、FW08 OFR、FW14 GPIF、FW17 CSRC等支持测量边界，不把今天网页中的2026数据用于历史T。

## 怎样读表

“可靠”是对所报告字段的可靠，不是对方向预测的可靠；“操纵风险”含策略行为/披露选择与误解风险，并非指控机构造假。没有具体原发布，lag/coverage仍需逐卡确认。三个市场允许相同经济机制使用不同可观测脚印。

'''
parts=[intro]
for i,(name,source,values) in enumerate(rows,1):
 parts.append(f'## FP-{i:02d} {name}\n\n市场/来源范围：{source}。\n\n|维度|解释与使用限制|\n|---|---|\n')
 for label,value in zip(labels,values): parts.append('|'+label+'|'+value+'|\n')
 parts.append('\n')
parts.append('''## 关键原来源与逐市场限制

- [CFTC release calendar](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm)：周二snapshot一般周五发布，特殊延迟不能忽略。
- [SEC 13F FAQ](https://www.sec.gov/files/divisions/investment/13ffaq.htm)及[insider disclosure](https://www.sec.gov/resources-small-businesses/going-public/officers-directors-10-shareholders)：报告与交易不同日期，披露不是完整净风险。
- [OFR primary dealer定义](https://www.financialresearch.gov/short-term-funding-monitor/datasets/nypd/)与[NYFed](https://www.newyorkfed.org/markets/counterparties/primary-dealers-statistics)：前周聚合不等于当前全部中介库存；部分详情是网页动态内容，静态抓取未完整呈现，不补造缺失字段。
- [JPX股票投资部类周报](https://www.jpx.co.jp/markets/statistics-equities/investor-type/)是cash equities范围；FW16的[derivatives publication guide](https://www.jpx.co.jp/english/markets/statistics-derivatives/sector/b5b4pj0000008ox8-att/guide-en.pdf)不能替代cash报表首次发布时间。现金和期货、foreign category和资金来源不同。
- [FINRA margin定义](https://www.finra.org/investors/learn-to-invest/advanced-investing/margin-statistics)、[Treasury auctions定义](https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/treasury-securities-auctions-data)、[Fed SLOOS](https://www.federalreserve.gov/data/sloos.htm)支持口径；历史值/发布时间要独立取得。
- 中国北向、融资/融券、政策工具规则必须按`RULE_CHANGE_MONITOR.md`分期，不能要求缺失字段仍连续可观测。日本BOJ停止新增购买、出售计划、借出归零不得混称资金流。

## 最小复现与缺失处理

下一批只需：原有日期行动文件、来源bytes/SHA与发布时间证据、主体/约束、实际净毛规模和未知、资产/融资/预期资料、现有价格定义。能得到新闻而得不到实际动作则ANNOUNCEMENT_ONLY；有动作无对照则机制描述；有事件反应无原预期则不能称underreaction。

每张Evidence Card保存来源ID、字段口径、单位/币种、已知范围、独立证据、替代解释与否证。holdings变动、AUM变动、gross成交和net现金不拼成总flow。多个官方转载属同一原源，多个资产同时受全球压力属同parent/date，报告raw与有效独立性分开。
''')
p=root/'MARKET_FOOTPRINTS.md'
if p.exists(): raise SystemExit('Refusing overwrite')
p.write_text(''.join(parts),encoding='utf-8')
print('footprints',len(rows),'path',p,'bytes',p.stat().st_size)
