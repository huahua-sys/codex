#!/usr/bin/env python3
"""Source-first exploratory Phase4 event reactions; never changes old results.

Raw open/close price returns exclude dividends and are not investable alpha.
Controls are retrospective similar price states, not identified counterfactuals.
Only publication-qualified events enter outcomes after a separate event lock.
"""
from __future__ import annotations
import argparse, bisect, calendar, hashlib, json, math, statistics
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/phase4'
HORIZONS = {'1w': (0, 7), '1m': (1, 0), '3m': (3, 0),
            '6m': (6, 0), '12m': (12, 0), '24m': (24, 0)}
GOOD_PIT = {'VERIFIED', 'VERIFIED_DATE_ONLY', 'VERIFIED_CONSERVATIVE_SESSION_LAG',
            'VERIFIED_DATE_CONSERVATIVE', 'VERIFIED_CONSERVATIVE_END_OF_DAY'}

def read(p): return json.loads(Path(p).read_text())
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def write_once(p, value):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with Path(p).open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')

def stamp(x):
    v = datetime.fromisoformat(x.replace('Z', '+00:00'))
    if v.tzinfo is None: raise ValueError('Timezone missing')
    return v

def months_after(d, n):
    m = d.month - 1 + n
    y = d.year + m // 12
    return date(y, m % 12 + 1, min(d.day, calendar.monthrange(y, m % 12 + 1)[1]))

def source(asset):
    p = ROOT / f'research/phase3/data/market/{asset}.canonical.json'
    body = read(p)
    rows = sorted(body['prices'], key=lambda x: x['date'])
    return rows, {'path': str(p.relative_to(ROOT)), 'sha256': digest(p),
                  'definition': 'CURRENT_VENDOR_RECONSTRUCTED_OPEN_CLOSE_PRICE_ONLY',
                  'original_quote_vintage_verified': False}

def features(rows, cutoff):
    # Slice only observations available before this decision's timestamp.
    past = [r for r in rows if stamp(r['available_at']) <= cutoff]
    if len(past) < 64: return None
    c = [float(r['close']) for r in past[-64:]]
    if not all(v > 0 and math.isfinite(v) for v in c): return None
    returns = [c[i] / c[i-1] - 1 for i in range(1, len(c))]
    return {'r63': c[-1] / c[0] - 1,
            'vol63': statistics.stdev(returns) * math.sqrt(252),
            'last_known_date': past[-1]['date']}

def reaction(rows, cutoff, horizon):
    eligible = [r for r in rows if stamp(r['session_open_at']) > cutoff]
    if not eligible: return {'status': 'NO_POST_PUBLICATION_OPEN'}
    entry = eligible[0]
    if not entry.get('open') or entry['open'] <= 0:
        return {'status': 'NOT_EXECUTION_IDENTIFIED'}
    n, days = HORIZONS[horizon]
    target = months_after(date.fromisoformat(entry['date']), n) + timedelta(days=days)
    future = [r for r in eligible if date.fromisoformat(r['date']) >= target]
    if not future: return {'status': 'PENDING_HORIZON', 'entry_date': entry['date'],
                           'target_date': target.isoformat()}
    exit_ = future[0]
    held = [r for r in eligible if r['date'] <= exit_['date']]
    price = float(entry['open'])
    closes = [float(r['close']) for r in held]
    wealth = [price] + closes
    peak = wealth[0]; drawdowns = []
    for v in wealth:
        peak = max(peak, v); drawdowns.append(v / peak - 1)
    gross = float(exit_['close']) / price - 1
    return {'status': 'REVEALED_PRICE_ONLY', 'entry_date': entry['date'],
            'entry_open_at': entry['session_open_at'], 'entry_open': price,
            'target_date': target.isoformat(), 'exit_date': exit_['date'],
            'exit_close': float(exit_['close']), 'gross_price_return': gross,
            'illustrative_20bp_roundtrip_return': gross - .002,
            'maximum_close_to_close_drawdown': min(drawdowns),
            'maximum_adverse_close_excursion': min(v / price - 1 for v in closes),
            'maximum_favorable_close_excursion': max(v / price - 1 for v in closes),
            'sessions': len(held), 'dividends_included': False,
            'session_dates_sha256': hashlib.sha256(json.dumps([r['date'] for r in held]).encode()).hexdigest()}

def control_pool(rows):
    chosen = {}; candidates = []
    for i, r in enumerate(rows):
        d = date.fromisoformat(r['date']); key = (d.year, (d.month-1)//3)
        if key not in chosen: chosen[key] = i
    for i in chosen.values():
        if i < 64: continue
        cutoff = stamp(rows[i]['session_open_at']) - timedelta(microseconds=1)
        feat = features(rows[:i], cutoff)
        if feat: candidates.append({'date': rows[i]['date'], 'cutoff': cutoff.isoformat(),
                                    'features': feat})
    return candidates

def select_controls(event, feat, pool, dates_in_family):
    t = stamp(event['available_at']).date()
    candidates = [c for c in pool if abs((date.fromisoformat(c['date'])-t).days) <= 366
                  and all(abs((date.fromisoformat(c['date'])-d).days) > 30 for d in dates_in_family)]
    if feat is None or len(candidates) < 3: return []
    s1 = statistics.pstdev([c['features']['r63'] for c in candidates]) or 1.
    s2 = statistics.pstdev([c['features']['vol63'] for c in candidates]) or 1.
    for c in candidates:
        c['distance'] = ((c['features']['r63']-feat['r63'])/s1)**2 + ((c['features']['vol63']-feat['vol63'])/s2)**2
    return sorted(candidates, key=lambda c: (c['distance'], c['date']))[:3]

def distribution(values):
    if not values: return {'n_raw': 0}
    x = np.asarray(values, dtype=float)
    return {'n_raw': len(x), 'mean': float(x.mean()), 'median': float(np.median(x)),
            'win_rate': float(np.mean(x > 0)), 'p25': float(np.quantile(x,.25)),
            'p75': float(np.quantile(x,.75)), 'worst_decile': float(np.quantile(x,.1)),
            'best_decile': float(np.quantile(x,.9)), 'min': float(x.min()), 'max': float(x.max())}

def clustered_interval(records, key):
    # Parent collapsing first; annual resampling retains common-year shocks.
    byparent = defaultdict(list)
    for r in records:
        if r.get(key) is not None: byparent[(r['parent_episode'],r['year'])].append(r[key])
    years = defaultdict(list)
    for (_, y), v in byparent.items(): years[y].append(statistics.mean(v))
    unique_parents = len({p for p, _ in byparent})
    if len(years) < 8 or unique_parents < 8:
        return {'status':'INSUFFICIENT_CLUSTER_CI', 'years':len(years),
                'unique_parents':unique_parents, 'parent_years':len(byparent)}
    ys = sorted(years); rng = np.random.default_rng(4102026)
    samples = [statistics.mean([v for y in rng.choice(ys, len(ys), replace=True) for v in years[int(y)]]) for _ in range(2000)]
    return {'status':'DESCRIPTIVE_YEAR_CLUSTER_BOOTSTRAP', 'years':len(ys),
            'parent_years':len(byparent), 'unique_parents':unique_parents,
            'replicates':2000, 'seed':4102026,
            'estimate_parent_collapsed':statistics.mean([v for vs in years.values() for v in vs]),
            'lower':float(np.quantile(samples,.025)), 'upper':float(np.quantile(samples,.975)),
            'independence_caveat':'Annual clusters may remain serially dependent; not independent causal trials.'}

def reveal():
    event_path = BASE/'data/events.all.v001.json'
    lock = read(BASE/'data/events.all.v001.lock.json')
    if digest(event_path) != lock['sha256']: raise ValueError('Event set changed after lock')
    for p, h in lock['source_files'].items():
        if digest(ROOT/p) != h: raise ValueError('Source changed after lock: '+p)
    body = read(event_path); events = body['events']
    cache = {a: source(a) for a in ['SPY','TLT','SSE','N225']}
    families = defaultdict(list)
    for e in events:
        if e.get('available_at'):
            families[(e['market'],e['family'])].append(stamp(e['available_at']).date())
    output = []
    for e in events:
        r = {'event_id':e['event_id'],'market':e['market'],'family':e['family'],
             'parent_episode':e['parent_episode'],'action_status':e['action_status'],
             'asset':e['study_asset'],'available_at':e.get('available_at'),
             'pit_status':e['pit_status'],'probability_forecast':None,
             'mechanism_identified':False, 'fundamental_solvency_identified':False}
        if e['pit_status'] not in GOOD_PIT or not e.get('available_at') or not e.get('source_proof_admitted'):
            r['status'] = 'POINT_IN_TIME_OR_SOURCE_UNCERTAIN'; output.append(r); continue
        rows, info = cache[e['study_asset']]; cutoff = stamp(e['available_at'])
        r.update(status='DESCRIPTIVE_EVENT_STUDY',year=cutoff.year, source=info,
                 features=features(rows,cutoff), horizons={})
        ctrls = select_controls(e,r['features'],control_pool(rows),families[(e['market'],e['family'])])
        r['matched_controls'] = ctrls
        for h in HORIZONS:
            obs = reaction(rows,cutoff,h)
            cr = [dict(control_date=c['date'],**reaction(rows,stamp(c['cutoff']),h)) for c in ctrls]
            usable = [c['gross_price_return'] for c in cr if c['status']=='REVEALED_PRICE_ONLY']
            m = statistics.mean(usable) if len(usable)==3 else None
            delta = obs.get('gross_price_return')-m if m is not None and obs['status']=='REVEALED_PRICE_ONLY' else None
            # Broad assets vs themselves cannot identify stock-selection alpha.
            benchmark_same_asset = 0. if obs['status']=='REVEALED_PRICE_ONLY' else None
            r['horizons'][h] = {'event':obs,'controls':cr,'control_mean_price_return':m,
                'matched_time_difference':delta,'same_asset_benchmark_difference':benchmark_same_asset,
                'benchmark_interpretation':'Broad-market exposure relative to itself is zero; matched-time difference is a state comparison, not alpha.',
                'result_class':('NEUTRAL' if abs(delta)<.02 else 'POSITIVE' if delta>0 else 'NEGATIVE') if delta is not None else 'UNIDENTIFIED'}
        output.append(r)
    write_once(BASE/'labels/event_reactions.v001.json',{'created_at_utc':now(),
        'event_lock_sha256':digest(BASE/'data/events.all.v001.lock.json'),
        'mode':'EXPLORATORY_NOT_BLIND_NOT_CAUSAL_NOT_NET_ALPHA','records':output})

def summarize():
    body=read(BASE/'labels/event_reactions.v001.json');rows=body['records'];slots=[];negative=[]
    groups=sorted(set((r['market'],r['family'],r['action_status']) for r in rows))
    for market,family,action in groups:
        selected=[r for r in rows if (r['market'],r['family'],r['action_status'])==(market,family,action)]
        for h in HORIZONS:
            mature=[r for r in selected if r.get('horizons',{}).get(h,{}).get('event',{}).get('status')=='REVEALED_PRICE_ONLY']
            paired=[r for r in mature if r['horizons'][h]['matched_time_difference'] is not None]
            cirows=[{'parent_episode':r['parent_episode'],'year':r['year'],
                'difference':r['horizons'][h]['matched_time_difference']} for r in paired]
            nonoverlap=[];last=None
            for r in sorted(mature,key=lambda r:(r['horizons'][h]['event']['entry_date'],r['event_id'])):
                obs=r['horizons'][h]['event']
                if last is None or obs['entry_date']>last:
                    nonoverlap.append(r);last=obs['exit_date']
            slots.append({'market':market,'family':family,'action_status':action,'horizon':h,
                'selected_raw':len(selected),'mature_raw':len(mature),'matched_raw':len(paired),
                'unique_parent':len(set(r['parent_episode'] for r in mature)),
                'unique_publication_dates':len(set(r['available_at'][:10] for r in mature)),
                'calendar_years':len(set(r['year'] for r in mature)),
                'effective_n':None,'actual_nonoverlap_raw':len(nonoverlap),
                'gross_price_return':distribution([r['horizons'][h]['event']['gross_price_return'] for r in mature]),
                'matched_time_difference':distribution([r['horizons'][h]['matched_time_difference'] for r in paired]),
                'maximum_drawdown':distribution([r['horizons'][h]['event']['maximum_close_to_close_drawdown'] for r in mature]),
                'matched_difference_interval':clustered_interval(cirows,'difference'),
                'independence_caveat':'Same mandate, global regime, overlapping returns and reused controls; no effective independent N identified.',
                'mechanism_status':'NOT_IDENTIFIED'})
            for r in paired:
                if r['horizons'][h]['matched_time_difference'] <= 0:
                    negative.append({'event_id':r['event_id'],'market':market,'family':family,
                        'horizon':h,'difference':r['horizons'][h]['matched_time_difference'],
                        'interpretation':'Counterexample to universal positive reaction; does not disprove participant mechanism.'})
    write_once(BASE/'analysis/event_study.results.v001.json',{'created_at_utc':now(),
        'label_sha256':digest(BASE/'labels/event_reactions.v001.json'),'comparison_slots':len(slots),
        'raw_event_records':len(rows),'independent_n':None,'probability_forecasts':0,
        'mechanisms_identified':0,'alpha_established':False,'slots':slots,'nonpositive_matched_cases':negative})

def engineering_check():
    # Delayed publication must not trade same-day or count an immature horizon.
    rows=[{'date':'2020-01-02','session_open_at':'2020-01-02T14:30:00+00:00','open':100.,'close':101.},
          {'date':'2020-01-03','session_open_at':'2020-01-03T14:30:00+00:00','open':110.,'close':120.},
          {'date':'2020-01-10','session_open_at':'2020-01-10T14:30:00+00:00','open':130.,'close':121.}]
    v=reaction(rows,stamp('2020-01-02T23:59:59+00:00'),'1w')
    assert v['entry_date']=='2020-01-03' and v['exit_date']=='2020-01-10'
    assert abs(v['gross_price_return']-.1)<1e-12
    assert reaction(rows,stamp('2020-01-02T23:59:59+00:00'),'12m')['status']=='PENDING_HORIZON'
    assert months_after(date(2020,1,31),1)==date(2020,2,29)
    assert clustered_interval([{'parent_episode':'one','year':2020,'difference':1.}]*20,'difference')['status']=='INSUFFICIENT_CLUSTER_CI'
    assert clustered_interval([{'parent_episode':'one','year':y,'difference':1.} for y in range(2010,2020)],'difference')['status']=='INSUFFICIENT_CLUSTER_CI'
    print('6 engineering guards PASS; synthetic values are not investment evidence.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['check','reveal','summarize']);a=p.parse_args()
    {'check':engineering_check,'reveal':reveal,'summarize':summarize}[a.action]()
