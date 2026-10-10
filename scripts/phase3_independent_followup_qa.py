#!/usr/bin/env python3
"""Rebuild follow-up means from immutable rows without using study aggregation."""
import hashlib,json,math
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
checks=0;errors=[]
def check(ok,description):
    global checks
    checks+=1
    if not ok:errors.append(description)
def close(a,b):return (a is None and b is None) or (a is not None and b is not None and math.isclose(a,b,abs_tol=1e-11,rel_tol=1e-11))
features={p['point_id']:p for p in read('research/phase3/features/decision_points.v001.json')['points']}
labels={p['point_id']:p for part in ['development','holdout'] for p in read(f'research/phase3/labels/{part}.v001.json')['points']}
lookup={}
for pid,p in features.items():
    for h in ['12m','24m']:
        y=labels[pid]['horizons'][h]
        if p['feature_eligible'] and y['status']=='REVEALED':lookup[(pid,h)]=(p,y)
def class_name(p):
    if p['industry'] in ['Broad','Growth','Technology','Semiconductor','Financials_Banks','Industrials','Consumer','Healthcare','Energy_Resources','Utilities']:return 'EQUITY'
    return 'TREASURY_DURATION' if p['industry'].startswith('Treasury_') else p['industry']
def flag(p,v):
    fields={'H-P3-TREND':('features','trend_group','POSITIVE','NONPOSITIVE'),'H-P3-DRAWDOWN':('features','drawdown_group','LARGE_DRAWDOWN','OTHER'),'H-P3-VOL':('features','vol_group','HIGH','NOT_HIGH'),'H-P3-CREDIT':('credit','group','TIGHTENING','NOT_TIGHTENING')}
    section,key,yes,no=fields[v];z=p[section].get(key)
    if v=='H-P3-CREDIT' and (p['market']!='US' or p['credit']['status']!='KNOWN_AT_T'):return None
    return 1 if z==yes else 0 if z==no else None
def interval(cells):
    if not cells:return None
    buckets={}
    for c in cells:buckets.setdefault((int(c['quarter'][:4])-2000)//2,[]).append(c['return_difference'])
    block=list(sorted(buckets)); sums=np.array([sum(buckets[k]) for k in block]);counts=np.array([len(buckets[k]) for k in block]);idx=np.random.default_rng(20261009).integers(0,len(block),size=(500,len(block)));a=sums[idx].sum(1)/counts[idx].sum(1)
    return np.quantile(a,[.025,.975]).tolist()
matched=read('research/phase3/matched/RESULTS.v001.json')
for result in matched['results']:
    st=result['stratum'];v=result['variable'];h=result['horizon'];q={}
    for (pid,hh),(p,y) in lookup.items():
        if hh!=h or [p['market'],p['currency'],class_name(p),y.get('return_basis',p.get('return_basis'))]!=st:continue
        g=flag(p,v)
        if g is not None:q.setdefault(p['calendar_quarter'],{0:[],1:[]})[g].append((pid,y))
    allcells=[]
    for quarter,g in sorted(q.items()):
        if not all(g.values()):continue
        diff=sum(y['net_return'] for _,y in g[1])/len(g[1])-sum(y['net_return'] for _,y in g[0])/len(g[0]);md=sum(y['max_drawdown'] for _,y in g[1])/len(g[1])-sum(y['max_drawdown'] for _,y in g[0])/len(g[0]);allcells.append({'quarter':quarter,'return_difference':diff,'mdd_difference':md})
    check(len(allcells)==result['both_group_quarters'],'matched count '+str(st)+v+h)
    for key,col in [('return_contrast','return_difference'),('gross_MDD_contrast','mdd_difference')]:check(close(result[key]['mean'],sum(c[col] for c in allcells)/len(allcells) if allcells else None),'matched mean '+v+h+col)
    iv=interval(allcells);stored=result['return_contrast']['ci95'];check((iv is None and stored is None) or (iv is not None and all(close(a,b) for a,b in zip(iv,stored))),'matched interval '+v+h)
reg=read('research/phase3/vol_falsification/PREREGISTRATION.v001.json');out=read('research/phase3/vol_falsification/RESULTS.v001.json')
for result in out['comparisons']:
    h=result['horizon'];omit=result['variant'][5:] if result['variant'].startswith('OMIT_') else None;era=result['era'];q={}
    for (pid,hh),(p,y) in lookup.items():
        if hh!=h or p['asset_id'] not in reg['assets'] or p['asset_id']==omit:continue
        if era!='ALL' and not int(era[:4])<=p['year']<=int(era[5:]):continue
        g=flag(p,'H-P3-VOL')
        if g is not None:q.setdefault(p['calendar_quarter'],{0:[],1:[]})[g].append((pid,y))
    expected=[]
    for quarter,g in sorted(q.items()):
        if not all(g.values()):continue
        values=g[0]+g[1];expected.append({'quarter':quarter,'point_ids':sorted(pid for pid,_ in values),'entry':min(y['entry_date'] for _,y in values),'exit':max(y['exit_date'] for _,y in values),'return_difference':sum(y['net_return'] for _,y in g[1])/len(g[1])-sum(y['net_return'] for _,y in g[0])/len(g[0]),'mdd_difference':sum(y['max_drawdown'] for _,y in g[1])/len(g[1])-sum(y['max_drawdown'] for _,y in g[0])/len(g[0])})
    check(len(expected)==result['both_group_quarters'],'vol count '+str((h,omit,era)))
    for a,b in zip(expected,result['cells']):
        check(a['quarter']==b['quarter'] and a['point_ids']==sorted(b['point_ids']) and a['entry']==b['entry'] and a['exit']==b['exit'],'vol membership/date')
        check(close(a['return_difference'],b['return_difference']) and close(a['mdd_difference'],b['mdd_difference']),'vol cell arithmetic')
    check(close(result['return_contrast']['mean'],sum(c['return_difference'] for c in expected)/len(expected) if expected else None),'vol aggregate')
    check(all(close(a,b) for a,b in zip(interval(expected) or [],result['return_contrast']['ci95'] or [])),'vol interval')
for r in out['nonoverlap']:
    full=next(c for c in out['comparisons'] if c['horizon']==r['horizon'] and c['variant']=='ALL' and c['era']=='ALL');chosen=[];end=None
    for c in full['cells']:
        if end is None or c['entry']>end:chosen.append(c);end=c['exit']
    check(chosen==r['cells'],'nonoverlap actual greedy list')
    check(all(a['exit']<b['entry'] for a,b in zip(chosen,chosen[1:])),'nonoverlap strict boundary')
    check(close(r['return_contrast']['mean'],sum(c['return_difference'] for c in chosen)/len(chosen)),'nonoverlap arithmetic')
    check(all(close(a,b) for a,b in zip(interval(chosen),r['return_contrast']['ci95'])),'nonoverlap interval')
for p,h in read('research/phase3/audit/PRIOR_STATE.v001.json')['immutable_file_hashes'].items():check(sha(p)==h,'old immutable '+p)
framework=read('CURRENT_FRAMEWORK.json');baseline=read('research/phase3/audit/PRIOR_OPERATIVE_FRAMEWORK.v001.json')['operative_framework']
for k,v in baseline.items():check(framework[k]==v,'old operative '+k)
for path in ['research/phase3/matched/PREREGISTRATION.v001.json','research/phase3/vol_falsification/PREREGISTRATION.v001.json']:
    r=read(path)
    for p,h in r['sources'].items():check(sha(p)==h,'followup frozen source/code '+p)
result={'audit_id':'ROOT_INDEPENDENT_FOLLOWUP_QA_V001','created_at':datetime.now(timezone.utc).isoformat(),'RAW_OBSERVATIONS':{'new_investment_samples':0,'independent_engineering_checks':checks,'matched_slots':104,'sensitivity_slots':88,'nonoverlap_slots':2},'EFFECTIVE_SAMPLE_ASSESSMENT':{'n_effective':None,'QA_is_not_investment_evidence':True},'code_sha256':sha('scripts/phase3_independent_followup_qa.py'),'status':'PASS' if not errors else 'FAIL','errors':errors}
path=ROOT/'research/phase3/audit/ROOT_FOLLOWUP_QA.v001.json'
with path.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(result));raise SystemExit(bool(errors))
