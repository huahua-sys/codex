#!/usr/bin/env python3
"""Checkpoint reports and append permanent research memory; no old experiment edits."""
import collections, hashlib, json, sys
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.phase3_analyze import rows_from_labels
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def write(p,x):
    p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(x if isinstance(x,str) else json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def append(p,x):
    with (ROOT/p).open('a') as f:f.write('\n\n'+x.rstrip()+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat(); fw=read('CURRENT_FRAMEWORK.json')
    old=read('research/phase3/audit/PRIOR_OPERATIVE_FRAMEWORK.v001.json')['operative_framework']
    assert all(fw[k]==v for k,v in old.items())
    assert not (ROOT/'research/phase3/CHECKPOINT_C3.v001.json').exists()
    points=read('research/phase3/features/decision_points.v001.json')['points'];rows=[]
    for part in ['development','holdout']:rows+=rows_from_labels(points,read(f'research/phase3/labels/{part}.v001.json'),part)
    deep=read('research/phase3/deep/dossiers.manifest.v001.json');dids={d['point_id'] for d in deep['dossiers']}
    maturity={h:sum(r['feature_eligible'] and r['label_status']=='REVEALED' for r in rows if r['horizon']==h) for h in ['1w','1m','3m','6m','12m','24m']}
    deep_maturity={h:sum(r['point_id'] in dids and r['feature_eligible'] and r['label_status']=='REVEALED' for r in rows if r['horizon']==h) for h in ['12m','24m']}
    quality=dict(collections.Counter(d['quality'] for d in deep['dossiers']))
    # All negative cases preserved, sorted by identifier, never used to select the panel.
    us=[r for r in rows if r['horizon']=='12m' and r['feature_eligible'] and r['label_status']=='REVEALED' and r['market']=='US' and r['industry'] in ['Broad','Growth','Technology','Semiconductor','Financials_Banks','Industrials','Consumer','Healthcare','Energy_Resources','Utilities']]
    bad=[r for r in us if r['groups']['H-P3-VOL']==1 and r['net_return']<0]
    missed=[r for r in us if r['groups']['H-P3-VOL']==0 and r['net_return']>.30]
    neg={'interpretation':'Descriptive negative cases, not errors of new probability forecasts. 30% is an outcome illustration, not a new signal or optimized threshold. Entire lists retained.','RAW_OBSERVATIONS':{'high_vol_negative12m':len(bad),'not_high_vol_gain_above30pct12m':len(missed)},'EFFECTIVE_SAMPLE_ASSESSMENT':{'n_effective':None,'reuses_locked_labels':True},'high_vol_negative':sorted(bad,key=lambda r:r['point_id']),'not_high_large_gain':sorted(missed,key=lambda r:r['point_id'])}
    write('research/phase3/vol_falsification/negative_case_index.v001.json',neg)
    write('DEEP_EPISODE_LIBRARY_REPORT.md',f'''# Phase3深度案例库验收

RAW OBSERVATIONS：273个规则预选dossier，八行业每年Q2及五宽基偶数年Q4。价格feature可用249、缺历史/源24；249个成熟12m，236个成熟24m。原信用+价格且缺基本面184；仅重构价格且缺基本面65；缺历史24。187篇存在原信用上下文，其中3篇价格不合格，不能把187当184完整可用案例。详见 `research/phase3/deep/dossiers.manifest.v001.json`。

EFFECTIVE SAMPLE ASSESSMENT：独立N未知；同一行业周期/美国信用报告/全球事件复用，273篇不等于273个独立世界。已识别因果机制=0，完整原估值/经营/预期/融资链机制案例=0。满足150–300篇固定起点资料整理，尚未满足150–300个完整高质量经济机制案例。

每篇严格分KNOWN_AT_T和KNOWN_ONLY_AFTER_T；A特征先统一锁、B标签后来一次揭晓，六期限保留缺失/待成熟。`labels_available=true`仅说明B容器已经生成，不说明六期限全部成熟，不说明缺价格案例有合法收益。

这些dossier是有来源的研究上下文，不是273次新Bear/Base/Bull预测；本阶段没有创造主观概率。模型历史记忆与供应商重构风险仍在，不声称真实未见未来盲测。原282与扩展374不改；新dossier与旧相同资产季度可能重合，有单独暴露标记，不能相加为独立样本。

案例入口：`research/phase3/deep/index.v001.json`和`research/phase3/deep/dossiers/`。行业解释库见INDUSTRY_MECHANISM_LIBRARY。下一批优先补原连续经营与再融资披露，而非再把同一价格状态扩写成更多故事。
''')
    write('PHASE3_SURVIVING_PRINCIPLES.md','''# Phase3存活结果：分层而不制造原则

状态：**NO ROBUST RETURN EDGE ESTABLISHED**；投资原则LEVEL3=0。本阶段新增非操作性统计候选1条，最高C=preliminary；经济机制本身仍D=idea。不救活原失败趋势/股票短债切换，不升级原15待检验候选。

RAW OBSERVATIONS：2113有效季度价格决策点、2087成熟12m、1995成熟24m；273dossier中249有价格、184同时有合格原信用。EFFECTIVE SAMPLE ASSESSMENT：独立N未知；101季度/26年共享全球周期，实际每资产全分区贪心无重叠合计480/245（12/24m），仍是相关资产行而非480/245个独立世界。

## LEVEL1 — Descriptive

1. 全样本大跌组12m均值更高但风险更大：开发期14.47% vs6.52%，平均gross MDD−23.81% vs−15.22%；日期等权差仅+1.77pp，块区间[−6.46,+8.98]pp。US同季度股票差+3.66pp、区间[−6.30,+12.98]，MDD差−7.88pp（更差）。大跌不是可验证的便宜，更不能证明错杀。
2. 正趋势组更高胜率/较浅回撤没有证明更高期望回报：开发12m日期差−.38pp、24m−5.66pp，区间跨零。同季度US股票12m−.74pp、24m−1.80pp；不能把趋势重命名为已验证确认工具。
3. 原SLOOS信用收紧不是可迁移收益过滤器：预定早两个年代12m差−8.50pp/+1.37pp，符号反转，二元信用×回撤保持NOT_RUN_GATE_FAILED。来源准入进展不等于“信用没有用”；该口径不能识别融资危机。

## LEVEL2 — PAC-P3-001 / PREDICTIVE_ASSOCIATION_ONLY

**Rule**：只登记研究关系——在固定美国股票ETF集合、同季度双组并存时，自身252session波动高于自身过去252个滚动波动中位数的组，后续12/24m平均净持有收益较高。不是买卖规则、不是更高上涨概率、不是beta调整后alpha。

**Economic mechanism**：风险补偿、周期修复、行业暴露/轮动、受限资金退出后回流都可能解释；尚无原经营/融资/持仓资料区分。相对波动是价格状态，没有信息惊喜或缓慢扩散的证据。

**Supporting observations**：预先登记主开发24m日期差+9.00pp，块区间[+1.74,+16.94]；主12m+1.66pp区间跨零。主结果后另登记同季度US股票对照，12/24m+7.66/+14.24pp，[+2.34,+11.12]/[+4.82,+24.86]pp，43/41双方季度。再次预登记全部10个leave-one-asset-out，各全期差符号仍正；不是看结果选择删除一个行业。跨分区实际严格无重叠只14/10季度，+6.58/+18.68pp，[+.13,+12.24]/[+6.14,+34.65]pp。全部方案/结果锁见research/phase3/matched及vol_falsification。

**Counterexamples**：Treasury同季度12/24m差−2.41/−2.59pp；开发市场分层香港、德国、英国24m方向相反。2000–09同季度US股票12/24m区间仍跨零，不足以证明跨年代稳定。开发主24m高波动组胜率73.26%低于不高组74.54%，均值优势不等于胜率优势。KBE2007Q4/2008Q1高波动之后12m净收益约−50.12%/−65.27%；金融机制反例保留。

**Negative controls / false negatives**：全US有效12m高波动组95个负收益行；不高波动组52个超过30%收益行（30%只是结果描述，没有新增signal门槛）。例如QQQ2002Q3/2019Q4不高组之后+55.18%/+46.02%。整个case列表保存在negative_case_index.v001.json，不能删除或只讲均值。

**Industries tested**：预定Technology/Semiconductor/Banks/Industrials/Consumer/Healthcare/Energy/Utilities及Broad/Growth美国代理，行业固定mandate映射；逐一删除后仍正只能排除单一资产完全驱动，不能证实每个行业内部都有效。金融只有KBE银行窄代理，原XLF全期隔离。

**Markets tested / regimes**：主面板美国/中国/香港/日本/欧洲当地收益；精确同季度可识别横截面主要是US股票与US债券，海外行业/地方现金不足，无法证实跨市场alpha。2000–09/2010–19/2020–25均报告，未用连续PIT利率/通胀把年代自动当经济regime；早期ETF历史、信用时间证据缺失，点数不是完整泡沫危机覆盖。

**Why it might persist / why arbitraged away**：风险承担、机构预算与不确定性可能要求补偿，未必是可套利错价；液体ETF公开价格特征易被套利，幸存者选择、周期暴露、成本和风险调整可消灭表面优势。没有机制识别，就不把“尚未被套利掉”当作已证事实。

**Price-In risk**：原估值/市场隐含增长/原一致预期全部未知。过去涨幅和波动不等于估值或反应不足。

**Failure conditions / falsifier**：未用于开发的行业/市场或未来冻结观测方向反转；相似风险暴露对照后差消失；闭市/ETF关闭/分红付款日执行核验消灭回报；原财务显示高波动只是补偿更差尾部；控制资产常量暴露后无增量。

**Confidence**：C，仅非操作性关联；机制D。多重比较、旧路径暴露、事后挑出值得攻击的主问题、区间未做multiple-testing校正均降级。不是LEVEL3，不进入CURRENT_FRAMEWORK operative fields。

**Next test**：先锁少量跨市场同业可交易代理与历史关闭工具；固定PIT风险暴露/地方现金，检验增量是否超越beta与行业身份。其次补原连续经营/融资数据，判断风险补偿或修复；真正未来capture按既定日程留存，缺捕获不回填。不得增加技术指标或改阈值救活。

## LEVEL3 — Investment Principle

0。尚无同时满足经济机制、跨市场/时期/风险匹配、反例边界及真实未来证据的原则。治理纪律、数据准入和现金benchmark不是由本样本验证的新收益规律。
''')
    write('PHASE3_RESEARCH_REPORT.md',f'''# Phase3研究与交付报告

本阶段增加了真实原信用发布和固定季度跨年代价格面板，未发现已可执行的稳健Conditional Edge。一个美国股票相对波动关联经过同日期、逐资产遗漏和非重叠反证后仍存活，最高仅C级非操作性候选；没有修改原投资规则。主面板之后已继续两个登记反证cycle，未停在扩样跑完。

## 已完成、未完成与停止边界

RAW OBSERVATIONS：2704固定选择格（26资产×2000–2025×四季度）；2113有效feature，92历史不足、395无源、104XLF隔离。六期限有效成熟标签分别{maturity}。主要12m2087、24m1995，不是2087/1995次新主观预测；概率预测新增0。273预定dossier质量见DEEP_EPISODE_LIBRARY_REPORT，完整已识别经济机制0。24个源下载成功，23个工具准入；26个计划不能说26个有效工具。

EFFECTIVE SAMPLE ASSESSMENT：101季度、26年、7市场标签（美国、中国、香港、日本、欧元区、德国、英国；五地区）、23有效工具。全球周期/同日行业相关与12/24m重叠仍在，独立N未知。跨分区每资产贪心无重叠12/24m仅480/245条，与分区内相加494/260不同；都不能称独立N。相对波动同季度严格全US非重叠对照仅14/10起点，独立世界数更小且未知。

原SLOOS104regular表，85可用公开时间（78封面精确分钟、7官方calendar日期级），19隔离；贷款标准由原人数计算，85跨2004–2025，不伪造2000–2003信用。原现托管档案仍不是第三方当年byte见证。报价是现在供应商的历史重构，不是原时点quote vintage。截止特征先统一锁；development统计锁后揭晓2024–25，但旧完整价格路径已暴露，后期仅计算隔离，不能叫真正future OOS。

执行5/21/63/126/252/504实际观察sessions，下一可交易观察开盘进入，固定50bp roundtrip假设；ETF除息经济再投资尚不等于付款日实盘，海外当地指数非直接可交易总回报。DAX供应商为performance口径，不能和其他当地价格指数混称。固定股债helper保守要求SPY/IEF/BIL共同历史，2002–2007某些IEF本可用对照因此缺失；保留原锁、报告限制，不为了补结论改实验。

**科学停止：RESEARCH_BLOCKED_BY_DATA_REQUIREMENT / NO ROBUST RETURN EDGE ESTABLISHED。** 价格状态的候选存活，不等于证明边际概率优势。下一关键问题需独立跨市场行业、历史风险暴露、原估值/预期、经营与再融资资料。继续重切同价格不能补这些识别条件。没有声称全球DATA EXHAUSTED。真实forward首月末2026-10-30尚未到，真实capture/decisions/outcomes均0，168计划slot不是实验，未部署cron。

## 用户要求的十五个回答

|问题|扩大样本后的答案|
|---|---|
|1. 原282哪些结论仍成立？|“尚无稳健通用/条件性优势”仍是证据状态；原冻结规则和weekly切换未重跑。本轮趋势均值/尾部、信用年代反转再次限制简单故事，不能说逐项重新验证原预测。|
|2. 哪些被推翻？|“增加更多记录便能证明优势”“大跌等于便宜”“信用不收紧就安全”“更高方向胜率必然更高赔率”不获支持。没有覆盖或删除原失败结果。|
|3. 哪些2016–2023特有？|同一新变量口径：高波动12m日期差2000–15约−.09pp，2016–23约+4.54pp；信用tight-minus-not早期−6.41pp、2016–23+7.43pp、2024–25−.94pp。反映样本/时代依赖，不能把整个2000–15冒称新OOS。|
|4. 哪些跨市场/regime仍存在？|没有经风险匹配并跨市场/regime验证的收益原则。US相对波动关联局部存活，但Treasury方向负、香港/德国/英国反例；年代不是有PIT证据的宏观regime标签。|
|5. 趋势是预测还是确认？|本轮没有证明独立收益预测性；正趋势组较浅回撤/较高胜率可能是确认用途线索，但确认必须能改变实际决策并胜过配置对照，尚未证明。|
|6. 估值预测什么尺度？|UNKNOWN / NOT TESTED：缺连续PIT原估值，不能用大跌或r252当估值。12/24m收益没有验证“估值只影响长期”的哲学。|
|7. 盈利修正有增量信息吗？|UNKNOWN / NOT TESTED：两原MSFT10-K/8facts不是历史一致预期revision序列，不能由实际盈利代替预期修正。|
|8. 信用是错杀过滤器吗？|重要但未识别的经济问题。原SLOOS单变量方向在年代间翻转，gate失败，Drawdown×Credit不运行；贷款标准不能代替spread/融资覆盖，不能判信用理论失败或有效。|
|9. Capital Cycle哪里最重要？|半导体、资源/能源、工业、公用事业的供给时滞机制值得优先，但历史原CapEx/需求观测未新增；八行业库是D级机制地图，不是实证排名。|
|10. 有真正Underreaction吗？|没有证实：无一致预期与首次现金流信息事件母体；波动后收益不等于慢反应。一周以上事件漂移需原发布、原预期和风险匹配对照。|
|11. 哪些只是Beta？|正绝对收益、相对全股票降回撤、公共时间反弹和行业均值都可由beta/配置解释。SPY残差仍不等于beta调整alpha；本轮未识别PAC-P3-001是否只是风险溢价/行业暴露。|
|12. 哪些可能Multiple Testing？|主两分区10272比较槽/5273可比较，相关基准槽51360及无重叠槽416；后续matched104/12可识别，遗漏年代88+无重叠2。均非独立假设计数；旧全部事后比较总数UNKNOWN。候选正区间未做选择校正，可信度降低，失败/无组格全保留。|
|13. 最接近的1–3个“钥匙”？|统计方向仅PAC-P3-001相对波动关联(C，非操作)。经济方向是原经营+再融资能否区别错杀/结构损伤(D)；原盈利信息相对起始隐含预期是否仍有增量(D)。不凑三条成立规律。|
|14. 为什么仍可能错？|存续ETF选择、原quote vintage缺失、全球周期与重叠、少量起点、beta/行业恒定暴露、尾部/执行成本、选择性关注及信息已price-in。早期区间跨零，US结果不能移植海外。|
|15. 下一笔研究成本花哪里？|先固定小跨市场同业/关闭工具及本地现金与PIT风险暴露，攻击存活vol关联；再固定连续原经营+债务到期/续借序列，区分错杀；最后原预期或可审计事件母体检验一周以上underreaction。同步真实未来捕获，不改旧规则。|

## 可审计入口与交付

先读SAMPLE_EXPANSION_PROTOCOL、EXPANDED_PANEL_REPORT、EFFECTIVE_SAMPLE_REPORT、CROSS_TIME_VALIDATION及PHASE3_SURVIVING_PRINCIPLES。机制专题为INDUSTRY_MECHANISM_LIBRARY、CRISIS_VS_CORRECTION_REPORT、TEMPORARY_VS_STRUCTURAL_REPORT、UNDERREACTION_REPORT；全部比较计入MULTIPLE_TESTING_LEDGER。

源/代码/锁/标签/完整失败格及counterexamples在research/phase3/。独立QA重新计算13086成熟horizon路径、配对与固定配置、全部统计/块区间；旧3366文件SHA守恒。具体验收以audit的最终JSON为准；工程计算检查不是新增投资样本。

最终CURRENT_FRAMEWORK仅更新研究状态与计数，9个operative字段逐一和Phase2基线相等，validated_principles仍空、live_signal_generation_enabled仍false。新增主观概率0，无新增校准成功声明。上轮Phase2包完整保留；Phase3完整包包括上轮便携研究与本轮源、代码、报告、checkpoint，原重复大输入用无损blueprint恢复并核验565原SHA。
''')
    # Preserve pre-outcome mechanism drafts; reports themselves are mutable narratives.
    for name in ['INDUSTRY_MECHANISM_LIBRARY.md','CRISIS_VS_CORRECTION_REPORT.md','UNDERREACTION_REPORT.md','TEMPORARY_VS_STRUCTURAL_REPORT.md']:
        text=(ROOT/name).read_text();write('research/phase3/mechanism_drafts/'+name,text)
        text=text.replace('未来标签尚未揭晓','未来标签已按锁顺序揭晓').replace('当前尚未揭晓未来价格标签','当前未来价格标签已按锁顺序揭晓').replace('尚未读取未来标签','未来标签已按锁顺序揭晓').replace('尚未揭晓标签','未来标签已按锁顺序揭晓')
        if name=='TEMPORARY_VS_STRUCTURAL_REPORT.md':text=text.replace('|`DATA_REQUIRED`|','|`NOT_RUN_GATE_FAILED`|',1)
        write(name,text)
        append(name,'''## Phase3完成后的实证边界

RAW OBSERVATIONS：2113有效价格决策点，2087成熟12m、1995成熟24m；新增完整经营/融资/估值/原预期机制观测仍0。EFFECTIVE SAMPLE ASSESSMENT：独立N未知；全球周期、行业与季度依赖不因复制信用值消失。

SLOOS预定gate在2000–09/2010–19的12m日期等权差为−8.50/+1.37pp，符号翻转，H-P3-DD-CREDIT明确NOT_RUN_GATE_FAILED，不调阈值。单指标未稳定不是信用危机机制被证伪；没有把净不收紧叫信用安全。

主面板大跌12m日期差+1.77pp且区间跨零；同季度US股票+3.66pp[−6.30,+12.98]且gross MDD差−7.88pp（更深）。同季度Treasury大跌12/24m−3.24/−9.86pp，只有5双方季度。价格下跌没有识别低估值或暂时错杀，也不能用后来反弹给T时资产负债表贴标签。

US股票相对波动同季度12/24m差+7.66/+14.24pp，国债对应−2.41/−2.59pp；逐一遗漏与全US严格非重叠反证后关联尚存，但早年代区间跨零、海外反例、未beta匹配。最高C非操作性关联，不等于强制出售、盈利改善、CapEx兑现或underreaction。完整存活与反证见PHASE3_SURVIVING_PRINCIPLES和research/phase3/vol_falsification。

本文件行业融资/现金流机制仍D，危机分类与一周以上慢反应均NOT IDENTIFIED。下一批优先固定原连续经营、再融资、地方信用和首次公开预期资料；不从赢家收益反推原因，不用宏观预测自动生成交易信号。
''')
    append('RESEARCH_LEDGER.md',f'''## RL-P3-C3 — 固定面板跨时间统计完成（补记锁链）

记账时间{now}；全A先锁，development结果锁后later揭晓，实际事件时间见各外置锁，不将本记账时间冒充事前。RAW OBSERVATIONS=2704选择/2113feature/2087成熟12m/1995成熟24m；原SLOOS104/85准入/19隔离，273dossier249有价格/184价格+信用。EFFECTIVE SAMPLE ASSESSMENT独立N未知；跨分区greedy12/24m480/245条而非分区相加494/260。主趋势无稳健收益增量，DD均值与风险共增，信用gate符号翻转NOT_RUN。主2分区10272比较槽全保留。

## RL-P3-C4 — 主面板后继续两次反证cycle

同季度同经济类matched104槽、12可识别，不运行失败credit gate；US股票vol12/24m差+7.66/+14.24pp。再次预登记全部10资产遗漏×4年代×2h共88槽及严格跨分区全US非重叠2槽，未挑最优删资产；非重叠14/10日期，差+6.58/+18.68pp。来源为真实冻结价格，新增decision/forecast0，全部坏格/负例保留。PAC-P3-001最高C统计关联，机制D，非风险匹配alpha、非新OOS，操作性原则0。

科学边界RESEARCH_BLOCKED_BY_DATA_REQUIREMENT / NO ROBUST RETURN EDGE ESTABLISHED：进一步可迁移性和风险补偿识别需跨市场行业/关闭工具、PIT原经营与融资/估值/预期。无全球DATA EXHAUSTED声明。forward只168计划，真实capture/预测/结果0。旧282、全部3366旧immutable与9operative fields不改；代码、QA与源字节已checkpoint。''')
    append('HYPOTHESIS_REGISTRY.md','''## Phase3完成状态（原记录不覆盖）

|ID|状态|结论边界|
|---|---|---|
|H-P3-TREND|DESCRIPTIVE_COMPLETED_NO_ROBUST_MEAN_EDGE|单变量趋势不重跑旧概率/择时规则；确认用途未验证|
|H-P3-DRAWDOWN|DESCRIPTIVE_COMPLETED_RISK_AND_RETURN_JOINT|均值反弹伴更深风险、日期配对区间跨0；不是低估值|
|H-P3-VOL|PREDICTIVE_ASSOCIATION_ONLY / C nonoperative|US股票局部关联存活；其他类/市场反例，未risk matched|
|H-P3-CREDIT|DESCRIPTIVE_COMPLETED_REGIME_SIGN_REVERSAL|原贷款标准而非信用整体；85原可用发布时间|
|H-P3-DD-CREDIT|NOT_RUN_GATE_FAILED|预定年代方向反转；不能改门槛/换股票子池救活|
|H-P3-VOL-ENDPOINT-v001|ENGINEERING_ENDPOINT_REGISTERED|504条相对波动未知，505足够；未改原协议|
|H-P3-MATCHED-CONTROLS-v001|EXPLORATORY_FALSIFICATION_COMPLETED|主结果已知后登记104槽/12有双组；非新OOS|
|H-P3-VOL-FALSIFICATION-v001|EXPLORATORY_SENSITIVITY_COMPLETED|88全遗漏/年代槽+2严格非重叠，全部展示，无优化|

旧15假说/15设计仍没有被新价格面板自动测试；原经济机制财务/估值缺失，未伪造历史observations。''')
    append('FAILED_HYPOTHESES.md','''## Phase3失败、反例与未识别记录

FH-P3-001：大跌就是便宜/安全买入的叙事不成立为原则。US同季度差区间跨0且未来gross MDD更深；Treasury大跌后均值负，只有5 dates。局部反弹尚可描述，不知道估值/偿付/原预期，不能判断错杀机制真伪。

FH-P3-002：信用收紧/未收紧单一过滤器方向跨年代不稳定；预定H-P3-DD-CREDIT gate失败，交互未执行。记录NOT_RUN_GATE_FAILED，不当信用因果理论被证伪；不改规则/换起点。

FH-P3-003：正趋势提高收益均值/独立赔率未成立；同季度US股票12/24m差约−.74/−1.80pp且区间跨0。较浅回撤不等于配置以上alpha，原失败概率rule保持冻结。

FH-P3-004：相对高波动若作“必涨/普适”故事被负控限制：95个US高波动负12m，52个不高波动仍>30%12m；Treasury方向负、HK/DE/UK市场反例、早2000–09区间跨0。有限US横截面平均关联仍存活，不能写完全被推翻，也不能救活原任何策略。全部negative case index保存。

FH-P3-005：尚无法判断Underreaction/价值长期尺度/盈利revision增量/CapEx收益因果；属于DATA_REQUIRED或NOT_IDENTIFIED，不是实验失败收益，也不是被证实经济钥匙。''')
    append('CANDIDATE_PRINCIPLES.md','''## Phase3追加：一个非操作性关联，零新增投资原则

PAC-P3-001 / LEVEL2 / C preliminary / PREDICTIVE_ASSOCIATION_ONLY：美国固定股票ETF集合里，相对自身历史高波动组的12/24m平均收益关系经同季度对照、全部10遗漏和严格非重叠后仍存活。不是更高上涨概率、不是beta匹配alpha、不是已识别经济机制；不得产生买卖规则。完整机制、counterexamples、negative controls、false negatives、产业/市场/年代、持续/套利解释、price-in、失效/下一测试见PHASE3_SURVIVING_PRINCIPLES。主结果后挑选攻击的问题与大范围比较需降级。

本次新增候选关联1/投资原则0；原15条candidate及CURRENT_FRAMEWORK operative candidate列表保持完全不变，没有A/B晋升。''')
    append('OPEN_QUESTIONS.md','''## Phase3之后按信息价值排序

1. PAC-P3-001是否只是行业身份、beta/久期或存续工具选择？先固定跨市场同业可交易代理/关闭ETF与地方现金，风险匹配不能使用未来估计作为T时信号；新实验登记全部对照，不改波动/持有期。
2. 原经营与再融资覆盖能否在同跌幅下区分修复与结构受损？固定少量公司全披露日历，原债务到期、可用现金、授信条件与经营现金；美国SLOOS只是context，不用其≤0代替安全，旧gate不救活。
3. 一周以后真正underreaction是否存在？先有固定首次披露/原预期母体与实际成本/风险对照；实际盈利不是revision、合同意向不是收入。真实monthly forward在2026-10-30按实际capture留存，缺当时snapshot就漏失，不能回填。

新但未识别的变量方向：贷款标准的“变化”与借款人的融资“水平/到期结构”可能是关键区分；相对波动可能标风险预算调整而非信息优势。这些是OPEN QUESTION / D，不因故事漂亮成为结论。''')
    append('PREDICTION_LEDGER.md',f'''## Phase3预测口径隔离 — {now}

新增主观Bear/Base/Bull/概率预测=0；2113是固定单变量决策feature，不是2113预测。2087/1995为12/24m成熟价格标签，经验winrate不是主观概率校准；没有新Brier或“70%概率”成功声明。原377有效预测与原374成熟12m锁完全不改，282基集保持。forward168planned/0real capture/0decision/0probability/0outcome；首月末2026-10-30。RAW OBSERVATIONS和独立N见Phase3面板/有效样本报告，不将多个期限标签记成新的实验。''')
    append('DATA_INVENTORY.md','''## Phase3增量库存

24实际Yahoo市场源成功、26计划/23准入；2000–2025固定季度2704格/2113feature。CSI300/CHINEXT无完整历史，XLF全期隔离，STOXX50E起2007不补早期；DAXperformance口径明确。QQQ2000普通split有Nasdaq作者press wire证明但不是原托管历史快照。全部原响应、canonical、manifest/SHA单独在research/phase3/data/market与action_proof，旧source不改。

SLOOS104regular原表，85可确认发布时间/19uncertain隔离；78PDF精确release ET/7官方calendar date-only，v002统一published_at精度但value/available保持，原人数推net非当年FRED修订series。原字节293+derived98全部来源引用与hash核验；2000–2003不能准入信用。变量仅US，不移植海外。

273deep dossier中249price、184price+原credit且均缺fundamentals。新增估值/原一致预期revision/行业CapEx与融资链0；独立N未知，不将273文本当机制证据。''')
    append('DATA_SOURCE_CATALOG.md','''## Phase3来源实测与新增限制

|Source|Data Type|Markets|History|Frequency|Point-in-Time Quality|Revision Risk|Survivorship Risk|Access Method|Reliability|Known Limitations|
|---|---|---|---|---|---|---|---|---|---|---|
|Fed archived regular SLOOS Table1+original report PDF|All Domestic Respondents大型/中型C&I标准net收紧|US only|104季度2000–2025；85时间可用2004–2025|quarterly|78原cover release minute、7官方calendar date保守次日；19UNKNOWN不喂A|今天托管archive静默更正风险；整数counts口径保留|银行响应样本构成演变，不等借款人余额加权|免费原HTML/PDF，293源字节+98derived留存|一手原发布；逐表人数/时间独立核验|不是overall信用安全、spread/default；firstyears timestamp缺，不移植海外|
|Yahoo chart Phase3 fixed26asset requests|dailyOHLC/actions|US/CN/HK/JP/EU/DE/UK|固定2000–2026来源请求，实际工具inception不同|daily|RECONSTRUCTED_NOT_ARCHIVED；逐T只取当时已发生行情/行动|供应商历史校正与分红金额未逐笔独立证|现存ETF选择、历史closed funds缺|免费接口原字节保留、24success/23admitted|二手，时间/价格/行动核验后有限使用|CSI300/CHINEXT缺，XLF隔离；STOXX从2007；DAXperformance；指数非可交易|
|Nasdaq issuer-authored release republished by MondoVisione|QQQ2000 ordinary2:1 action unit proof|US|effective2000-03-20，原作者说明firstyear|event|只admin单位证明，不当T时news predictor|当前镜像/重新托管，非当年byte见证|不解决全市场survivorship|免费完整正文+SHA|作者是一手issuer、托管是republication，双重边界说明|只解决普通action资格，不放行XLFspinoff，不创造历史经营数据|

代码、源清单与正式准入锁先于新标签。FRED今日修订历史未因网络可用就突然准入；旧其他数据缺口保留。''')
    append('CHANGELOG.md',f'''## {now} — Phase3 fixed panel + two falsification cycles

2704fixed/2113feature/2087mature12m/1995mature24m；原SLOOS104/85/19；273deep/249price/184price+credit。锁A→dev→later，协议未覆盖，505endpoint另登记。主10272比较槽；matched104以及vol全部遗漏/年代88+非重叠2。US波动关联最高C非操作，原operative9字段及全部旧immutable不变，失败策略无调参。科学边界blocked by original economic/risk/expectations data；前瞻0real。10required Phase3报告+summary+deep report，完整导出与上轮再交付正在验收。''')
    fw['framework_version']='0.4.0-phase3-research';fw['last_updated']=now
    fw['phase3_state'].update({'status':'NO_ROBUST_RETURN_EDGE_ESTABLISHED_RESEARCH_BLOCKED_BY_DATA_REQUIREMENT','new_feature_records':2113,'new_revealed_labels':sum(maturity.values()),'mature_feature_labels':maturity,'later_labels_opened':True,'deep_dossiers':273,'deep_price_available':249,'deep_price_and_original_credit':184,'identified_economic_mechanisms':0,'global_combined_actual_nonoverlap_12m':480,'global_combined_actual_nonoverlap_24m':245,'new_probability_forecasts':0,'new_operational_investment_principles':0,'exploratory_nonoperative_associations':[{'id':'PAC-P3-001','level':2,'confidence':'C','mechanism_confidence':'D','actionable':False,'path':'PHASE3_SURVIVING_PRINCIPLES.md'}],'matched_comparison_slots':104,'matched_identified':12,'vol_sensitivity_slots':88,'vol_strict_nonoverlap_slots':2,'effective_n':None,'forward_real_decisions':0,'operational_framework_changed':False,'stop_reason':'Further identification/transferability requires PIT economic/risk/expectations/financing data; no claim global data exhausted.'})
    assert all(fw[k]==v for k,v in old.items());write('CURRENT_FRAMEWORK.json',fw)
    write('research/status/LATEST.md',f'''# 当前可续接状态 — {now}

PHASE3主面板及两个反证cycle完成。NO ROBUST RETURN EDGE ESTABLISHED；进一步风险/机制/可迁移识别RESEARCH_BLOCKED_BY_DATA_REQUIREMENT，非全球DATA EXHAUSTED。原282和全部旧A/B/锁/失败策略不修改；9operative framework字段守恒，validated=[]，live=false。

2704fixed格/2113feature；12m2087、24m1995；273dossier249price/184price+原credit，完整机制0；原SLOOS104/85准入/19未知。独立N未知；101季度/26年，实际跨分区无重叠480/245仍相关资产行。主面板后的matched104/12可识别，再完整vol88+2反证，PAC-P3-001最高C非操作关联，未证明beta-adjusted alpha或未来OOS。新概率0；forward计划168/真实capture0，第一真实月末2026-10-30，未部署cron。

先读PHASE3_RESEARCH_REPORT、PHASE3_SURVIVING_PRINCIPLES、SAMPLE_EXPANSION_PROTOCOL、四统计报告及四机制报告，MULTIPLE_TESTING_LEDGER保留全部坏格。下一轮优先攻击存活关联的行业/beta/历史closed工具，原经营与再融资资料区分错杀，原事件预期检验慢反应。禁止rerun分析覆盖已冻结presentation或结果。

数据/代码/锁/原源在research/phase3，checkpoint C1/C2/C3/C4可恢复，独立QA在audit。上轮Phase2 ZIP不改，本轮便携包保留上轮研究+新增完整成果，565旧重复输入用blueprints无损恢复核对。
''')
    paths=['SAMPLE_EXPANSION_PROTOCOL.md','PHASE3_RESEARCH_REPORT.md','PHASE3_SURVIVING_PRINCIPLES.md','CURRENT_FRAMEWORK.json','RESEARCH_LEDGER.md','HYPOTHESIS_REGISTRY.md','FAILED_HYPOTHESES.md','CANDIDATE_PRINCIPLES.md','OPEN_QUESTIONS.md','PREDICTION_LEDGER.md','CHANGELOG.md','research/status/LATEST.md','research/phase3/features/decision_points.v001.json','research/phase3/labels/development.v001.json','research/phase3/labels/holdout.v001.json','research/phase3/analysis/development.lock.v001.json','research/phase3/analysis/holdout.lock.v001.json']
    write('research/phase3/CHECKPOINT_C3.v001.json',{'created_at':now,'stage':'MAIN_PANEL_COMPLETED_FROM_FROZEN_LOCK_CHAIN','recording_is_retrospective':True,'operative_fields_unchanged':True,'maturity':maturity,'independent_n':None,'files':{p:sha(ROOT/p) for p in paths}})
    write('research/phase3/CHECKPOINT_C4.v001.json',{'created_at':now,'stage':'TWO_FOLLOWUP_FALSIFICATION_CYCLES_COMPLETED','comparison_slots':{'matched':104,'vol_sensitivity':88,'vol_nonoverlap':2},'new_decisions':0,'new_predictions':0,'new_investment_principles':0,'nonoperative_candidate':'PAC-P3-001_C','files':{p:sha(ROOT/p) for p in ['research/phase3/matched/PREREGISTRATION.v001.json','research/phase3/matched/RESULTS.v001.json','research/phase3/matched/RESULTS.lock.v001.json','research/phase3/vol_falsification/PREREGISTRATION.v001.json','research/phase3/vol_falsification/RESULTS.v001.json','research/phase3/vol_falsification/RESULTS.lock.v001.json','CURRENT_FRAMEWORK.json','RESEARCH_LEDGER.md']}})
    print(json.dumps({'maturity':maturity,'deep_maturity':deep_maturity,'deep_quality':quality,'old_operative_fields':'UNCHANGED','new_investment_principles':0}))
if __name__=='__main__':main()
