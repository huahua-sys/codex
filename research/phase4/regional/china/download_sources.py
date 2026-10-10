#!/usr/bin/env python3
"""Preserve official source bytes and log failures. No prices; no result selection."""
import concurrent.futures, datetime, hashlib, json, pathlib, urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[2]/'sources'/'china'
ROOT.mkdir(parents=True,exist_ok=True)

def fetch(item):
 sid,url=item['source_id'],item['url']
 out=dict(item,retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 ResearchLab source archival'})
  with urllib.request.urlopen(req,timeout=25) as r:
   d=r.read();out.update(status=r.status,final_url=r.url,content_type=r.headers.get('Content-Type'))
  out['sha256']=hashlib.sha256(d).hexdigest();out['bytes']=len(d)
  suffix='.pdf' if d.startswith(b'%PDF') else '.html'
  dest=ROOT/(sid+suffix)
  if dest.exists() and dest.read_bytes()!=d:
   dest=ROOT/(sid+'.retrieval_'+out['sha256'][:12]+suffix)
  dest.write_bytes(d);out['path']=str(dest.relative_to(ROOT.parents[3]));out['status']='DOWNLOADED'
 except Exception as e:out.update(status='BLOCKED',error=type(e).__name__+': '+str(e))
 return out

def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument('plan');a.add_argument('receipt');x=a.parse_args()
 plan=json.loads(pathlib.Path(x.plan).read_text())
 results=list(concurrent.futures.ThreadPoolExecutor(max_workers=5).map(fetch,plan))
 pathlib.Path(x.receipt).write_text(json.dumps(results,ensure_ascii=False,indent=2))
 for z in results:print(z['source_id'],z['status'],z.get('bytes'),z.get('error',''))
if __name__=='__main__':main()
