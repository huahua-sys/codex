#!/usr/bin/env python3
"""Administrative adapter: frozen public-source files -> masked replay batch.

Never computes outcomes. Subprocess Stage A receives only filtered packets.
"""
import argparse
import copy
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab.schema import read_json, sha256, utc_now, write_once
from lab.select import select_episodes
from scripts.import_dataset import import_dataset

ROOT = Path(__file__).resolve().parents[1]

def build(name, asset_ids, years, month_day='09-30'):
    folder = ROOT/'research/replays'/name
    folder.mkdir(parents=True, exist_ok=True)
    assets, universe, sources = {}, [], {}
    official = ROOT/'data/raw/round_002/official/release_records.json'
    releases = read_json(official) if official.exists() else []
    for aid in asset_ids:
        path = ROOT/'data/raw/round_002/market'/f'{aid}.canonical.json'
        raw = read_json(path)
        meta = copy.deepcopy(raw['metadata'])
        meta['original_vintage_status'] = 'NOT_ARCHIVED_PROVIDER_CORRECTIONS_POSSIBLE'
        meta['return_basis'] = 'TOTAL_RETURN' if meta['instrument_type']=='ETF' else 'PRICE_ONLY'
        meta['tradability'] = 'EXCHANGE_TRADED_ETF' if meta['instrument_type']=='ETF' else 'NONTRADABLE_INDEX'
        unavailable=aid=='XLF'
        if unavailable:
            # No prices/actions are asserted. This is only the expected units
            # contract for an empty, deliberately unresolved packet.
            meta['excluded_source_price_basis']=meta['price_basis']
            meta['price_basis']='UNADJUSTED'
            meta['quarantine_reason']='SOURCE_CORPORATE_ACTION_UNITS_UNRESOLVED_NO_OBSERVATIONS_ADMITTED'
        if not unavailable and meta['instrument_type']=='ETF' and (meta.get('split_action_validation_required') or not meta.get('total_return_eligible', True)):
            raise ValueError(f'{aid}: action validation needed before total-return replay')
        context=[]
        if meta['market']=='US':
            for row in releases:
                if row['pit_status']!='VERIFIED': continue
                r=copy.deepcopy(row)
                r['category']={'policy':'Policy','inflation':'Inflation'}[r['category']]
                context.append(r)
                if r['category']=='Policy':
                    rates=copy.deepcopy(r);rates['record_id']+='-RATES';rates['category']='Rates'
                    rates['value']=rates['fields'];context.append(rates)
        assets[aid]={'currency':meta['currency'],'instrument_type':meta['instrument_type'],
                     'cost_bps_roundtrip':50.,'metadata':meta,'prices':[] if unavailable else raw['prices'],
                     'actions':[] if unavailable else raw['actions'],'context':context,
                     'coverage_end':raw['coverage_end'],'action_coverage':raw['action_coverage']}
        universe.append({'asset_id':aid,'market':meta['market'],'inception_date':meta['inception_reference_date']})
        sources[aid]={'path':str(path.relative_to(ROOT)),'sha256':sha256(path),
                      'source_sha256':meta['source_sha256']}
    bundle={'batch_id':name,'created_at':utc_now(),'role':'ADMINISTRATIVE_FULL_HISTORY_NOT_STAGE_A',
            'not_original_quote_vintage':True,'assets':assets,'source_manifest':sources}
    bundle_path=folder/'admin_bundle.v001.json'
    selection_path=folder/'selection.v001.json'
    prereg_path=folder/'preregistration.v001.json'
    selection=select_episodes(universe,[f'{y}-{month_day}' for y in years],round_id=name)
    selection['batch_role']='EXPLORATORY' if name=='ROUND_002' else 'NEW_LABELS_COMPUTATIONAL_HOLDOUT_NOT_PROSPECTIVE'
    if name in ('ROUND_002','ROUND_002_V002','ROUND_002_V003'):
        design=ROOT/'research/replays/ROUND_002/selection_design.v001.json'
        selection['prior_selection_design_sha256']=sha256(design)
        selection['source_resolution']='Native HSI and N225 accessible; no fallback used.'
    prereg={'batch_id':name,'created_at':utc_now(),'status':'FROZEN_BEFORE_THIS_BATCH_OUTCOMES',
            'selection_sha256':None,'selection_inspects_outcomes':False,
            'rule':'R002-TREND-PRIOR-v001','rule_parameters_changed':False,'parameter_search_count':0,
            'primary_horizon':'12m','secondary_horizons':['1w','1m','3m','6m','24m'],
            'context_role':'Background only; official releases never change the frozen trend rule.',
            'cash_assumption':'0% local currency, NOT observed cash; separate USD cash study later',
            'cost_bps_roundtrip':50,'p_up':{'positive':0.6,'mixed':0.5,'negative':0.4},
            'protocol_sha256':sha256(ROOT/'EPISODE_SELECTION_PROTOCOL.md'),
            'biases':['Current historical quote vintage; original corrections unknown','Rule designed today, not cognitively blind',
                      'Surviving fixed ETF/index universe','Annual overlapping 24m labels and shared calendar clusters',
                      'No historical valuation, analyst expectations, breadth or security-level fundamentals'],
            'new_batch_rejects':'No asset/date parameter branches, no outcome-directed replacement',
            'next_cycle_evaluation':'Frozen 0.5/0.6 probability baselines; always-up direction; fixed long buyhold; no tuning'}
    write_once(bundle_path,bundle)
    write_once(selection_path,selection)
    prereg['selection_sha256']=sha256(selection_path)
    write_once(prereg_path,prereg)
    write_once(folder/'administrative_sources.v001.lock.json',{
        'bundle_sha256':sha256(bundle_path),'selection_sha256':sha256(selection_path),
        'preregistration_sha256':sha256(prereg_path),'canonical_sources':sources,
        'official_records_sha256':sha256(official) if official.exists() else None})
    import_dataset(bundle_path,selection_path,folder/'ex_ante')
    print(json.dumps({'batch':name,'episodes':len(selection['episodes']),'date_clusters':len(years),
                      'status':'FILTERED_INPUTS_READY_NO_OUTCOMES_COMPUTED'}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--assets',required=True)
    p.add_argument('--years',required=True);p.add_argument('--month-day',default='09-30');a=p.parse_args()
    build(a.name,a.assets.split(','),[int(y) for y in a.years.split(',')],a.month_day)
