#!/usr/bin/env python3
"""Freeze regional primary-source records and produce inspectable evidence cards.
No price data or future labels are opened by this collector.
"""
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/phase4'
REGIONS={'us':('US','SPY'), 'china':('China','SSE'), 'japan':('Japan','N225')}
GOOD={'VERIFIED','VERIFIED_DATE_ONLY','VERIFIED_CONSERVATIVE_SESSION_LAG',
      'VERIFIED_DATE_CONSERVATIVE','VERIFIED_CONSERVATIVE_END_OF_DAY'}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_once(p,body):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    with Path(p).open('x') as f:
        json.dump(body,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def safe_path(value):
    p=Path(value);p=p if p.is_absolute() else ROOT/p
    p=p.resolve()
    if ROOT not in p.parents or not p.is_file():return None
    return p

def main():
    files={};events=[];inputs={};missing=[]
    for region,(market,asset) in REGIONS.items():
        path=BASE/f'regional/{region}/events.json'
        if not path.is_file():raise FileNotFoundError(path)
        inputs[str(path.relative_to(ROOT))]=sha(path)
        body=json.loads(path.read_text()); records=body if isinstance(body,list) else body['events']
        for original in records:
            e=dict(original)
            if e['market']!=market:raise ValueError('Wrong market '+e['event_id'])
            required=['event_id','family','parent_episode','pit_status','action_status',
                      'participant_type','constraint','observed_action','known_at_t','unknown_at_t']
            for k in required:
                if k not in e:raise ValueError(f'{e["event_id"]}: missing {k}')
            e['study_asset']=asset
            if market=='US' and any(x in str(e['family']).lower() for x in ['treasury','repo','funding']):e['study_asset']='TLT'
            paths=[]
            for value in e.get('source_paths',[]):
                p=safe_path(value)
                if p:
                    rel=str(p.relative_to(ROOT));paths.append(rel);files[rel]=sha(p)
                else:missing.append({'event_id':e['event_id'],'missing_source_path':value})
            proof=e.get('publication_date_evidence') or e.get('published_date_evidence')
            e['source_proof_admitted']=bool(paths and proof and e.get('available_at') and e['pit_status'] in GOOD)
            e['source_paths']=paths
            e['source_file_hashes']={p:files[p] for p in paths}
            e['publication_date_evidence']=proof
            e['original_quote_vintage_verified']=False
            e['independent_first_publication_archive_verified']=False
            e['price_study_scope']='BROAD_MARKET_CONTEXT_NOT_ISSUER_OR_FLOW_CAUSAL_EFFECT'
            e['classification_at_t']='UNCLEAR_UNLESS_INDEPENDENT_ASSET_SOLVENCY_AND_HOLDER_EVIDENCE'
            e['probability_forecast']=None
            e['historical_future_memory_risk']='MODEL_OR_PRIOR_RESEARCH_MAY_ALREADY_KNOW_HISTORY'
            events.append(e)
    assert len(events)==len({e['event_id'] for e in events}), 'Duplicate event IDs'
    events.sort(key=lambda e:(e['market'],e.get('published_date') or '',e['event_id']))
    path=BASE/'data/events.all.v001.json'
    write_once(path,{'created_at_utc':datetime.now(timezone.utc).isoformat(),
        'mode':'EXPLORATORY_SOURCE_FIRST_NOT_BLIND','new_probability_forecasts':0,
        'regional_inputs':inputs,'events':events,'missing_source_references':missing})
    script=ROOT/'scripts/phase4_event_study.py'
    lock={'locked_at_utc':datetime.now(timezone.utc).isoformat(),
          'path':str(path.relative_to(ROOT)),'sha256':sha(path),'regional_inputs':inputs,
          'source_files':files,'code_files':{str(script.relative_to(ROOT)):sha(script)},
          'new_event_labels_read_before_lock':False,'prior_historical_outcomes_may_be_known':True}
    write_once(BASE/'data/events.all.v001.lock.json',lock)
    for e in events:
        eid=e['event_id']
        write_once(ROOT/f'research/behavioral_events/{eid}.v001.json',e)
        card={k:e.get(k) for k in ['event_id','market','published_date','available_at','participant_type',
            'observed_action','constraint','action_status','flow_size','flow_duration','voluntary_or_forced',
            'source_paths','source_urls','source_file_hashes','source_excerpt','publication_date_evidence',
            'source_proof_admitted','mechanism','alternative_explanation','falsifier','confidence_level']}
        card.update(evidence_id='EC-'+eid, costliness_of_action='UNASSESSED_UNLESS_ORIGINAL_SOURCE_QUANTIFIES_COMMITTED_COST',
                    independent_evidence='Same issuer reposts are not independent confirmation.',
                    potential_size_interpretation='Capacity/authorization/holdings are not executed marginal flow.',
                    evidence_scope='Participant action and disclosure evidence; no correctness or tradable-edge inference.')
        write_once(ROOT/f'research/evidence_cards/EC-{eid}.v001.json',card)
    print(json.dumps({'events':len(events),'source_proof_admitted':sum(e['source_proof_admitted'] for e in events),
                      'unique_parent_episodes':len({e['parent_episode'] for e in events}),
                      'source_files':len(files),'missing_source_references':len(missing)},indent=2))

if __name__=='__main__':main()
