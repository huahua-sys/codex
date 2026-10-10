# Phase 3 原始 SLOOS 信贷供给小数据

## RAW OBSERVATIONS / EFFECTIVE SAMPLE ASSESSMENT

RAW OBSERVATIONS：104份2000–2025 regular季度原发布页、104份原国内银行Table 1。104份表可精确核算固定指标；85份同时取得合格日期证明并纳入PIT，19份时间不明，其`value=null`。有效发布日期跨22个年份（2004–2025）；2000–2003全部仍不可用，2004有2份，2007有3份，其余2005–2025年份4份。N_effective=null：银行受访池重合、季度标准变化的持续性、同一全球信用周期和受访池变化均破坏独立性。85个来源发布不是85次独立投资实验，更不能按各US资产复用次数增加N。

## 固定变量与原数值

`series_id=SLOOS_CI_LARGE_MIDDLE_NET_TIGHTENING`。使用Table 1第一问A：大型/中型企业C&I贷款标准，以及**All Respondents国内银行**列。不是Large Banks子列，不是外国分支机构Table 2。严格按原整数respondent counts核算：

`100 × (Tightened considerably + Tightened somewhat − Eased somewhat − Eased considerably) / Total`。

保留每类count、原行、原百分比和有理数分子/分母。检查五类count之和等于Total，各类count对应原百分比在0.1位四舍五入范围内。104表全部通过；不把正文“a moderate fraction”等approximate措辞转换为精确数值，也没有使用当前FRED历史替换原数值。由于原发布表以一位小数显示各类别，canonical的数值是从原整数counts精确派生的net ratio，可能与各类别已舍入百分比的直接相减略有差异；固定零阈值的净收紧方向依据整数差确定。

`value>0`意为银行过去三个月标准**净收紧**。`value≤0`仅意为没有净收紧；不能等同信用利差稳定、无违约、银行资产负债表健康或贷款需求增长。当前标准水平仍可能很紧；这是变化调查。只适用于美国银行信贷供给，不作为香港、日本、中国或欧洲本地信用代理。

## 真正发布时间

最终85条合格记录：78条使用原完整报告PDF封面的`For release at ... [date]`，7条使用官方历史calendar明确的SLOOS发布行，并与该调查原页面日期一致。所有原日期证明和source SHA均保留。

没有将调查月份、季度结束、URL年月、下载时间、PDF creation/modification metadata或Last Update单独当成公开发布日期。原页面Last Update仅用于定位历史calendar候选月份；必须独立calendar有SLOOS发布日且匹配才接受。统一采用该日之后纽约当地00:00的保守available_at。

最终使用v002：78条原PDF封面明确官方公布日与ET 2 p.m.，published_at按America/New_York时区转UTC，published_at_precision=OFFICIAL_RELEASE_STATEMENT_MINUTE。这是原官方声明的release minute，不是当年服务器日志。7条calendar日期证明的记录不假装精确实际timestamp：published_at保留date-only保守上界，precision=DATE_ONLY_CONSERVATIVE_UPPER_BOUND；publication_date保存真正已证明公开日，published_at_upper_bound单独明确保存保守上界。UNKNOWN的19条无时间。第一次v001把published_at统一放保守上界的工程语义问题保留追溯，不纳入最终A；v002只规范化字段，没有改变任何数值、available_at、85/19缺失状态或样本范围。比必要时点晚可见是允许的，绝不早于已证明公开日。

19条UNKNOWN：2000的4条、2001的4条、2002的4条、2003的4条、2004 January/July、2007 April（URL May）。早年PDF没有明确release statement，部分PDF封面字体无法正常提取。2007 April报告是May 17更正版本，明确讨论May 14初始公布和图表更正，但本轮保守标准未接受它作为原表与发布时间完全绑定的记录。不可因它能补齐信用组而偷偷放行。时间未合格的原整数表仍供后续补证审阅，但不进入信号。

## 来源与版本审计

官方`https://www.federalreserve.gov/data/sloos.htm`直接提供历史原调查链接。固定regular季度列表见release_index.v002.json，原字节、HTTP状态、访问时刻、实际redirect、实际官方href和SHA在raw/*.source.json。原table、full report和历史calendar保存为原字节`.bin`，PDF文本只是可复核派生文件。

首次URL解析遗漏2017三条迁移到`/data/sloos/YYYYMM/default.htm`的链接，且含2001 March/2020 September两份supplemental调查。纠正后每年固定4条regular调查共104；此前103条索引、中间acquisition和两份supplemental下载均保留，不纳入最终记录、不删除。此修正发生在任何市场标签读取之前。旧宽松date regex曾误匹配导航`release dates`，最终严格PDF/calendar证明不使用那个中间字段。具体源码每次执行前都登记SHA，code_registration.001–013.json保留全过程。

虽然现在获取的是官方按调查保存的原报告，并且可解析的dated完整报告counts与单独Table 1交叉核对未发现数值冲突，这仍是当前托管的历史发布，不是第三方当年原字节快照。可能存在未记录的静默更正。受访银行组成、总回应数及大型银行定义也随时间变动；使用All Respondents减少Large Banks子组定义切换，但不能消除受访池变化。不能宣布全时期完全同质。

网络实际可用。官方现代calendar可补证；所测若干旧calendar URL404仅说明这些具体URL不存在。ALFRED/FRED release191日期候选URL503，未作为数值或日期来源；不是宣布整个FRED不可用。未泛化为DATA EXHAUSTED。

## 锁与后续使用

最终credit.records.v002.json及credit.records.lock.v002.json已冻结，SHA256：`7a9ba70837a5f75f480c61ba56d03a2520ec2be2a5634849843227ad12fbce2e`。v001原哈希`bd04ddfd231801bb86eaa4e78f81eda0b8bf3abccf2e2e3d9032884ed85a33f0`保持。normalization_comparison.v002.json逐一核实104条value和available_at不变。所有原数值、日期和源均在面板特征/未来收益之前采集；本采集脚本没有读取任何价格、return或episode结果。

使用latest合格记录、available_at≤T且距T≤180天，仅US。2000–09存在21条合格原发布，2010–19存在40条，但这只说明预注册gate的数据基础，不能保证收益差同方向或投资优势。由已冻结面板执行H-P3-CREDIT单变量及其预注册二元gate。若gate失败必须NOT_RUN_GATE_FAILED，不能改年份、改零阈值或放行UNKNOWN记录。

自检acquisition.qa.v001.json核验原SHA、整数总和、net公式、aware时间与缺失状态；它是同作者工程QA，不能冒充独立科学审计。下一项最有价值数据工作是补证2000–2004早年真正发布日及当时信用利差/违约/贷款标准水平，不能用net tightening变化一个变量判断整场资产负债表危机。
