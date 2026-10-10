#!/usr/bin/env python3
"""Phase4 US original-source acquisition; no price/outcome access.

Standard library only. Catalog keyword rules are structural participant/action
rules, not return filters. Immutable cache prevents hidden source replacement.
"""
import concurrent.futures as cf
import hashlib, html, json, re, urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlencode

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'research/phase4/regional/us'
SRC=ROOT/'research/phase4/sources/us'
UA='Mozilla/5.0 InvestmentResearchLab archival research'

class Parser(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.a=None; self.buf=[]; self.skip=0; self.text=[]
    def handle_starttag(self,t,a):
        d=dict(a)
        if t in ('script','style'): self.skip+=1
        if t=='a': self.a=d.get('href'); self.buf=[]
        if t in ('p','div','br','h1','h2','h3','tr'): self.text.append('\n')
    def handle_endtag(self,t):
        if t in ('script','style'): self.skip=max(0,self.skip-1)
        if t=='a' and self.a: self.links.append((self.a,' '.join(self.buf))); self.a=None
    def handle_data(self,d):
        if self.skip:return
        self.text.append(d)
        if self.a:self.buf.append(d)

def digest(b):return hashlib.sha256(b).hexdigest()
def savej(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def fetch(url,role='original_release'):
    key=digest(url.encode())[:20]; meta=SRC/(key+'.source.json'); raw=SRC/(key+'.html')
    if meta.exists():return json.loads(meta.read_text())
    m={'source_id':'US_SOURCE_'+key,'url':url,'role':role,'accessed_at':datetime.now(timezone.utc).isoformat(),'source_path':str(raw.relative_to(ROOT)), 'revision_risk':'Currently hosted official original page, not contemporaneous archive; silent site corrections remain possible.'}
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=30) as r:
            b=r.read();m.update(http_status=r.status,final_url=r.url,content_type=r.headers.get('Content-Type'),source_sha256=digest(b),bytes=len(b));raw.write_bytes(b)
        p=Parser();p.feed(b.decode('utf-8','replace'));txt='\n'.join(re.sub(r'\s+',' ',x).strip() for x in ''.join(p.text).split('\n') if x.strip())
        textpath=SRC/(key+'.txt');textpath.write_text(txt);m['text_path']=str(textpath.relative_to(ROOT));m['text_sha256']=digest(txt.encode())
    except Exception as e:m.update(http_status=None,error=str(e))
    savej(meta,m);return m

def links(meta):
    if not meta.get('source_sha256'):return []
    p=Parser();p.feed((ROOT/meta['source_path']).read_text(errors='replace'));return p.links
def choose(records):
    records=sorted(records,key=lambda x:(x['date'],x['url']))
    ix=sorted(set((i*(len(records)-1))//9 for i in range(10))) if len(records)>10 else range(len(records))
    return [dict(records[i],catalog_index=i,catalog_n=len(records)) for i in ix]

def main():
    OUT.mkdir(parents=True,exist_ok=True);SRC.mkdir(parents=True,exist_ok=True)
    if (OUT/'selected_source_slots.v001.json').exists():
        raise SystemExit('Existing source selection is preserved. Do not rerun over v001; use a new preregistered acquisition directory/version for additional sources.')
    fedurls=['https://www.federalreserve.gov/newsevents/pressreleases/'+(str(y)+'all.htm' if y<2016 else str(y)+'-press.htm') for y in range(2008,2026)]
    securls=['https://www.sec.gov/newsroom/press-releases?'+urlencode({'year':y,'combine':'money market'}) for y in range(2008,2026)]
    msft=[{'url':f'https://www.microsoft.com/en-us/Investor/earnings/FY-{y}-Q4/press-release-webcast','date':f'{y}-07-01','year':y,'title':f'Microsoft FY{y} Q4 official earnings release'} for y in range(2008,2026)]
    # Lock source universe and title rules before reading source body or outcome.
    design={'mode':'EXPLORATORY_SOURCE_FIRST','period':[2008,2025],'fed_catalogs':fedurls,'sec_catalogs':securls,'corporate_universe':msft,'corporate_scope':'Single current issuer MSFT; yearly FY Q4 enumerated 2008–2025; missing endpoints retained. This is not a broad corporate census.','liquidity_title_regex':'announces results of auction','regulatory_title_regex':'(final rule|final rules|adopts|approves).*?(capital|liquidity|leverage|stress|resolution|Volcker)|(capital|liquidity|leverage).*?(final rule|final rules)','fund_title_regex':'(adopts|approves|amends|amendments|extends|withdraws|reforms).*?(money market)|(money market).*?(adopts|approves|amends|amendments|extends|withdraws|reforms)','equisequence':'floor(i*(n-1)/9), i=0..9; fewer than 10 all; retain missing selected endpoints; no replacement'}
    dp=OUT/'acquisition_design.v001.json'
    if not dp.exists():savej(dp,design)
    else:assert json.loads(dp.read_text())==design
    results={}
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for m in ex.map(lambda u:fetch(u,'official_catalog'),fedurls+securls):results[m['url']]=m
    liq=[];reg=[];fund=[];bad=[]
    for u in fedurls:
        m=results[u]
        if not m.get('source_sha256'):bad.append(m);continue
        for href,title in links(m):
            match=re.search(r'/(monetary|bcreg)(\d{8})[a-z]?\.htm',href)
            if not match:continue
            date=match[2][:4]+'-'+match[2][4:6]+'-'+match[2][6:]
            rec={'url':urljoin(u,href),'date':date,'title':html.unescape(title),'catalog_source_id':m['source_id'],'catalog_source_path':m['source_path']}
            if re.search(design['liquidity_title_regex'],title,re.I):liq.append(rec)
            if re.search(design['regulatory_title_regex'],title,re.I):reg.append(rec)
    for u in securls:
        m=results[u]
        if not m.get('source_sha256'):bad.append(m);continue
        # Detect pagination; preserve incomplete-catalog status, do not silently claim census.
        for href,title in links(m):
            if not re.search(r'/newsroom/press-releases/\d{4}-\d+$',href):continue
            if not re.search(design['fund_title_regex'],title,re.I):continue
            year=re.search(r'/(\d{4})-\d+$',href)[1]
            fund.append({'url':urljoin(u,href),'date':year+'-01-01','title':html.unescape(title),'catalog_source_id':m['source_id'],'catalog_source_path':m['source_path']})
    def uniq(rs):return list({x['url']:x for x in rs}.values())
    catalogs={'central_bank_liquidity_execution':uniq(liq),'regulatory_capital_constraints':uniq(reg),'passive_and_fund_constraints':uniq(fund),'corporate_capital_allocation':msft}
    # SEC precise dates are unknown until original page read. Fetch all structurally qualified candidate pages for dates.
    allfund=[]
    for r in catalogs['passive_and_fund_constraints']:
        m=fetch(r['url']);text=(ROOT/m['text_path']).read_text() if m.get('text_path') else ''
        dates=re.findall(r'(?:Washington D\.C\.,\s*)?((?:January|February|March|April|May|June|July|August|September|October|November|December|Jan\.|Feb\.|Mar\.|Apr\.|Aug\.|Sept\.|Oct\.|Nov\.|Dec\.)\s+\d{1,2},\s+\d{4})',text)
        if dates:
            d=dates[0].replace('Sept.','Sep.');fmt='%B %d, %Y' if '.' not in d else '%b. %d, %Y'
            try:r['date']=datetime.strptime(d,fmt).strftime('%Y-%m-%d')
            except ValueError:pass
        r['original_source_id']=m['source_id'];allfund.append(r)
    catalogs['passive_and_fund_constraints']=allfund
    savej(OUT/'catalogs.v001.json',{'catalogs':catalogs,'catalog_status':{'fed':'OFFICIAL_YEAR_ARCHIVE_TITLE_CLASSIFICATION; failed years retained','sec':'PARTIAL_CATALOG: first filtered page per year; pagination not fully crawled; narrower money-market rule universe, not ETF flows','corporate':'PARTIAL_CATALOG: fixed MSFT FY Q4 endpoints; no survivor-adjusted corporate census'},'failed_catalogs':bad})
    chosen={k:choose(v) for k,v in catalogs.items()}
    savej(OUT/'selected_source_slots.v001.json',chosen)
    urls=list(dict.fromkeys(r['url'] for rs in chosen.values() for r in rs))
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for m in ex.map(fetch,urls):results[m['url']]=m
    savej(OUT/'source_manifest.v001.json',{'records':[json.loads(p.read_text()) for p in sorted(SRC.glob('*.source.json'))]})
    print(json.dumps({'catalog_counts':{k:len(v) for k,v in catalogs.items()},'selected_counts':{k:len(v) for k,v in chosen.items()},'failed_catalogs':len(bad),'source_count':len(list(SRC.glob('*.source.json')))},indent=2))

if __name__=='__main__':main()
