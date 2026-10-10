#!/usr/bin/env python3
"""Build frozen evidence cards from selected source bytes; never opens prices."""
import hashlib, html, json, pathlib, re, zipfile, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[4]
REG=ROOT/'research/phase4/regional/japan';SRC=ROOT/'research/phase4/sources/japan'

def clean(s): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
    selection=json.loads((REG/'selected_source_assignment.json').read_text())
    manifest=json.loads((SRC/'SOURCE_MANIFEST.json').read_text())
    index={r['source_id']:r for r in manifest}
    # Correct filename extensions for exact original XLSX bytes, without modifying any byte.
    for row in manifest:
        if row['status']!='FETCHED':continue
        p=ROOT/row['path']
        if p.read_bytes().startswith(b'PK\x03\x04') and '.xlsx' in row['url']:
            q=p.with_suffix('.xlsx')
            if p!=q:p.rename(q)
            row['path']=str(q.relative_to(ROOT));row['content_format']='XLSX'
    events=[];fails=[]
    corp_parent={24:'JP-JPX-BUYBACK-20160728',25:'JP-JPX-BUYBACK-20160728',26:'JP-JPX-BUYBACK-20170130',27:'JP-JPX-BUYBACK-20170130',28:'JP-JPX-BUYBACK-20170130',29:'JP-JPX-BUYBACK-20210428',30:'JP-JPX-BUYBACK-20210428',31:'JP-JPX-BUYBACK-20230130'}
    for i,r in enumerate(selection,1):
        source=index[r['event_source_id']];cat=index[r['catalog_source_id']]
        if source['status']!='FETCHED':fails.append({'selection':r,'reason':'SELECTED_SOURCE_DOWNLOAD_FAILED'});continue
        p=ROOT/source['path'];txt=p.with_suffix('.txt')
        if txt.exists(): text=txt.read_text()
        elif p.suffix=='.xlsx':
            with zipfile.ZipFile(p) as z:
                ss=ET.fromstring(z.read('xl/sharedStrings.xml'))
                text=' | '.join(''.join(si.itertext()) for si in list(ss))
            p.with_suffix('.txt').write_text(text)
        else:
            raw=p.read_text(errors='replace');text=clean(raw[raw.find('<!-- [START] CONTENT_1 -->'):raw.find('<!-- [START] FOOTER -->')] if 'boj' in r['url'] else raw)
            p.with_suffix('.txt').write_text(text)
        text_clean=clean(text)
        family=r['family'];d=r['published_date']
        e={'event_id':f'JP-P4-{i:03}','market':'Japan','family':family,'parent_episode':None,
           'published_date':d,'available_at':d+'T23:59:59+09:00','timezone':'Asia/Tokyo',
           'published_date_evidence':{'precision':'DATE_CONSERVATIVE_END_OF_DAY','excerpt':r['date_evidence'],'locator':'official catalog date adjacent to selected URL',
                'source_path':cat['path'],'source_sha256':cat['sha256'],'source_url':cat['url'],
                'historical_vintage_independently_archived':False},
           'participant_type':None,'constraint':None,'trigger':r['title'],'observed_action':None,
           'action_status':None,'action_type':None,'flow_size':None,'flow_duration':None,
           'assets':['NIKKEI'],'voluntary_or_forced':None,'price_sensitive':None,'information_based':None,
           'known_at_t':[],'known_only_after_t':['此发布日期以后的市场回报、追加政策/执行与实际现金流变化；本文件未读取'],
           'unknown_at_t':['市场预期中已计入的行动规模/时间','同日其他政策与全球风险变化','可靠原始信用/盈利修正','实际可交易alpha'],
           'source_ids':[source['source_id'],cat['source_id']],'source_paths':[source['path'],cat['path']],
           'source_urls':[source['url'],cat['url']],'source_sha256':[source['sha256'],cat['sha256']],
           'source_excerpt':None,'pit_status':'VERIFIED_DATE_ONLY','confidence_level':'LEVEL_1_MECHANISM_PLAUSIBLE',
           'mechanism':None,'alternative_explanation':None,'falsifier':None,
           'fundamental_change_at_t':None,'credit_change_at_t':None,
           'selection_basis':{'method':'official catalog ascending equal-rank capped 10 per family; n<=10 all retained','catalog_index':r['catalog_index'],'catalog_n':r['catalog_n'],'catalog_coverage':'PARTIAL_CATALOG' if family!='BOJ' else 'ANNUAL_STATEMENT_CATALOGS_2008_2025','outcome_used':False},
           'source_vintage_limitation':'原publisher日期可确认；现有网站字节不是独立历史网页快照，未证明每个字节在T已原样存在。'}
        if family=='BOJ':
            regime=('2008_NORMAL' if i==1 else '2009_2012_LOW_RATE' if i<5 else '2013_2015_QQE' if i<7 else '2017_2023_YCC' if i<10 else '2025_NORMALIZATION')
            e.update(parent_episode='JP-BOJ-'+regime,participant_type='Central Bank (BOJ)',constraint='物价稳定与金融市场运行目标；政策委员会及业务框架约束，非股东回报最大化',
                observed_action='已发布政策委员会指导/维持或变更政策条件。不是实际ETF买卖交易回执。',action_status='ANNOUNCEMENT_ONLY',action_type='ANNOUNCEMENT_ONLY',
                flow_duration='指导适用于meeting之间或年度目标；实际执行速度与金额未知',voluntary_or_forced='POLICY_DISCRETION_WITH_LEGAL_MANDATE',price_sensitive='目标实施受市场条件限制；并非无条件托底',information_based='包含经济判断与非收益政策目标，不能解释为买入方向预测',
                mechanism='政策改变JGB收益率/融资和日元相对回报，并可能授权ETF配置；实际执行与价格传导需另验',alternative_explanation='市场事前预期/全球货币政策/汇率变化共同驱动；宽基反应不能识别BOJ买卖实流',falsifier='若实施现金流未发生或市场已预期全部变更，持续资金流领先价格解释不成立')
            # Preserve only contemporaneous statements, including unchanged policies as negative controls.
            target=re.search(r'(?:call rate[^.]{0,100}|annual pace[s]?[^.]{0,150}|around\s+0\.?[0-9]*\s*percent)',text_clean,re.I)
            e['known_at_t']=['当日官方政策指导原文已公开','政策额度/年度速度是指导，不等于已完成现金流']+([target.group(0)] if target else [])
            e['unknown_at_t']+=['未来真实ETF/JGB执行日与净额','日元变化是否导致对冲/去杠杆']
            start=text_clean.find('Bank of Japan');e['source_excerpt']=text_clean[max(0,start):max(0,start)+230]
        elif family=='GPIF':
            mandate=any(x in r['title'].lower() for x in ['policy asset mix','revised policy','revised stewardship'])
            fy='2023' if i==11 else '2024' if i<=14 or i==17 else '2025'
            e.update(parent_episode=('JP-GPIF-STEWARDSHIP' if i in [15,20] else 'JP-GPIF-ALLOCATION-2025' if i==16 else 'JP-GPIF-DISCLOSURES-FY'+fy),participant_type='Public Pension (GPIF)',
                constraint='长期养老金给付、政策配置偏离范围、外部管理人与治理要求；不能把资产配置当择时预测',
                observed_action=('发布配置/委托人治理规则；未观察真实净买入' if mandate else '滞后公布季度/年度持仓与资产配置状态；权重/市值变化不等于净买卖'),
                action_status='MANDATE_CHANGE' if mandate else 'OBSERVED_ACTION',action_type='MANDATE_CHANGE' if mandate else 'RETROSPECTIVE_DISCLOSURE',
                flow_duration='多年配置/委托制度；披露仅覆盖过去会计期，未来执行速度未知',voluntary_or_forced='MANDATE_CONSTRAINED_REBALANCING_NOT_VERIFIED_FORCED_TRADE',
                price_sensitive='配置偏离范围可能约束，但具体成交价格敏感性未知',information_based='非方向赌注；资产配置与养老负债匹配可以独立于短期市场观点',
                mechanism='目标与实际持仓差距可能诱发慢速再平衡；先扣除价格/FX/衍生品估值及养老金净移交',alternative_explanation='资产上涨或日元改变可导致市值/权重变动；季度披露时成交早已发生',falsifier='剔除估值与资金移交后无同向净买卖，或目标范围内无强制再平衡，则慢钱持续买入解释失败')
            e['known_at_t']=['当前发布日期之前完成会计期的已公布信息','市值/权重包含价格与FX重估；未识别独立净流量','不可将会计期末视为公开日期']
            if i==16:e['known_at_t']+=['第五中期目标配置2025-04-01生效；四资产各25%维持目标，不代表新增25%资金需求']
            if i==20:e['known_at_t']+=['文件规则修订日为2025-12-08，英文公开目录日期2025-12-22；从后者保守计时']
            e['unknown_at_t']+=['净买卖与价格重估分解','管理人对冲、衍生品与未公开执行安排','会计期结束日至公开日之间持仓变动']
            e['source_excerpt']=text_clean[:210]
            e['holding_snapshot_only']=not mandate
        elif family=='GovernanceCrossShareholding':
            e.update(parent_episode='JP-JPX-CORPORATE-GOVERNANCE-CODE',participant_type='Exchange / Listing Rule Authority',
                constraint='上市公司治理、compliance-or-explain与董事会披露约束；不等于强制卖出所有交叉持股',
                observed_action='制定/修订治理准则与上市规则；无独立持股出售金额证据',action_status='MANDATE_CHANGE',action_type='MANDATE_CHANGE',
                flow_duration='多年治理/董事会实施；个体出售、回购与资本投入进度未知',voluntary_or_forced='RULE_CONSTRAINED_DISCLOSURE_WITH_COMPANY_DISCRETION',
                price_sensitive='企业资产出售与回购可以等待/调整；非刚性立即成交',information_based='规则信息；不是现金流改善或低估值证明',
                mechanism='董事会解释政策持股合理性/资本效率后可能出售、改变股东治理与利润留存用途；必须识别实际行动及价值捕获',
                alternative_explanation='企业已计划出售或改资本政策；全球利润与日元环境可解释指数上涨',falsifier='只有披露措辞改变，持股未减且资本回报/盈利未改善，则治理改革=新增买盘逻辑失败')
            date_pattern={'2015-05-13':'May 13, 2015','2018-06-01':'Jun. 01, 2018','2021-06-11':'Jun. 11, 2021'}[d]
            hit=text_clean.find(date_pattern); e['source_excerpt']=text_clean[max(0,hit):max(0,hit)+230]
            if hit<0:raise RuntimeError('Original governance release publication date not found: '+d)
            e['published_date_evidence'].update(excerpt=date_pattern,locator='original Market News date heading',source_path=source['path'],source_sha256=source['sha256'],source_url=source['url'])
            e['known_at_t']=['原发布日期规则文本已公开','2015规则2015-06-01生效；2018/2021修订按原公告生效','治理规则本身没有给出交叉持股实售或回购规模']
            e['unknown_at_t']+=['各公司实际出售、买回与CapEx分配','少数股东能否捕获回报']
        else:
            amount=re.search(r'3[．.]\s*Total value of shares acquired\s+JPY\s*([\d,]+)',text)
            if not amount: raise RuntimeError('Original period actual buyback amount not identified: '+str(i))
            amount=int(amount.group(1).replace(',',''))
            shares=re.search(r'2[．.]\s*Total no\. of shares acquired\s+([\d,]+)\s*shares',text)
            period=re.search(r'4[．.]\s*Acquisition period\*?\s+([^\n]+)',text)
            e.update(parent_episode=corp_parent[i],participant_type='Corporation (Japan Exchange Group; single company only)',
                constraint='董事会授权上限、取得期限、blackout与市场购回规则；额度并非必须完成的义务',observed_action='公布已执行回购状态，包含真实零执行月与结束记录',
                action_status='OBSERVED_ACTION',action_type='RETROSPECTIVE_DISCLOSURE',flow_size={'value':amount,'unit':'JPY','basis':'PERIOD_ACTUAL_REPURCHASE_VALUE; positive is issuer gross purchase, not broad-market net flow'},
                flow_duration=clean(period.group(1)) if period else 'UNKNOWN',voluntary_or_forced='VOLUNTARY_WITH_AUTHORIZATION_CAP',
                price_sensitive='自主选择取得速度与是否完成上限；确切limit order未知',information_based='资本分配/库存股取得行为；管理层看好不等于投资正确',
                mechanism='已实施回购减少可流通供给但授权残余额不代表未来刚性买盘；公告后的新增买入须另证',
                alternative_explanation='EPS机械变化、资本结构/员工激励库存、经营现金流及市场变化；NIKKEI仅宽基背景而非8697个股收益',
                falsifier='计划结束/执行归零，或经营回报不改善；此时剩余额度≠持续买盘')
            e['source_excerpt']=clean(amount and text[text.find('2．'):text.find('(Reference)')] or text[text.find('1.'):text.find('(Reference)')])[:260]
            e['known_at_t']=[f'截至公开日已披露该取得期间真实购回JPY {amount:,}',f"实际股数 {int(shares.group(1).replace(',','')) if shares else 'UNKNOWN'}，按交易日口径",
                '回购上限与累积完成额是不同字段；当期0不能删除为失败样本','这是单个JPX公司，不代表全日本企业净流，也不测试个股alpha']
            if i in [24,25]:e['known_at_t']+=['2016董事会上限JPY10bn；已披露累积JPY3,994,268,900']
            if i==25:e['known_at_t']+=['旧计划已结束；同日另有新计划，不能把两计划剩余量连起来']
            e['unknown_at_t']+=['未来买入是否还有余额、是否愿意执行','8697原点时预期/估值/盈利修正']
            e['reported_actual_period_shares']=int(shares.group(1).replace(',','')) if shares else None
        events.append(e)
    write(REG/'events.json',events)
    write(REG/'missing_slots.json',{'foreign_investors':json.loads((REG/'selection.v001.json').read_text())['foreign_missing_slots'],'selected_failed':fails,
       'additional_failed_candidates':[{'url':'https://www.sony.com/en/SonyInfo/IR/news/2019.html','status':'HTTP_403','outcome_used':False,'excluded_reason':'official directory access failed; no inferred event or date'},
            {'url':'https://www.boj.or.jp/en/mopo/etf/index.htm','status':'HTTP_404','excluded_reason':'candidate directory does not exist; no retry substitutes guessed flows'}]})
    # Add retained probes to byte manifest with no historical timing claim.
    seen={r.get('path') for r in manifest}
    for p in sorted(SRC.glob('probe_*')):
        if p.suffix=='.txt' or str(p.relative_to(ROOT)) in seen:continue
        manifest.append({'source_id':p.stem,'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'status':'FETCHED','role':'PRESELECTION_ACCESS_PROBE_NOT_EVENT','url':{
            'probe_stock250101':'https://www.jpx.co.jp/english/markets/statistics-equities/investor-type/dh3otn000000pp8l-att/stock_val_1_250101.pdf',
            'probe_0':'https://www.gpif.go.jp/en/performance/pdf/2014_q1.pdf','probe_1':'https://www.gpif.go.jp/en/performance/pdf/adoption_of_new_policy_asset_mix.pdf','probe_2':'https://www.gpif.go.jp/en/topics/2024/'}[p.stem]})
    write(SRC/'SOURCE_MANIFEST.json',manifest)
    counts={};statuses={}
    for e in events:counts[e['family']]=counts.get(e['family'],0)+1;statuses[e['action_type']]=statuses.get(e['action_type'],0)+1
    checks={'events':len(events),'families':counts,'action_types':statuses,'unique_parent':len({e['parent_episode'] for e in events}),
       'unique_date':len({e['published_date'] for e in events}),'unique_year':len({e['published_date'][:4] for e in events}),
       'positive_actual_flow':sum(e['flow_size'] is not None and e['flow_size']['value']>0 for e in events),'zero_actual_flow':sum(e['flow_size'] is not None and e['flow_size']['value']==0 for e in events),
       'selection_sha256':hashlib.sha256((REG/'selection.v001.json').read_bytes()).hexdigest(),
       'events_sha256':hashlib.sha256((REG/'events.json').read_bytes()).hexdigest(),'price_data_read':False,'original_byte_checks':True}
    for e in events:
        for p,s in zip(e['source_paths'],e['source_sha256']):assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==s
    write(REG/'QA_CHECKPOINT.json',checks);print(json.dumps(checks,ensure_ascii=False))
if __name__=='__main__':main()
