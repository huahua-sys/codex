#!/usr/bin/env python3
"""Administrator acquisition after protocol lock. Never changes earlier sources."""
import concurrent.futures,datetime as dt,hashlib,json,shutil,sys
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import download_market_data as old
from lab.schema import write_once,sha256
DEST=ROOT/'research/phase3/data/market'

def run():
    lock=json.loads((ROOT/'research/phase3/PROTOCOL.lock.v001.json').read_text())
    for f,h in lock['files'].items():
        assert sha256(ROOT/f)==h,f
    design=json.loads((ROOT/'research/phase3/design.v001.json').read_text())
    registration=ROOT/'research/phase3/data/MARKET_ACQUISITION.lock.v001.json'
    if registration.exists():raise ValueError('Already registered; do not redownload a new source version')
    write_once(registration,{'registered_at':dt.datetime.now(dt.timezone.utc).isoformat(),'protocol_sha':sha256(ROOT/'SAMPLE_EXPANSION_PROTOCOL.md'),'code_sha':sha256(__file__),'old_helper_sha':sha256(ROOT/'scripts/download_market_data.py'),'source_end_exclusive':design['source_end_exclusive'],'scope':'ADMIN_ONLY_FUTURE_NOT_FEATURES'})
    prior_boundaries=old.boundaries
    def boundaries(day,market,zone):
        clocks={'EU':(dt.time(9),dt.time(18)),'DE':(dt.time(9),dt.time(17,30)),'UK':(dt.time(8),dt.time(16,30))}
        if market not in clocks:return prior_boundaries(day,market,zone)
        tz=ZoneInfo(zone);o,c=clocks[market]
        return tuple(old.iso(x) for x in (dt.datetime.combine(day,o,tz),dt.datetime.combine(day,c,tz),dt.datetime.combine(day+dt.timedelta(days=1),dt.time(0),tz)))
    old.boundaries=boundaries
    for a in design['assets']:
        aid=a['asset_id'];previous=old.ASSETS.get(aid)
        old.ASSETS[aid]=(a['symbol'],a['market'],a['currency'],a['instrument_type'],a['industry'],a['timezone'],previous[-1] if previous else 'NOT_USED_FOR_HISTORICAL_ADMISSION')
    DEST.mkdir(parents=True,exist_ok=True)
    def get(a):
        aid=a['asset_id'];r=old.acquire(aid,'2000-01-01','2026-10-08','PHASE3')
        temp=ROOT/'data/raw/phase3/market'
        cp=temp/(aid+'.canonical.json');rp=temp/(aid+'.yahoo.raw.json')
        if cp.exists():
            b=json.loads(cp.read_text())
            b['metadata']['raw_path']=str((DEST/rp.name).relative_to(ROOT))
            b['metadata']['panel_industry']=a['industry']
            b['metadata']['native_level_basis']='INDEX_PERFORMANCE_EMBEDDED_DIVIDENDS' if aid=='DAX' else 'INDEX_PRICE_LEVEL' if a['instrument_type']=='INDEX' else 'ETF_PROVIDER_ACTION_ECONOMIC_RETURN'
            b['metadata']['historical_action_admission']='UNKNOWN_SPLIT_QUARANTINE' if b['metadata'].get('split_action_validation_required') else 'NO_SPECIAL_ACTION_FLAGGED_PROVIDER_CONDITIONAL'
            if aid=='DAX':
                raw=json.loads(rp.read_text());meta=raw['chart']['result'][0]['meta']
                b['metadata']['native_level_evidence']={'provider_longName':meta.get('longName'),'provider_shortName':meta.get('shortName'),'provider_symbol':meta.get('symbol'),'scope':'Provider-labelled native index; not a separate investible return or historic constituent archive'}
            write_once(DEST/cp.name,b);cp.unlink()
            if rp.exists():shutil.move(str(rp),DEST/rp.name)
            r['canonical_path']=str((DEST/cp.name).relative_to(ROOT));r['canonical_sha256']=sha256(DEST/cp.name)
            r['metadata']=b['metadata']
        elif (ROOT/f'data/raw/round_002/market/{aid}.canonical.json').exists():
            src=ROOT/f'data/raw/round_002/market/{aid}.canonical.json';shutil.copyfile(src,DEST/src.name)
            r.update(fallback='FIXED_EXISTING_SOURCE_NO_DATE_EXTENSION',canonical_path=str((DEST/src.name).relative_to(ROOT)),canonical_sha256=sha256(DEST/src.name))
        if rp.exists():shutil.move(str(rp),DEST/rp.name)
        print(json.dumps({'asset':aid,'status':r['status'],'rows':r.get('metadata',{}).get('row_count'),'splits':r.get('metadata',{}).get('split_count'),'fallback':r.get('fallback'),'error':r.get('error')},ensure_ascii=False),flush=True)
        return aid,r
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results=dict(pool.map(get,design['assets']))
    write_once(ROOT/'research/phase3/data/MARKET_SOURCES.v001.json',{'completed_at':dt.datetime.now(dt.timezone.utc).isoformat(),'sources':results,'scope':'Current provider history, not original market vintages; provider corrections and surviving instruments remain biases'})
    print(json.dumps({'sources':len(results),'success':sum(x['status']=='SUCCESS' for x in results.values()),'manifest':'research/phase3/data/MARKET_SOURCES.v001.json'}))

if __name__=='__main__':run()
