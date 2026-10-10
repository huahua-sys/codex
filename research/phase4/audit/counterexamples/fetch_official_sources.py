#!/usr/bin/env python3
"""Non-price, retrospective mechanism audit: original bytes only; no research results altered."""
import concurrent.futures, datetime, hashlib, json, pathlib, subprocess, urllib.request
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[4]; DEST=ROOT/'sources/counterexamples';AUDIT=ROOT/'research/phase4/audit/counterexamples'
SOURCE_URLS={
'FSB_2020_11_17_HOLISTIC_REVIEW':'https://www.fsb.org/wp-content/uploads/P171120-2.pdf',
'FCIC_2011_FINANCIAL_CRISIS':'https://www.govinfo.gov/content/pkg/GPO-FCIC/pdf/GPO-FCIC.pdf',
'FED_2020_06_25_BANK_DISTRIBUTIONS':'https://www.federalreserve.gov/newsevents/pressreleases/bcreg20200625c.htm',
'FED_2020_03_23_LIQUIDITY':'https://www.federalreserve.gov/newsevents/pressreleases/monetary20200323b.htm',
'BOJ_2024_03_19_END_ETF_PURCHASES':'https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2024/k240319a.pdf',
'SEC_2022_12_14_INSIDER_PLANS':'https://www.sec.gov/newsroom/press-releases/2022-222',
'FED_2020_11_09_STABILITY':'https://www.federalreserve.gov/publications/files/financial-stability-report-20201109.pdf',
'BERKSHIRE_2008_SHAREHOLDER_LETTER':'https://www.berkshirehathaway.com/letters/2008ltr.pdf',
'IEA_2022_PV_SUPPLY_CHAINS':'https://www.iea.org/reports/solar-pv-global-supply-chains/executive-summary',
'GE_2017_ANNUAL_REPORT':'https://www.ge.com/sites/default/files/GE_AR17.pdf'
}
class HTMLText(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.suppress=0
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.suppress+=1
  if t in ['p','br','div','li','h1','h2','h3']:self.parts.append('\n')
 def handle_endtag(self,t):
  if t in ['script','style']:self.suppress=max(0,self.suppress-1)
 def handle_data(self,d):
  if not self.suppress:self.parts.append(d)
def fetch(it):
 key,url=it;stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'InvestmentResearchLab public source audit contact research@example.org'}),timeout=45) as r:b=r.read();status=r.status;ct=r.headers.get('content-type','');resolved=r.url
  suffix='.pdf' if b.startswith(b'%PDF') else '.html'
  p=DEST/(key+suffix)
  if p.exists() and p.read_bytes()!=b:raise RuntimeError('existing source differs; preserve old and add a new version')
  p.write_bytes(b)
  txt=AUDIT/(key+'.extracted.txt')
  if suffix=='.pdf':subprocess.run(['pdftotext','-layout',str(p),str(txt)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  else:
   parser=HTMLText();parser.feed(b.decode('utf-8',errors='replace'));txt.write_text(''.join(parser.parts),encoding='utf-8')
  return {'id':key,'requested_url':url,'resolved_url':resolved,'retrieved_at':stamp,'status':status,'content_type':ct,'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'extract_path':str(txt.relative_to(ROOT)),'available_at':'POINT_IN_TIME_UNCERTAIN_UNTIL_DATE_EVIDENCE_REVIEWED','scope':'RETROSPECTIVE_MECHANISM_AUDIT_NOT_BLIND_SIGNAL'}
 except Exception as e:return {'id':key,'requested_url':url,'retrieved_at':stamp,'error':str(e),'status':'FETCH_FAILED_RETAINED'}
with concurrent.futures.ThreadPoolExecutor(8) as ex:rows=list(ex.map(fetch,SOURCE_URLS.items()))
(AUDIT/'source_fetch_manifest.v001.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for r in rows:print(r['id'],r['status'],r.get('bytes',r.get('error')))
