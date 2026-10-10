#!/usr/bin/env python3
"""Source-first event records only. No price reads, no probabilities, no optimisation."""
import json,re,html,hashlib,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];R=ROOT/'research/phase4/regional/china';S=ROOT/'research/phase4/sources/china'
receipts=[]
for p in R.glob('*receipt.json'):receipts.extend(json.loads(p.read_text()))
by={x['source_id']:x for x in receipts}
texts={}
for sid,x in by.items():
 if x.get('status')!='DOWNLOADED':continue
 p=ROOT/x['path']
 if p.suffix=='.html':
  t=p.read_text(errors='replace');t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S);t=html.unescape(re.sub('<[^>]+>',' ',t));texts[sid]=re.sub(r'\s+',' ',t)
 elif p.suffix=='.pdf':
  d=p.with_suffix('.derived.txt');texts[sid]=d.read_text() if d.exists() else ''
(R/'source_extracted_text.json').write_text(json.dumps(texts,ensure_ascii=False,indent=2))

def source(sid):return by[sid]
def excerpt(sid,term,n=180):
 t=texts[sid];i=t.find(term)
 if i<0:raise ValueError((sid,term))
 return t[i:i+n]
def date_evidence(sid,date):
 t=texts[sid];m=re.search(re.escape(date),t)
 if m:return t[max(0,m.start()-15):m.end()+30]
 for pat in [date.replace('-','年',1).replace('-','月',1)+'日',str(int(date[:4]))+'年'+str(int(date[5:7]))+'月'+str(int(date[8:]))+'日']:
  if pat in t:return excerpt(sid,pat,50)
 raise ValueError(('No numeric date evidence',sid,date))

events=[]
def event(sid,family,date,participant,constraint,action,status,flow=None,duration='UNKNOWN_AT_T',parent=None,term=None,known=None,unknown=None,mechanism=None,alternate=None,falsifier=None,extra_sources=None):
 x=source(sid);srcs=[sid]+(extra_sources or []);p=parent or sid
 es=term and excerpt(sid,term,180) or texts[sid][:180]
 pe=date_evidence(sid,date)
 e=dict(event_id='PENDING',market='China',family=family,parent_episode=p,published_date=date,
 available_at=date+'T23:59:59+08:00',timezone='Asia/Shanghai',participant_type=participant,constraint=constraint,
 trigger='原源所报告的行动或制度调整；未用未来价格选样',observed_action=action,action_status=status,
 flow_size=flow,flow_duration=duration,assets=['SHCOMP'],voluntary_or_forced='主动/规则约束；不能据公告认定被迫买卖',price_sensitive='UNKNOWN_AT_T',information_based='UNKNOWN_AT_T',
 known_at_t=known or [action],known_only_after_t=['后续实际资产价格仅可作Outcome Label；本模块未读取','后续计划履行率和最终现金流不在T时点信息集'],
 unknown_at_t=unknown or ['市场事前预期和已计价程度','新增流量的未来净额、持续性和对手方','受益资产长期盈利、偿付能力是否受损'],
 source_ids=srcs,source_paths=[source(a)['path'] for a in srcs],source_urls=[source(a)['url'] for a in srcs],source_sha256=[source(a)['sha256'] for a in srcs],
 source_excerpt=es,publication_date_evidence=dict(source_id=sid,excerpt=pe,locator='原HTML可见发布日期/发布目录日期；PDF发布日期由配套官方网页证明',precision='DATE_ONLY',timestamp_policy='即使页面给时分秒也采用日末保守上界；不是精确首发时刻'),
 pit_status='VERIFIED_DATE_ONLY',confidence_level='LEVEL 1 — 机制可行；行为/制度事实有原源，预测优势未识别',
 mechanism=mechanism or '规则改变约束→可能改变边际行为；实际流量、资产价值和价格预期链条仍须分别验证',
 alternative_explanation=alternate or '约束变化可能只是响应已发生的市场/宏观变化；方向可由基本面或同期政策驱动',
 falsifier=falsifier or '后续实际执行为零、其他资金完全抵销、基本面继续损坏或效应仅持续不足一周',
 fundamental_change_at_t=None,credit_change_at_t=None,selection_basis='PARTIAL_CATALOG；官方日期排序等序位规则，未读取新未来价格；完整候选/未选/blocked保留',
 source_vintage_limitation='今日官方服务器原始响应字节+可见历史发布时间；不是历史日期网页的独立WARC快照，未知内容修订风险')
 events.append(e);return e

def flow(v,basis,scope,direction='UNKNOWN'):return dict(value=v,unit='亿元人民币',currency='CNY',basis=basis,scope=scope,direction=direction)
# PBOC partial directory: preselected positions across 180 eligible dated records.
pb={
 1:(370,'340亿元一年央票+30亿元28天正回购；是毛回笼，不知到期抵销','1年/28天','GROSS_ABSORPTION','发行了2008年第六十四期央行票据'),
 2:(420,'180亿元三月央票+60亿元六月央票+180亿元28天正回购；毛回笼','91天/182天/28天','GROSS_ABSORPTION','发行了2008年第九十期'),
 3:(950,'450亿元一年央票+500亿元28天正回购；毛回笼','1年/28天','GROSS_ABSORPTION','发行了2009年第三十六期央行票据'),
 4:(240,'发行240亿元一年央票；毛回笼','1年','GROSS_ABSORPTION','发行了2010年第七十二期央行票据'),
 5:(1450,'7天650亿元、14天800亿元逆回购；毛投放','7天/14天','GROSS_INJECTION','以利率招标方式开展了逆回购操作'),
 6:(300,'14天150亿元、28天150亿元逆回购；毛投放','14天/28天','GROSS_INJECTION','开展了300亿元逆回购操作'),
 7:(0,'当天不开展逆回购；不把1000亿元国库现金存款操作冒充央行股票买入','当天','ZERO_REVERSE_REPO','不开展逆回购操作'),
 8:(100,'7天逆回购毛中标量；未扣到期','7天','GROSS_INJECTION','开展了100亿元逆回购操作'),
 9:(20,'7天逆回购毛中标量；未扣到期','7天','GROSS_INJECTION','开展了20亿元逆回购操作'),
 10:(450,'香港CMU发行300亿元91天+150亿元一年央票；境外人民币流动性毛回笼','91天/1年','OFFSHORE_GROSS_ABSORPTION','发行了2024年第十期和第十一期央行票据')}
for x in json.loads((R/'event_download_plan.json').read_text()):
 if not x['source_id'].startswith('CN-S-PBOC-OMO-'):continue
 i=int(x['source_id'][-2:]);v,b,d,di,term=pb[i]
 e=event(x['source_id'],'央行执行',x['published_date'],'中国人民银行/一级交易商','货币市场流动性、央票/回购到期结构',b,'OBSERVED_ACTION',flow(v,'GROSS_OPERATION',b,di),d,parent='CN-PBOC-OMO-'+x['published_date'][:4],term=term,mechanism='央行与银行体系之间的准备金/抵押融资传导；不识别股票资金归属或股票回报')
 e['voluntary_or_forced']='央行政策执行；交易商依规则投标';e['price_sensitive']='招标利率/价格；股票价格敏感性未识别';e['information_based']='资金供需管理，不是资产盈利预测';e['known_at_t']=[b,'未获知到期规模，因此不能将毛操作当净投放']
 if i==10:e['assets']=['SHCOMP','CNH money market','Hong Kong CNY bills'];e['asset_scope_caveat']='主要行动发生于离岸人民币货币市场；SHCOMP仅预定广义背景，不证明直接股票需求'
 if i==7:e['zero_action']=True
# Huijin all available 2023–25 original directory action records, then fixed equal ranks.
for x in json.loads((R/'huijin_selected.json').read_text()):
 sid=x['source_id'];t=texts[sid].split('最新要闻')[0];d=x['date']
 if '发行' in t.split('中央汇金投资有限责任公司')[0]:
  m=re.search(r'在银行间债券市场发行(\d+)亿元|公开招标发行(\d+)亿元',t);v=int(next(g for g in m.groups() if g)) if m else None
  e=event(sid,'政策性/国家资本',d,'中央汇金/债务融资工具持有人','债务到期与负债管理','汇金报告完成债券发行；募集用途是优化负债结构/流动资金或偿还到期债券，不能分配为股票净买入','OBSERVED_ACTION',flow(v,'ACTUAL_ISSUANCE_NOT_EQUITY_PURCHASE','汇金债务融资毛发行') if v is not None else None,'2–7年债券期限；新增股市投入持续期未知',parent='CN-HUIJIN-FUNDING-'+d[:4],term='汇金公司于',known=['债务融资已经发行','一般募集用途没有证券购买金额归属'],mechanism='资金可得性/到期再融资约束；发行提供容量，不自动提供股票买盘',alternate='新债主要偿还旧债，净可投资资本没有增加',falsifier='资金明细表显示新增净资金且具有已执行股票购买用途，才推翻“用途未识别”')
  e['cash_use_stage']='FUNDING_EXECUTED; EQUITY_DEPLOYMENT_NOT_IDENTIFIED'
 else:
  term='中央汇金公司近日已' if sid.endswith('1002221') else '中央汇金公司坚定看好'
  e=event(sid,'政策性/国家资本',d,'中央汇金','维护市场稳定/国有资本管理职责，可有非收益目标','原公告明确已发生增持，同时许诺未来继续；不披露金额和剩余购买能力','OBSERVED_ACTION',None,'六个月（2023银行未来意向）；2025ETF持续期未知',parent='CN-HUIJIN-EQUITY-SUPPORT-'+d[:4],term=term,known=['已发生增持的官方主体披露','未来继续增持是意向，未当作既成现金流'],unknown=['已执行成交量/金额、标的ETF和未来日程','稳定目标与财务回报目标权重','持有者约束与被投资银行/公司长期资产质量'],mechanism='稳定市场职责可能降低短期价格敏感性；已成交与剩余额度必须分开')
  e['voluntary_or_forced']='政策职责下主动执行；没有逐日被迫购买证据';e['price_sensitive']='可能对短期价格不敏感，但未识别交易规则';e['information_based']='稳定/配置意愿，不证明内部盈利信息或正确性'
# Insurance permission / registration (all six distinct dated candidates; duplicate mirrors not independent).
ins=[
('CN-S-INS-2014-MIRROR','2014-02-19','规则按资产大类分类、设比例监管和年度审议；未披露新增配置','MANDATE_CHANGE','制定不同大类资产的投资总量'),
('CN-S-INS-2015-MIRROR','2015-07-08','合格公司单一蓝筹比例上限5%→10%，权益达到30%后可增至40%；是上限而非应投金额','MANDATE_CHANGE','将投资单一蓝筹股票的比例上限'),
('CN-S-INS-2018-RULE','2018-10-26','允许专项产品化解股票质押流动性风险；不纳入权益比例；未提供实缴/资产购买','MANDATE_CHANGE','允许保险资产管理公司设立专项产品'),
('CN-S-INS-2018-REGISTER','2018-10-30','凤凰系列10月29日完成登记；200亿元为目标总规模，未证明实缴或已投','OBSERVED_ACTION','完成登记手续'),
('CN-S-INS-2020','2020-07-19','按偿付能力等分八档，最高45%，能力不足不得新增权益；没有实际新增股票配置','MANDATE_CHANGE','明确八档权益类资产监管比例'),
('CN-S-INS-2025-MIRROR','2025-04-08','调整为按偿付能力分五档上限10/20/30/40/50%；不能将50%上限乘资产当确定流入','MANDATE_CHANGE','权益类资产配置比例，调整为以下标准')]
for sid,d,a,status,term in ins:
 e=event(sid,'保险配置',d,'保险机构/保险资产管理人','偿付能力、负债久期、集中度、流动性、内部授权',a,status,None,'制度可能多年；实际配置速度UNKNOWN_AT_T',parent='CN-INSURANCE-SPECIAL-2018' if '2018' in sid else 'CN-INSURANCE-ALLOCATION-'+d[:4],term=term,known=[a],unknown=['当时存量持仓距离上限的余量','实际实缴和成交','偿付能力和负债现金流限制','同次政策其他资金的抵销'],mechanism='扩大合格保险人的可配置集合；需求仍取决于偿付能力、资产负债匹配和投资意愿',alternate='此前未接近上限，因此上限提升不约束边际买入；专项产品还可能投资债权',falsifier='约束原本不绑定或放开后实际权益仓位不升，则“释放确定股市增量”失败')
 e['source_level']='政府门户转载监管原文/通稿；不是第二条独立证据'
 e['voluntary_or_forced']='制度强制上限；具体投资自主决策';e['price_sensitive']='配置仍受收益/风险/负债约束，非无条件买入';e['information_based']='制度约束变化或登记事实；无回报预测'
 if status=='OBSERVED_ACTION':e['cash_use_stage']='PRODUCT_REGISTERED; CASH_DEPLOYMENT_NOT_IDENTIFIED';e['announced_capacity']={'value':200,'unit':'亿元人民币','basis':'TARGET_FUND_SIZE_NOT_PAID_IN'}
# Margin directory plus dated source-first CSRC candidates. Equal ranks over 17, no rescuing notable ones.
mar=json.loads((R/'sse_margin_all_candidates.json').read_text());mar=[x for x in mar if x['eligible']]
for sid,d in [('CN-S-MARGIN-2015-LAW','2015-07-01'),('CN-S-MARGIN-2015','2015-11-13'),('CN-S-MARGIN-2023','2023-08-27'),('CN-S-MARGIN-2024','2024-02-05')]:mar.append(dict(source_id=sid,published_date=d,title=texts[sid].split(' | ')[0],role='SEARCH_CANDIDATE'))
mar=sorted(mar,key=lambda x:(x['published_date'],x['source_id']));msel=[mar[i*(len(mar)-1)//9] for i in range(10)] if len(mar)>10 else mar
(R/'margin_all_candidates_final.json').write_text(json.dumps(mar,ensure_ascii=False,indent=2));(R/'margin_selected.json').write_text(json.dumps(msel,ensure_ascii=False,indent=2))
for x in msel:
 sid=x['source_id'];d=x['published_date'];t=texts[sid];term='为' if '为' in t else '根据'
 if sid=='CN-S-MARGIN-2015-LAW':term='2015年7月1日证监会令第117号公布'
 # Article-specific extracts: keep only native words and avoid inferring clearing transactions.
 if sid=='CN-S-MARGIN-DIR-2024-07-10':term='融券保证金比例'
 if sid=='CN-S-MARGIN-DIR-2023-10-14':term='融券保证金比例'
 if sid=='CN-S-MARGIN-DIR-2023-04-28':term='担保物集中度管理'
 if sid=='CN-S-MARGIN-DIR-2013-06-25':term='ETF融资余额'
 if term not in t:term=x['title']
 e=event(sid,'融资融券',d,'证券交易所/券商/信用账户投资者','标的资格、保证金、担保物集中度、券源、短售/信息披露规则',x['title']+'：公布融资融券约束/规则变化；尚无账户级执行量', 'MANDATE_CHANGE',None,'制度期间；可能持续月/年，实际去杠杆速度未知',parent='CN-MARGIN-RULES-'+d[:4],term=term,known=['仅原源可见规则文本/资格约束发生变化；不等于已清仓或买入'],unknown=['各账户是否触及约束','券商自设保证金/追保期限','变更实际执行金额与对冲','借款人的现金流与资产价值'],mechanism='担保物/风险限额改变可改变可维持仓位，但余额变化不等于forced cash flow',alternate='借款人可能主动还贷/增加抵押品；规则有过渡期/存量合约例外',falsifier='没有账户触发约束或原约束不绑定，则强迫清算机制未成立')
 e['voluntary_or_forced']='规则必须遵守；尚未观察forced liquidation';e['source_archive_caveat']='部分SSE现存法规路径迁移至2025目录；采用正文/当前官方索引的旧发布日期，非用URL路径当发布日期'
# Corporate actual aggregate / spending / loan disbursement reports: no issuer selection using future performance.
corp=[
('CN-S-CORP-2020','2020-06-11','2020年1–5月199家上市公司实施股份回购，金额147.31亿元',flow(147.31,'ACTUAL_AGGREGATE_BUYBACK_REPORTED','2020年1–5月两市回购'),'今年 1-5月','CN-CORPORATE-BUYBACK-2020'),
('CN-S-CORP-2023','2023-10-31','前三季度实体类公司研发支出约5813亿元、同比8%；真实产业支出不等股票买盘或盈利捕获',flow(5813,'ACTUAL_RESEARCH_EXPENSE_NOT_STOCK_FLOW','2023年前三季度沪市实体公司研发'),'实体类公司合计研发支出约5813亿元','CN-CORPORATE-SPENDING-2023'),
('CN-S-CORP-2024','2024-01-12','12月15日至发布会窗口，514家公司实际回购增持超过277亿元；309家428亿元为计划上限，分别保存',flow(277,'ACTUAL_AGGREGATE_REPORTED_LOWER_BOUND','新闻发布会所述12月15日规则后至发布时窗口'),'514','CN-CORPORATE-BUYBACK-2023-2024'),
('CN-S-CORP-2025','2025-05-09','2024年浙江辖区上市公司实施回购210余亿元；2025年5月披露才进入信息集',flow(210,'ACTUAL_AGGREGATE_REPORTED_LOWER_BOUND','2024年浙江辖区回购；不是全国'),'实施回购 210','CN-CORPORATE-BUYBACK-ZJ-2024'),
]
for sid,d,a,f,term,parent in corp:
 e=event(sid,'公司/产业资金',d,'上市公司/控股股东/管理层/产业企业','预算、现金流、债务、公司治理、回购用途',a,'OBSERVED_ACTION',f,'已报告期间的累计事实；未来持续期UNKNOWN_AT_T',parent=parent,term=term,known=[a,'累计流量是发布前的既成事实，不能证明发布后仍有剩余买盘'],mechanism='付出真实资金比口头意向更可检验；回购可用于员工激励而不注销，产业费用可产生供给竞争',alternate='公司在高价回购、员工激励/支撑价格、行业过度投资；经济变化共同决定支出与价格',falsifier='投资未转化为订单/自由现金流、回购用途造成再稀释、或预算/剩余额度已耗尽')
 if sid=='CN-S-CORP-2023':e['fundamental_change_at_t']='源报告显示真实研发支出同比增加，但未来利润捕获未识别'
 if sid=='CN-S-CORP-2025':e['asset_scope_caveat']='地方公司子集；SHCOMP只作预定宽基背景，不能归因或代表全市场流量'
# Loan Q4: published official news date corroborates report, which separates facility operations from loan issuance.
q4txt=texts['CN-S-CORP-LOAN-2024-Q4'];q4m=re.search(r'已发放[^。]{0,80}',q4txt)
# Do not take a statement about SFISF operation or agreed contracts as actual shareholder buyback.
e=event('CN-S-CORP-LOAN-2024-Q4-PUBLICATION','公司/产业资金','2025-02-13','中国人民银行/非银金融机构/贷款银行','合格抵押品、专款专用、银行授信、贷款与回购双层执行','2024Q4货币政策报告披露2024年10月/2025年1月互换便利分别开展500/550亿元操作；这是换券工具执行，不等股票购入','OBSERVED_ACTION',flow(1050,'ACTUAL_FACILITY_OPERATION_NOT_STOCK_PURCHASE','2024年10月与2025年1月互换便利两次操作合计'),'工具可融资；剩余股票部署日程未知',parent='CN-CAPITAL-MARKET-FACILITIES-2024',term='2024年第四季度中国货币政策执行报告',extra_sources=['CN-S-CORP-LOAN-2024-Q4'],known=['报告已公开','互换便利报告的500/550亿元为工具执行金额，不是购买股票金额'],mechanism='合格非银抵押品换高流动性资产后再融资；必须追踪融资和股票成交两道脚印')
e['source_excerpt']=excerpt('CN-S-CORP-LOAN-2024-Q4','别开展操作 500',220);e['source_excerpt_source_id']='CN-S-CORP-LOAN-2024-Q4'
e=event('CN-S-CORP-LOAN-2025-Q1-PUBLICATION','公司/产业资金','2025-05-12','商业银行/上市公司/主要股东','银行风险自担、回购专用账户、现金用途限制','官方上海门户在5月12日发布并附2025Q1报告：3月末相关贷款已发放约420亿元；拟申请近900亿元/合同超700亿元并非实际支出','OBSERVED_ACTION',flow(420,'ACTUAL_LOAN_DISBURSEMENT_NOT_VERIFIED_EQUITY_TRADE','截至2025年3月末股票回购增持银行贷款'),'存量贷款；后续回购/增持期未知',parent='CN-CAPITAL-MARKET-FACILITIES-2024',term='发布时间：2025-05-12',extra_sources=['CN-S-CORP-LOAN-2025-Q1'],known=['截至报告期末实际发放贷款约420亿元','贷款合同/申请上限大于实发','采用可查官方转载5月12日作为保守公开日；不将3月31日季度末当已知时点'],unknown=['逐笔股票购买、贷款尚未部署/是否已用','剩余贷款和计划执行时间','是否提前计价、是否替代原自有资金','贷款企业和股东资产负债表风险'],mechanism='资金便宜/专用贷款增强购买能力；融资到账仍需成交明细核实，不能认定净新增市场买盘')
e['source_excerpt']=excerpt('CN-S-CORP-LOAN-2025-Q1','3 月末，上市公司披露',250);e['source_excerpt_source_id']='CN-S-CORP-LOAN-2025-Q1';e['original_report_cover_date']='2025-05-09';e['original_first_publication_verified_from_native_contemporaneous_source']=False
# Stable global CN IDs sorted chronologically after source selection, no forecasts attached.
events.sort(key=lambda x:(x['published_date'],x['family'],x['source_ids'][0]))
for i,e in enumerate(events,1):e['event_id']=f'CN-P4-{i:03d}'
(R/'events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
# Explicit archive shell/failed sources and undated notice remain excluded, never filled.
quarantine=[]
for sid in ['CN-S-INS-2014','CN-S-INS-2015','CN-S-INS-2025','CN-S-CORP-2019','CN-S-CORP-RELOAN-2024','CN-S-CORP-RELOAN-2024-PBOC']:
 x=source(sid);quarantine.append(dict(x,pit_status='POINT_IN_TIME_UNCERTAIN',reason='下载失败/JS shell无正文，或只有成文日期未证明原首次发布日期；未纳入量化事件',known_only_after_t=['今日检索/工具抽取不可替代当时已公开原文']))
(R/'quarantined_candidates.json').write_text(json.dumps(quarantine,ensure_ascii=False,indent=2))
# All native response receipts and derived text inventory, including excluded context.
index=[]
for sid,x in sorted(by.items()):
 y=dict(x);p=ROOT/x['path'] if x.get('path') else None
 if p and p.suffix=='.pdf' and p.with_suffix('.derived.txt').exists():
  d=p.with_suffix('.derived.txt');y.update(derived_text_path=str(d.relative_to(ROOT)),derived_text_sha256=hashlib.sha256(d.read_bytes()).hexdigest())
 y['is_event_source']=any(sid in e['source_ids'] for e in events);y['primary_source_bytes']=y.get('status')=='DOWNLOADED';y['historical_vintage_snapshot']=False;index.append(y)
(R/'sources_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2))
from collections import Counter
summary=dict(raw_events=len(events),family_counts=dict(Counter(e['family'] for e in events)),action_status_counts=dict(Counter(e['action_status'] for e in events)),pit_counts=dict(Counter(e['pit_status'] for e in events)),unique_parent=len(set(e['parent_episode'] for e in events)),unique_dates=len(set(e['published_date'] for e in events)),years=sorted(set(e['published_date'][:4] for e in events)),real_stock_purchase_events=[e['event_id'] for e in events if 'HUIJIN-EQUITY' in e['parent_episode']],independent_n='NOT_IDENTIFIED；同项目/年和公共流动性重叠',quarantined_candidates=len(quarantine),source_bytes_downloaded=sum(x.get('bytes',0) for x in index),future_price_read=False)
(R/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
# Freeze regional newly-built Stage A evidence before root outcomes.
paths=['events.json','sources_index.json','huijin_selected.json','margin_selected.json','summary.json']
lock={'locked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':'CHINA_SOURCE_EVIDENCE_PRE_OUTCOME','sha256':{f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in paths},'outcomes_seen_in_module':False}
(R/'CHINA_EVENT_EVIDENCE.v001.lock.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2))
