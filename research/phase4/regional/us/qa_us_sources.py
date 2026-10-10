#!/usr/bin/env python3
"""Verify original US evidence bytes and append-only event wording overlay."""
import json,hashlib
from pathlib import Path
from acquire_us_sources import ROOT,OUT,SRC,savej,digest

def main():
    problems=[];checks=0
    for v,file in [('v001','events.json'),('v002','events.v002.json')]:
        lock=json.loads((OUT/f'events.lock.{v}.json').read_text());checks+=1
        if digest((OUT/file).read_bytes())!=lock['sha256']:problems.append('EVENT_LOCK_MISMATCH_'+v)
    old=json.loads((OUT/'events.json').read_text());new=json.loads((OUT/'events.v002.json').read_text());assert len(old)==len(new)==42
    immutable=['event_id','published_date','available_at','timezone','family','parent_episode','selection_basis','source_paths','source_urls','source_sha256','action_type','action_status','outcomes']
    for a,b in zip(old,new):
        for field in immutable:
            checks+=1
            if a[field]!=b[field]:problems.append(a['event_id']+':IMMUTABLE_'+field)
        checks+=1
        if (a['flow_size'] or {}).get('value')!=(b['flow_size'] or {}).get('value'):problems.append(a['event_id']+':AMOUNT_CHANGED')
        checks+=1
        if len(a['source_paths'])!=len(a['source_sha256']):problems.append(a['event_id']+':SOURCE_GRAIN')
        for path,sha in zip(a['source_paths'],a['source_sha256']):
            checks+=1
            if not (ROOT/path).is_file() or digest((ROOT/path).read_bytes())!=sha:problems.append(a['event_id']+':SOURCE_SHA')
        checks+=1
        if a['publication_date_precision']=='DATE' and 'T23:59:59' not in a['available_at']:problems.append(a['event_id']+':DATE_PRECISION_NOT_CONSERVATIVE')
        if a['flow_size'] and (not a['flow_size'].get('currency') or not isinstance(a['flow_size']['value'],(float,int))):problems.append(a['event_id']+':FLOW_SCHEMA')
    participants=json.loads((OUT/'participants.v001.json').read_text());keys=[k for k in participants[0] if k not in ['participant_id','name','source_ids','source_urls','source_paths','source_sha256','evidence_level','interpretation_boundary']]
    assert len(keys)==20 and len(participants)==22
    for p in participants:
        for k in keys:
            checks+=1
            if not p.get(k):problems.append(p['participant_id']+':EMPTY_'+k)
        checks+=1
        if not p['source_ids']:problems.append(p['participant_id']+':NO_OFFICIAL_REFERENCE')
    for path in SRC.glob('*.source.json'):
        m=json.loads(path.read_text())
        if not m.get('source_sha256'):continue
        checks+=1
        if digest((ROOT/m['source_path']).read_bytes())!=m['source_sha256']:problems.append(path.name+':RAW_SOURCE_SHA')
    report={'status':'PASS' if not problems else 'FAIL','checks':checks,'problems':problems,'n_raw_us':42,'n_effective':'UNKNOWN; program/issuer/quarter/global clustering','actors':22,'fields_per_actor':20,'old_source_and_outcome_immutable':True,'v002_is_post_global_reveal_documentary_overlay':True,'tested_return_edge':False,'sec_legacy_route_gaps':3,'selected_slot_missing':1,'source_coverage_not_complete':True}
    savej(OUT/'qa.v002.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))
    if problems:raise SystemExit(1)

if __name__=='__main__':main()
