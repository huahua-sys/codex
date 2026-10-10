#!/usr/bin/env python3
"""Fetch a small, fixed list of mechanism/measurement/rule sources, never event labels.
Each saved body is immutable by filename. Existing files must agree with ledger SHA.
These current reference pages are NOT point-in-time observations at a historical T.
"""
import concurrent.futures, datetime, hashlib, json, pathlib, re, subprocess, tempfile
import urllib.request, html
HERE=pathlib.Path(__file__).resolve().parent
SOURCES=[
('FW01','SEC T+1 implementation','2024-04-30','https://www.sec.gov/newsroom/press-releases/2024-62',['May 28, 2024','T+1']),
('FW02','SEC current Treasury clearing hub',None,'https://www.sec.gov/featured-topics/treasury-clearing-implementation',['Dec. 31, 2026','June 30, 2027']),
('FW03','SEC August 2026 Treasury clearing update','2026-08-07','https://www.sec.gov/newsroom/speeches-statements/uyeda-statement-update-secs-work-toward-treasury-clearing-implementation-080726-update-secs-work-toward-treasury-clearing-implementation-august-2026',['December 31, 2026','June 30, 2027','Dec. 31, 2026']),
('FW04','SEC Form 13F FAQ',None,'https://www.sec.gov/files/divisions/investment/13ffaq.htm',['45 days','$100 million','short positions']),
('FW05','SEC Insider transactions disclosure',None,'https://www.sec.gov/resources-small-businesses/going-public/officers-directors-10-shareholders',['two business days','Forms 3']),
('FW06','CFTC COT release calendar',None,'https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm',['Tuesday','Friday','3:30']),
('FW07','New York Fed primary dealer statistics',None,'https://www.newyorkfed.org/markets/counterparties/primary-dealers-statistics',['does not itself audit','weekly','fails']),
('FW08','OFR dealer release convention',None,'https://www.financialresearch.gov/short-term-funding-monitor/datasets/nypd/',['Thursday','prior week']),
('FW09','Fed Treasury holdings retrospective','2021-10-06','https://www.federalreserve.gov/econres/notes/feds-notes/sizing-hedge-funds-treasury-market-activities-and-holdings-20211006.html',['148 billion','173 billion','cash-futures']),
('FW10','Fed futures-liquidity counterevidence',None,'https://www.federalreserve.gov/econres/feds/market-liquidity-in-treasury-futures-market-during-march-2020.htm',['do not find evidence','basis traders']),
('FW11','NBER Coval Stafford fire-sales paper','2005-05','https://www.nber.org/papers/w11357',['capital flows','1980','2003']),
('FW12','BOJ ending new ETF purchases','2024-03-19','https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2024/k240319a.pdf',['ETFs','J-REITs','discontinue']),
('FW13','BOJ ETF disposal decision','2025-09-19','https://www.boj.or.jp/en/mopo/mpmdeci/state_2025/k250919a.htm',['330 billion','5 billion','temporarily adjust','suspend']),
('FW14','GPIF policy portfolio (current)','2025-04-01','https://www.gpif.go.jp/gpif/portfolio.html',['2025年4月1日','25%','乖離']),
('FW15','JPX equities investor trading (current)',None,'https://www.jpx.co.jp/markets/statistics-equities/investor-type/',['週間','2026','売買']),
('FW16','JPX derivatives publication guide',None,'https://www.jpx.co.jp/english/markets/statistics-derivatives/sector/b5b4pj0000008ox8-att/guide-en.pdf',['Thursday','15:30','prior']),
('FW17','CSRC actual versus lending-cap distinction','2024-10-18','https://www.csrc.gov.cn/csrc/c100028/c7513040/content.shtml',['3000亿元','贷款','回购']),
('FW18','CSRC securities relending suspension','2024-07-10','https://www.csrc.gov.cn/csrc/c100028/c7493852/content.shtml',['2024年7月11日','2024年7月22日','暂停']),
('FW19','SSE margin rule 2026 (current effective)','2026-01-14','https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/specific/margin/c/c_20260114_10805174.shtml',['2026年01月19日','现行有效','100%']),
('FW20','SSE previous margin regime','2023-08-27','https://www.sse.com.cn/aboutus/mediacenter/hotandd/c/c_20230827_5725661.shtml',['80%','2023年9月8日']),
('FW21','HKEX Northbound disclosure change','2024-07-26','https://www.hkex.com.hk/-/media/HKEX-Market/Services/Circulars-and-Notices/Participant-and-Members-Circulars/HKSCC/2024/ce_HKSCC_NOM_096_2024.pdf',['19 August 2024','quarterly','5th Northbound']),
('FW22','US Treasury auction data definition',None,'https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/treasury-securities-auctions-data',['auction','bids','accepted']),
('FW23','FINRA margin statistics definition',None,'https://www.finra.org/investors/learn-to-invest/advanced-investing/margin-statistics',['month','debit','FINRA']),
('FW24','Fed SLOOS releases',None,'https://www.federalreserve.gov/data/sloos.htm',['quarter','standards','2026']),
('FW25','BOJ current ETF operating page',None,'https://www.boj.or.jp/en/mopo/measures/mkt_ope/ope_t/index.htm',['2026','2025','ETFs']),
]

def fetch(s):
    sid,title,date,url,terms=s
    target=HERE/(sid+'.'+('pdf' if '.pdf' in url else 'html'))
    rec={'source_id':sid,'title':title,'url':url,'document_date_hint':date,'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'CURRENT_REFERENCE_OR_LATER_EXPLANATORY_ONLY','historical_event_admissible':False,'available_at_for_historical_replay':None,'date_hint_is_publication_proof':False}
    try:
        if target.exists(): body=target.read_bytes(); status=200; finalurl=url; rec['access']='EXISTING_NO_OVERWRITE'
        else:
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (Investment Research Lab evidence archive)'})
            with urllib.request.urlopen(req, timeout=30) as r:
                status=r.status; finalurl=r.url; body=r.read()
            if status!=200: raise RuntimeError('HTTP '+str(status))
            target.write_bytes(body)
        rec.update(http_status=status,final_url=finalurl,bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),path=str(target.relative_to(HERE)))
        if target.suffix=='.pdf':
            result=subprocess.run(['pdftotext','-layout',str(target),'-'],capture_output=True,check=True)
            text=result.stdout.decode('utf-8',errors='replace')
        else:
            decoded=body.decode('utf-8',errors='replace')
            decoded=re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ',decoded,flags=re.S|re.I)
            text=html.unescape(re.sub(r'<[^>]+>', ' ',decoded))
        text=re.sub(r'\s+',' ',text)
        excerpt=[]
        for term in terms:
            i=text.lower().find(term.lower())
            if i>=0:
                excerpt.append({'term':term,'excerpt':text[max(0,i-80):i+len(term)+120]})
        rec['matched_terms']=[e['term'] for e in excerpt]
        rec['excerpts']=excerpt
        # Store extracted full reference text separately. It is not any historical T's input.
        (HERE/(sid+'.extracted.txt')).write_text(text,encoding='utf-8')
        rec['status']='FETCHED_REFERENCE_NOT_PIT_EVENT'
    except Exception as e:
        rec.update(status='FETCH_FAILED_NO_SUBSTITUTION',error=str(e))
    return rec

if __name__=='__main__':
    ledger=HERE/'FRAMEWORK_SOURCE_LEDGER.v001.json'
    if ledger.exists(): raise SystemExit('Refusing to overwrite v001 ledger; make new version')
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool: records=list(pool.map(fetch,SOURCES))
    out={'version':'v001','purpose':'Mechanism, measurement and current-rule reference evidence; never historical replay inputs','sources':records}
    ledger.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'fetched':sum(x['status'].startswith('FETCHED') for x in records),'failed':[{'id':x['source_id'],'error':x.get('error')} for x in records if x['status'].startswith('FETCH_FAILED')]},ensure_ascii=False))
