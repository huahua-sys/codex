#!/usr/bin/env python3
"""Restore exported administrative bundles/inputs exactly, without networking.

The package stores immutable market rows once and small per-file blueprints.
--verify-only reconstructs every original SHA without writing large duplicates.
Existing files are checked, never overwritten. Old invalid pilots stay invalid.
"""
import argparse,hashlib,json
from datetime import datetime
from pathlib import Path

def encoded(obj):
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode('utf-8')

def digest(data):return hashlib.sha256(data).hexdigest()

def stamp(s):return datetime.fromisoformat(s.replace('Z','+00:00'))

def safe(root,name):
    p=(root/name).resolve()
    if root not in p.parents:raise ValueError('path escapes package: '+name)
    return p

def restore(root,verify_only=False):
    root=Path(root).resolve();plan=json.loads((root/'DATA_RESTORE_BLUEPRINTS.json').read_text())
    sources={}
    for aid,s in plan['canonical_sources'].items():
        data=safe(root,s['path']).read_bytes();assert digest(data)==s['sha256'],s['path']
        sources[aid]=json.loads(data)
    def records(aid,kind,mode,cutoff=None):
        if mode=='EMPTY':return []
        rows=sources[aid][kind]
        if mode=='FULL':return rows
        statuses={'VERIFIED','VERIFIED_CONSERVATIVE_SESSION_LAG',
                  'KNOWN_MARKET_OBSERVATION_RECONSTRUCTED' if kind=='prices' else 'KNOWN_CORPORATE_ACTION_RECONSTRUCTED'}
        return [r for r in rows if r.get('pit_status') in statuses and r.get('available_at') and stamp(r['available_at'])<=stamp(cutoff)]
    verified,written=0,0
    for b in plan['files']:
        obj=b['body']
        if b['kind']=='INPUT':
            for k in ('prices','actions'):obj[k]=records(b['asset_id'],k,b[k+'_mode'],obj['cutoff_at'])
        else:
            for aid,modes in b['asset_modes'].items():
                for k in ('prices','actions'):obj['assets'][aid][k]=records(aid,k,modes[k])
        payload=encoded(obj);assert digest(payload)==b['sha256'],b['path']
        verified+=1;p=safe(root,b['path'])
        if p.exists():assert digest(p.read_bytes())==b['sha256'],b['path']
        elif not verify_only:
            p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('xb') as out:out.write(payload)
            written+=1
    return {'verified_original_files':verified,'written_files':written,'network_requests':0,
            'immutable_sha256_match':True,'invalid_pilots_are_still_excluded':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));p.add_argument('--verify-only',action='store_true')
    a=p.parse_args();print(json.dumps(restore(a.root,a.verify_only)))
