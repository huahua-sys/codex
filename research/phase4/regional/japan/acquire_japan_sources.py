#!/usr/bin/env python3
"""Source-first official Japan catalogs. No price access. Standard-library only."""
import concurrent.futures as cf
import datetime as dt
import hashlib
import html
import json
import pathlib
import re
import subprocess
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = ROOT / 'research/phase4/sources/japan'
REG = ROOT / 'research/phase4/regional/japan'
OUT.mkdir(parents=True, exist_ok=True)
REG.mkdir(parents=True, exist_ok=True)
records = []

def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()

def date(s):
    s=clean(s).replace('Sept.', 'Sep').replace('Sept ', 'Sep ').replace('.', '')
    for fmt in ['%b %d, %Y', '%B %d, %Y']:
        try: return dt.datetime.strptime(s, fmt).date().isoformat()
        except ValueError: pass
    return None

def get(job):
    name,url,role = job
    target=OUT/name
    try:
        if target.exists(): b=target.read_bytes()
        else:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'InvestmentResearchLab/4 public research'}), timeout=35) as r: b=r.read()
            target.write_bytes(b)
        r={'source_id':name.rsplit('.',1)[0], 'url':url,'path':str(target.relative_to(ROOT)),
           'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'role':role,'status':'FETCHED',
           'retrieved_at':dt.datetime.now(dt.timezone.utc).isoformat()}
        if b.startswith(b'%PDF'):
            txt=subprocess.run(['pdftotext','-layout',str(target),'-'],capture_output=True,text=True).stdout
            target.with_suffix('.txt').write_text(txt)
        else: txt=b.decode('utf-8','replace')
        return r,txt
    except Exception as e:
        return {'source_id':name.rsplit('.',1)[0],'url':url,'role':role,'status':'FAILED',
                'error':type(e).__name__+': '+str(e)},''

def fetch(jobs):
    result={}
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        for r,t in ex.map(get,jobs): records.append(r);result[r['source_id']]=(r,t)
    return result

def select(rows):
    rows=sorted({(r['published_date'],r['url']):r for r in rows}.values(),key=lambda r:(r['published_date'],r['url']))
    n=len(rows); pos=list(range(n)) if n<=10 else [i*(n-1)//9 for i in range(10)]
    return rows,[dict(rows[p],catalog_index=p,catalog_n=n) for p in pos]

def main():
    jobs=[(f'boj_catalog_{y}.html',f'https://www.boj.or.jp/en/mopo/mpmdeci/state_{y}/index.htm','OFFICIAL_DATED_CATALOG') for y in range(2008,2026)]
    jobs += [(f'gpif_catalog_{y}.html',f'https://www.gpif.go.jp/en/topics/{y}/','OFFICIAL_DATED_CATALOG') for y in range(2014,2026)]
    jobs += [('jpx_governance_catalog.html','https://www.jpx.co.jp/english/equities/listing/cg/index.html','INSTITUTIONAL_CATALOG'),
             ('jpx_capital_catalog.html','https://www.jpx.co.jp/english/corporate/investor-relations/shareholders/basic-policy/index.html','CURRENT_PROGRAM_CATALOG_NOT_PIT'),
             ('jpx_foreign_catalog_2025.html','https://www.jpx.co.jp/english/markets/statistics-equities/investor-type/00-00-archives-01.html','DATED_OBSERVATION_CATALOG_NO_RELEASE_DATE')]
    # Monthly official directories covering the complete programs shown in the current JPX table.
    # Program completion is not publication date; directories establish the latter separately.
    months=['201701','201702','201705','201706','202109','202110','202307','202308','202507','202508']
    jobs += [(f'jpx_corp_catalog_{m}.html',f'https://www.jpx.co.jp/english/corporate/news/news-releases/static-archives-{m}.html','OFFICIAL_DATED_PARTIAL_CATALOG') for m in months]
    pages=fetch(jobs)
    catalogs={}
    boj=[]
    for k,(r,s) in pages.items():
        if not k.startswith('boj_catalog_'): continue
        for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',s,re.S):
            cells=re.findall(r'<td\b[^>]*>(.*?)</td>',row,re.S)
            if len(cells)<2: continue
            d=date(cells[0]); a=re.search(r'href="([^"]+)"',cells[1])
            if d and a: boj.append({'family':'BOJ','published_date':d,'title':clean(cells[1]),'url':urllib.parse.urljoin(r['url'],a.group(1)),'date_evidence':clean(cells[0]),'catalog_source_id':r['source_id'],'catalog_source_path':r['path']})
    catalogs['BOJ'],selected_boj=select(boj)
    gpif=[]
    for k,(r,s) in pages.items():
        if not k.startswith('gpif_catalog_'): continue
        for rawdate,dd in re.findall(r'<dt class="NewsList__title">(.*?)</dt>\s*<dd class="NewsText">(.*?)</dd>',s,re.S):
            d=date(rawdate);a=re.search(r'href="([^"]+)"',dd)
            title_m=re.search(r'<h2[^>]*>(.*?)</h2>',dd,re.S);title=clean(title_m.group(1)) if title_m else clean(dd)
            if not d or d>'2025-12-31' or d<'2008-01-01' or not a:continue
            # Participant actions: allocation mandate, quarterly holdings disclosures, stewardship-rule implementation.
            if not any(x in title.lower() for x in ['investment results','policy asset mix','revised policy','revised stewardship','portfolio holdings']): continue
            if any(x in title.lower() for x in ['annual report','(summary)','（summary）']):continue
            gpif.append({'family':'GPIF','published_date':d,'title':title,'url':urllib.parse.urljoin(r['url'],a.group(1)),'date_evidence':clean(rawdate),'catalog_source_id':r['source_id'],'catalog_source_path':r['path']})
    catalogs['GPIF'],selected_gpif=select(gpif)
    corp=[]
    for k,(r,s) in pages.items():
        if not k.startswith('jpx_corp_catalog_'): continue
        # Each item holds its own news date and anchor. The date is never guessed from URL.
        for block in re.findall(r'<li\b[^>]*>(.*?)</li>',s,re.S):
            if not re.search(r'(?:status|completion|conclusion).*?acquisition of own shares',clean(block),re.I):continue
            a=re.search(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',block,re.S)
            dmatch=re.search(r'(Jan\.?|Feb\.?|Mar\.?|Apr\.?|May|Jun\.?|Jul\.?|Aug\.?|Sep\.?|Sept\.?|Oct\.?|Nov\.?|Dec\.?)\s*(\d{1,2}),?\s*(20\d\d)',clean(block))
            if a and dmatch:
                d=date(' '.join([dmatch.group(1),dmatch.group(2)+',',dmatch.group(3)]))
                if d:corp.append({'family':'CorporateCapitalAllocation','published_date':d,'title':clean(a.group(2)),'url':urllib.parse.urljoin(r['url'],a.group(1)),'date_evidence':dmatch.group(0),'catalog_source_id':r['source_id'],'catalog_source_path':r['path']})
    catalogs['CorporateCapitalAllocation'],selected_corp=select(corp)
    # The official governance landing page enumerates all three Code versions. Original dated releases verify publication.
    gov=[{'family':'GovernanceCrossShareholding','url':u,'published_date':d,'title':title,
          'date_evidence':'Original dated release body, verified after download','catalog_source_id':'jpx_governance_catalog','catalog_source_path':pages['jpx_governance_catalog'][0].get('path')}
          for d,u,title in [('2015-05-13','https://www.jpx.co.jp/english/news/1020/20150511-02.html','Formulation of Japan Corporate Governance Code'),
          ('2018-06-01','https://www.jpx.co.jp/english/news/1020/20180601.html','Publication of Revised Japan Corporate Governance Code'),
          ('2021-06-11','https://www.jpx.co.jp/english/news/1020/20210611-01.html','Publication of Revised Japan Corporate Governance Code')]]
    catalogs['GovernanceCrossShareholding'],selected_gov=select(gov)
    foreign=[]
    r,s=pages['jpx_foreign_catalog_2025']
    for u in re.findall(r'href="([^"]*stock_val_1_\d{6}\.pdf)"',s):
        code=re.search(r'_(\d{6})\.pdf',u).group(1)
        foreign.append({'family':'ForeignInvestors','url':urllib.parse.urljoin(r['url'],u),'observation_code':code,'published_date':None,
            'pit_status':'POINT_IN_TIME_UNCERTAIN','reason':'Weekly observation end/filename is not actual release date; no historical dated release proof identified','catalog_source_id':r['source_id'],'catalog_source_path':r.get('path')})
    foreign=sorted({r['url']:r for r in foreign}.values(),key=lambda r:r['observation_code'])
    n=len(foreign); fpos=list(range(n)) if n<=10 else [i*(n-1)//9 for i in range(10)]
    foreign_selected=[dict(foreign[i],catalog_index=i,catalog_n=n) for i in fpos]
    catalogs['ForeignInvestors']=foreign
    selection=selected_boj+selected_gpif+selected_gov+selected_corp
    # Lock catalog selection before interpreting any event, reading no price data.
    (REG/'catalogs.json').write_text(json.dumps(catalogs,ensure_ascii=False,indent=2))
    (REG/'selection.v001.json').write_text(json.dumps({'protocol':'BEHAVIORAL_EVENT_SELECTION_PROTOCOL.v001','rows':selection,'foreign_missing_slots':foreign_selected,
        'catalog_coverage':{'BOJ':'18 official annual statement catalogs; no claim that all BOJ operation flows are covered','GPIF':'PARTIAL_CATALOG: accessible English archive years only','ForeignInvestors':'PARTIAL_CATALOG: 2025 weekly Prime trading values; release dates uncertain','GovernanceCrossShareholding':'PARTIAL_CATALOG: 3 Code original/revisions; excludes full governance follow-up universe','CorporateCapitalAllocation':'PARTIAL_CATALOG: JPX company programs, source-accessibility example; not Japan corporate universe'}},ensure_ascii=False,indent=2))
    (REG/'selection.v001.sha256').write_text(hashlib.sha256((REG/'selection.v001.json').read_bytes()).hexdigest()+'\n')
    event_jobs=[]
    for i,r in enumerate(selection,1):
        ext='.pdf' if '.pdf' in r['url'].lower() else '.html'
        r['event_source_id']=f'jp_event_source_{i:03}'
        event_jobs.append((r['event_source_id']+ext,r['url'],'SELECTED_EVENT_SOURCE'))
    event_jobs += [(f'jp_foreign_missing_{i:02}.pdf',r['url'],'EXCLUDED_RELEASE_DATE_UNCERTAIN') for i,r in enumerate(foreign_selected,1)]
    event_jobs += [('boj_2024_exit.pdf','https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2024/k240319a.pdf','INSTITUTIONAL_CONTEXT_NOT_SELECTED_EVENT'),
                   ('boj_2025_disposal.pdf','https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2025/k250919a.pdf','INSTITUTIONAL_CONTEXT_NOT_SELECTED_EVENT'),
                   ('boj_2025_disposal_terms.html','https://www.boj.or.jp/en/mopo/measures/term_cond/etf_s1.htm','INSTITUTIONAL_CONTEXT_NOT_SELECTED_EVENT'),
                   ('gpif_2014_policy_mix.pdf','https://www.gpif.go.jp/en/performance/pdf/adoption_of_new_policy_asset_mix.pdf','INSTITUTIONAL_CONTEXT_NO_PUBLISH_DATE'),
                   ('jpx_capital_cost_request.html','https://www.jpx.co.jp/english/equities/listing/cg/tvdivq0000008jdy-att/20230331_e.pdf','INSTITUTIONAL_CONTEXT_VERIFY_ONLY')]
    fetch(event_jobs)
    (REG/'selected_source_assignment.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2))
    (OUT/'SOURCE_MANIFEST.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    print(json.dumps({'catalog_sizes':{k:len(v) for k,v in catalogs.items()},'selected':len(selection),'foreign_uncertain':len(foreign_selected),'fetch_failed':sum(r['status']=='FAILED' for r in records)},ensure_ascii=False))

if __name__=='__main__':main()
