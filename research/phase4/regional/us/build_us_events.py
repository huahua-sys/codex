#!/usr/bin/env python3
"""Normalize original US source actions. Never imports market prices/outcomes."""
import hashlib,json,re,shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from acquire_us_sources import ROOT,OUT,SRC,fetch,savej,digest

MONTHS='January|February|March|April|May|June|July|August|September|October|November|December|Jan\\.|Feb\\.|Mar\\.|Apr\\.|Jul\\.|Aug\\.|Sept\\.|Oct\\.|Nov\\.|Dec\\.'
DATE_RE='(?:'+MONTHS+')\\s+\\d{1,2},\\s+\\d{4}'
def parsedate(s):
    s=s.replace('Sept.','Sep.')
    return datetime.strptime(s,'%b. %d, %Y' if '.' in s else '%B %d, %Y').strftime('%Y-%m-%d')
def pub(date,tz,prec='DATE',time=None):
    clock=time if prec=='MINUTE' else '23:59:59'
    return datetime.fromisoformat(date+'T'+clock).replace(tzinfo=ZoneInfo(tz)).isoformat()
def body(text):
    m=re.search(r'For (?:immediate )?release',text)
    if m: return text[m.start():].split('Last Update:')[0]
    m=re.search(r'Washington D\.C\.,',text)
    if m:return text[m.start():].split('###')[0]
    m=re.search(r'REDMOND',text)
    return text[m.start():] if m else text
def event_base(family,slot,source,date,timezone,excerpt,pub_evidence):
    return {'market':'US','family':family,'parent_episode':None,'published_date':date,'available_at':pub(date,timezone),'timezone':timezone,'publication_date_precision':'DATE','publication_date_evidence':pub_evidence,'participant_type':None,'constraint':None,'trigger':None,'observed_action':None,'action_status':'OBSERVED_ACTION','action_type':'RETROSPECTIVE_DISCLOSURE','flow_size':None,'flow_duration':None,'assets':['SPY'],'voluntary_or_forced':'UNKNOWN','price_sensitive':'UNKNOWN','information_based':'UNKNOWN','known_at_t':[],'known_only_after_t':[],'unknown_at_t':['未来价格、市场真实预期、未公开的仓位/对冲以及交易对手约束'],'source_ids':[source['source_id']],'source_paths':[source['source_path']],'source_urls':[source['url']],'source_sha256':[source['source_sha256']],'source_excerpt':excerpt,'pit_status':'PIT_ORIGINAL_PUBLICATION_DATE_VERIFIED','confidence_level':'LEVEL 1','mechanism':None,'alternative_explanation':None,'falsifier':None,'fundamental_change_at_t':None,'credit_change_at_t':None,'selection_basis':{'protocol':'research/phase4/protocols/BEHAVIORAL_EVENT_SELECTION_PROTOCOL.v001.md','catalog_index':slot.get('catalog_index'),'catalog_n':slot.get('catalog_n'),'rule':'date order equisequence floor(i*(n-1)/9); no outcome/price filter'},'classification_at_t':'UNCLEAR','outcomes':None}

def main():
    if (OUT/'events.lock.v001.json').exists():
        raise SystemExit('US events v001 is frozen. Verify existing files with qa_us_sources.py; any correction must be an append-only documented version, never rerun the builder in-place.')
    slots=json.loads((OUT/'selected_source_slots.v001.json').read_text());manifest=json.loads((OUT/'source_manifest.v001.json').read_text())['records'];ms={x['url']:x for x in manifest}
    events=[];missing=[]
    credit=json.loads((ROOT/'research/phase3/data/credit/credit.records.v002.json').read_text())['records']
    # Full regular-release universe 2008–2025. PIT failures retained, not replaced.
    banks=sorted([r for r in credit if 2008<=r['survey_year']<=2025],key=lambda r:(r['survey_year'],r['survey_month']))
    chosen=[(i*(len(banks)-1))//9 for i in range(10)]
    savej(OUT/'bank_catalog.v001.json',{'n':len(banks),'records':[{'record_id':r['record_id'],'published_date':r['publication_date'],'pit_status':r['pit_status']} for r in banks],'selected_indices':chosen})
    for ix in chosen:
        r=banks[ix]
        if not r.get('available_at') or r.get('value') is None:missing.append({'family':'bank_lending_standards','slot':ix,'record_id':r['record_id'],'status':'POINT_IN_TIME_UNCERTAIN'});continue
        srcs=[]
        for source in [r['availability_evidence']['source'],{'url':r['source_url'],'source_path':r['source_path'],'source_sha256':r['source_sha256'],'content_type':'application/pdf','role':'original_respondent_table'}]:
            sid='US_SOURCE_'+digest(source['url'].encode())[:20];p=SRC/(sid+'.pdf');b=(ROOT/source['source_path']).read_bytes();assert digest(b)==source['source_sha256'];p.write_bytes(b)
            sm=dict(source,source_id=sid,source_path=str(p.relative_to(ROOT)),bytes=len(b),reused_from=source['source_path']);savej(SRC/(sid+'.source.json'),sm);srcs.append(sm)
        counts=r['value_evidence']['counts'];excerpt=r['availability_evidence']['quote']+'\nOriginal table1: All Respondents: '+json.dumps(counts,ensure_ascii=False)
        ev=event_base('bank_lending_standards',{'catalog_index':ix,'catalog_n':len(banks)},srcs[0],r['publication_date'],'America/New_York',excerpt,{'excerpt':r['availability_evidence']['quote'],'locator':'Original full-report cover, page 1','source_path':srcs[0]['source_path']})
        ev.update(parent_episode='US_SLOOS_'+str(r['survey_year'])+'_'+str(r['survey_month']).zfill(2),participant_type='US domestic commercial banks',constraint='资本、风险/损失预期、借款人需求；问卷不识别哪项约束绑定',trigger='过去约三个月贷款条件变化；在原报告日才公开',observed_action=f"受访银行报告对大/中企业C&I贷款标准净收紧 {r['value']:.6f} 个百分点（非资金流）",flow_duration='回看约三个月；下一季度持续性未知',voluntary_or_forced='UNKNOWN; respondent lending choice not proven forced',price_sensitive='NOT_IDENTIFIED',information_based='SELF_REPORTED_LENDING_ACTION',known_at_t=[r['availability_evidence']['quote'],{'net_tightening_percentage_points':r['value'],'respondent_counts':counts}],credit_change_at_t={'reported_net_tightening_pp':r['value'],'scope':'US domestic-bank large/middle-firm C&I lending standards, not spreads/defaults'},mechanism='信贷供给约束可能经融资/现金流传到资产价格；不是即时flow或偿付安全证明',alternative_explanation='需求下降、被调查银行构成或宏观预期同向变化',falsifier='控制共同宏观状态后，报告无法区分资产损坏/持有人约束，或贷款标准不传到实际融资量',publication_date_precision='MINUTE',available_at=r['published_at'])
        ev['source_ids']=[s['source_id'] for s in srcs];ev['source_paths']=[s['source_path'] for s in srcs];ev['source_urls']=[s['url'] for s in srcs];ev['source_sha256']=[s['source_sha256'] for s in srcs]
        events.append(ev)
    for family,rows in slots.items():
        for slot in rows:
            source=ms[slot['url']]
            if not source.get('text_path'):
                missing.append({'family':family,'slot':slot,'status':'SOURCE_UNAVAILABLE','error':source.get('error')});continue
            text=(ROOT/source['text_path']).read_text();b=body(text);date=slot['date'];tz='America/New_York'
            if family=='corporate_capital_allocation':
                tz='America/Los_Angeles';m=re.search(DATE_RE,b)
                if not m:missing.append({'family':family,'slot':slot,'status':'POINT_IN_TIME_UNCERTAIN','reason':'No original dateline'});continue
                date=parsedate(m.group());pubquote=b[:m.end()+70]
            elif family=='passive_and_fund_constraints':
                m=re.search(DATE_RE,b)
                if not m:missing.append({'family':family,'slot':slot,'status':'POINT_IN_TIME_UNCERTAIN','reason':'No original dateline'});continue
                date=parsedate(m.group());pubquote=b[:m.end()+3]
            else:
                # Original HTML article date, not solely URL or Last Update metadata.
                raw=(ROOT/source['source_path']).read_text(errors='replace')
                datehits=re.findall(r'<(?:p|time)[^>]*(?:article__time|time)[^>]*>(.*?)</(?:p|time)>',raw,re.S)
                dates=[re.sub('<[^>]+>','',s).strip() for s in datehits]
                match=next((x for x in dates if re.search(DATE_RE,x)),None)
                if not match:missing.append({'family':family,'slot':slot,'status':'POINT_IN_TIME_UNCERTAIN','reason':'Original article publication date not located'});continue
                original_date=re.search(DATE_RE,match).group();assert parsedate(original_date)==date;pubquote=original_date+'; '+b.split('\n')[0]
            ev=event_base(family,slot,source,date,tz,b[:2200],{'excerpt':pubquote,'locator':'Original article publication heading/dateline (not fiscal-end or URL-only)','source_path':source['source_path']})
            if family=='central_bank_liquidity_execution':
                taf='Term Auction Facility' in b;label='Total propositions accepted:' if taf else 'Total Amount Awarded:'
                amount=re.search(re.escape(label)+r'\s*\$\s*([\d,.]+)\s*(billion)?',b)
                if amount:
                    value=float(amount[1].replace(',',''))*(1e9 if amount[2] else 1)
                    ev['flow_size']={'value':value,'currency':'USD','unit':'USD','scope':'this auction gross awarded principal','basis':'AWARD_RESULT_NOT_SETTLED_CASH_FLOW; offered ceiling excluded; renewal/net balance not known'}
                ev.update(parent_episode='US_TAF' if taf else 'US_TDF',participant_type='Federal Reserve and eligible depository institutions',constraint='银行抵押品/到期融资与Fed资格、期限、竞价限制' if taf else '银行选择将储备转为不能即期支付的定期存款；Fed技术性测试',trigger='公布上一日定期贷款拍卖授标结果' if taf else '公布定期存款拍卖授标结果',observed_action='TAF授标已完成；现金贷款将在原声明所列未来settlement日交割' if taf else 'TDF存款授标已完成；未来settlement将把可用准备金转成定期存款，方向与TAF相反',flow_duration=(re.search(r'\d+-day',b).group() if re.search(r'\d+-day',b) else '28-day')+' loan/deposit term, not an equity buying forecast',voluntary_or_forced='VOLUNTARY_BID; funding need may constrain choice but no proven forced equity sale',price_sensitive='AUCTION_PRICE_SENSITIVE',information_based='FUNDING_OPERATION_NOT_STOCK_VIEW',mechanism='TAF缓解合格抵押融资约束；TDF是相反方向的准备金期限转换，不能共同归为QE',alternative_explanation='流动性操作可能是危机严重程度的内生响应；授标可能替代其他融资/展期，非净增股市资金',falsifier='融资约束未缓解、使用者/资产偿付恶化，或授标未交割/只为技术测试',known_at_t=[b[:1800]],unknown_at_t=ev['unknown_at_t']+['实际未来交割、净新增而非rollover金额、借款人身份/资产质量、资金是否购买股票'])
                time=re.search(r'For release at (\d{1,2}):(\d{2}) ([ap])\.m\. (EST|EDT)',b)
                if time:
                    hour=int(time[1])%12+(12 if time[3]=='p' else 0);ev.update(publication_date_precision='MINUTE',available_at=pub(date,tz,'MINUTE',f'{hour:02d}:{time[2]}:00'))
            elif family=='regulatory_capital_constraints':
                ev.update(parent_episode='US_AMLF_RULES' if 'AMLF' in slot['title'] or '20080919' in slot['url'] else ('US_VOLCKER_RULES' if 'volcker' in slot['title'].lower() else 'US_BANK_REG_'+date),participant_type='Federal banking agencies and regulated banks/dealers',constraint='资本/杠杆/压力测试或持仓活动限制；规则生效前过渡期须单列',trigger=slot['title'],observed_action=slot['title'],action_status='MANDATE_CHANGE',action_type='MANDATE_CHANGE',flow_duration='监管适用期；各行落实时间和真实仓位改变未知',voluntary_or_forced='MANDATORY_RULE_FOR_APPLICABLE_ENTITIES; actual trades not observed',price_sensitive='UNKNOWN; regulation is not a trade',information_based='PUBLIC_REGULATORY_RULE_NOT_DIRECTIONAL_SIGNAL',mechanism='规则改变可影响中介资产负债表空间，但需要银行资本余量/风险预算和实际仓位佐证',alternative_explanation='规则已在提案/立法时预期；不约束边际银行，或受盈利/风险需求抵消',falsifier='未适用于边际中介、其他约束仍绑定，或额度释放不伴随真实风险承担',known_at_t=[b[:2200]],unknown_at_t=ev['unknown_at_t']+['实际资金流和受影响银行边际约束、最终生效后的执行规模'])
            elif family=='passive_and_fund_constraints':
                proposal='Proposes' in slot['title']
                ev.update(parent_episode='US_MMF_2014_REFORM' if date[:4]=='2014' else 'US_MMF_2023_REFORM',participant_type='SEC, money-market-fund boards/advisers and redeeming investors',constraint='可赎回负债对非即期可卖资产；净值、流动资产、费用与门槛制度',trigger=slot['title'],observed_action=slot['title'],action_status='ANNOUNCEMENT_ONLY' if proposal else 'MANDATE_CHANGE',action_type='ANNOUNCEMENT_ONLY' if proposal else 'MANDATE_CHANGE',flow_duration='proposal not binding' if proposal else '按规则过渡期执行；基金资金实际迁移未知',voluntary_or_forced='NOT_A_TRADE; applicable fund rule mandatory only after effectiveness',price_sensitive='UNKNOWN',information_based='RULE_ACTION_NOT_OBSERVED_FUND_FLOW',mechanism='赎回成本/门槛改变先赎回优势及流动性储备；不能据此推算股票flow',alternative_explanation='改革被预期，或改变产品/负债结构但无股票边际流',falsifier='过渡期内持仓/客户结构未改变，或制度变化不降低/改变run incentives',known_at_t=[b[:2200]],unknown_at_t=ev['unknown_at_t']+['基金未来赎回额、持仓迁移、ETF创建赎回实量；2021回述2020不是2020时已知'])
                if proposal:ev['known_only_after_t']=['该原文回顾2020年赎回压力属于2021年才公开/汇总的叙事；未回填2020事件。']
            else:
                norm=re.sub(r'\s+',' ',b);cash=re.search(r'Common stock repurchased\s*\(([\d,]+)\)',norm,re.I)
                excerpt=re.search(r'Common stock repurchased.{0,130}',norm,re.I)
                if cash:
                    ev['flow_size']={'value':int(cash[1].replace(',',''))*1e6,'currency':'USD','unit':'USD','scope':f'Microsoft FY{slot["year"]} Q4 three months ended June 30, cash-flow row, first current-year column','basis':'ACTUAL_REPORTED_COMMON_STOCK_REPURCHASE_CASH_OUTFLOW; not authorization; may include share tax withholding, does not identify open-market timing'}
                detail=excerpt.group() if excerpt else 'Cash-row amount not extracted; scale remains null'
                ev['source_excerpt']=pubquote+'\n'+detail+'\n'+(re.search(r'Microsoft returned.{0,220}',norm).group() if re.search(r'Microsoft returned.{0,220}',norm) else '')
                if slot['year']==2009:ev['source_excerpt']+='\n'+re.search(r'While we did not repurchase.{0,180}',norm).group()
                ev.update(parent_episode='US_MSFT_CAPITAL_ALLOCATION',participant_type='Microsoft board/treasury and existing shareholders',constraint='现金创造、债务、回购授权、资本配置和股票薪酬；投资者方向意图不能由现金流推知',trigger='固定FY Q4财报发布；6月30日财期结束不等于披露日',observed_action='披露此前季度的common-stock-repurchase现金支出，非当日新回购指令；2009原文另明确该季度无常规回购',flow_duration='已发生季度流；未来回购速度/窗口与授权使用量未知',voluntary_or_forced='MIXED_UNKNOWN; discretionary capital return and tax-withholding obligations may differ',price_sensitive='EXECUTION_NOT_IDENTIFIED',information_based='CAPITAL_ALLOCATION_BELIEF_NOT_CORRECTNESS',mechanism='真实减少流通股可能传导到每股现金流；借债/对冲/薪酬稀释及支付价格可抵消，报告本身滞后',alternative_explanation='补偿股权稀释、员工代扣或常规分配；未来盈利和估值更主导结果',falsifier='净股数未下降、资金用于昂贵回购而核心投资/盈利恶化，或披露时已完全预期',known_at_t=[pubquote,detail],unknown_at_t=ev['unknown_at_t']+['回购精确交易日与支付价格、未来订单/利润、相对基本价值、price-in程度'],fundamental_change_at_t='Full earnings release also changes reported business/earnings information; cannot isolate repurchase disclosure from earnings')
            events.append(ev)
    events.sort(key=lambda e:(e['published_date'],e['family']))
    for n,e in enumerate(events,1):e['event_id']=f'US-P4-{n:03d}'
    for e in events:
        e['pit_status']='VERIFIED' if e['publication_date_precision']=='MINUTE' else 'VERIFIED_DATE_CONSERVATIVE'
        e['source_revision_risk']='Official historical original currently hosted; no contemporaneous independent archive snapshot; possible silent source corrections.'
        e['broad_asset_reaction_only']=True
        e['counterfactual']='NOT_IDENTIFIED: matched broad-asset date controls are descriptive and cannot isolate actor-specific counterfactual'
        e['generalizability']='Not established; same program/company and common macro constraints cluster observations.'
        e['closest_similar_events']=[]
        e['important_differences']=[]
    savej(OUT/'events.json',events);savej(OUT/'missing_slots.v001.json',missing)
    savej(OUT/'source_manifest.v002.json',{'records':[json.loads(p.read_text()) for p in sorted(SRC.glob('*.source.json'))]})
    summary={'raw_events':len(events),'unique_dates':len({e['published_date'] for e in events}),'unique_years':len({e['published_date'][:4] for e in events}),'unique_parent_episodes':len({e['parent_episode'] for e in events}),'families':dict(Counter(e['family'] for e in events)),'action_status':dict(Counter(e['action_status'] for e in events)),'action_type':dict(Counter(e['action_type'] for e in events)),'missing_slots':len(missing),'price_or_outcome_read':False,'effective_sample':'UNKNOWN: 10 SLOOS releases, 10 auctions primarily two Fed programs, 9 single-issuer records and shared regulatory parents; raw not independent N','highest_confidence':'LEVEL 1 prior to price study; source action is not return edge'}
    savej(OUT/'summary.v001.json',summary);savej(OUT/'events.lock.v001.json',{'file':'research/phase4/regional/us/events.json','sha256':digest((OUT/'events.json').read_bytes()),'locked_at':datetime.now().astimezone().isoformat(),'price_outcome_accessed_before_lock':False})
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
