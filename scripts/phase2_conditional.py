#!/usr/bin/env python3
"""Finite conditional study; frozen adaptive exploration, never a new timing rule.

Official release publication times gate features. Shared benchmark helpers are
used only after registration to build future economic outcome labels. There is
no fitting, rule rescue, optimal-weight choice, or new independent replay.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lab.schema import HORIZONS, timestamp
from scripts.phase2_benchmarks import SOURCE, evaluate_cutoff, load_asset

OUT = ROOT / 'research/phase2'
PREREG = OUT / 'conditional.preregistration.v001.json'
LOCK = OUT / 'conditional.preregistration.v001.lock.json'
OFFICIAL = ROOT / 'data/raw/round_002/official/release_records.json'
YEARS = list(range(2016, 2024))
SEED = 20261009
DESIGN = {
    'study_id': 'PHASE2-CONDITIONAL-v001',
    'research_mode': 'ADAPTIVE_EXPLORATORY_NOT_INDEPENDENT_BLIND_CONFIRMATION',
    'prior_historical_knowledge_and_old_rule_outcomes_known': True,
    'purpose': 'finite falsification of two economic mechanisms, not a trading strategy',
    'sample': {'years': YEARS, 'cutoff': '09-30T23:59:59+00:00', 'date_clusters': 8, 'outcome_selection': False},
    'feature_publication_gate': 'VERIFIED original archive, published_at <= available_at <= T; source HTML SHA must match',
    'freshness_days': 45,
    'annual_policy_direction': 'current September FOMC lower bound minus previous calendar year September FOMC lower bound; never current-meeting rate change; 2016 UNKNOWN',
    'units': 'CPI yoy and Fed target bounds are percent numbers (5.25 means 5.25 percent), delta in percentage points',
    'conditions': {
        'Q-P2-C1': {'if': 'original headline CPI yoy >= 3.0 AND current September Fed target lower bound > prior annual September target lower bound', 'primary_prediction': '12m IEF net minus BIL net is negative and weaker than non-signal observations', 'mechanism': 'inflation-linked tightening creates duration repricing and policy-path risk relative to short bills', 'not_identified': 'term premium, starting yield, expected policy path, price-in, growth and future inflation are unobserved', 'strong_local_counterexample': 'signal followed by nonnegative 12m IEF-minus-BIL', 'endpoint': 'IEF-minus-BIL net return; IEF MDD/MAE and lower residual observations descriptive', 'unknown_policy_direction': 'signal null, not false'},
        'Q-P2-C2': {'if': 'original headline CPI yoy >= 3.0 AND current Fed target upper bound <= 0.5', 'primary_prediction': 'next calendar year September original FOMC target lower bound increases by >= 0.5 percentage points', 'mechanism': 'a high observed inflation / near-zero policy gap can put pressure on future policy normalization', 'secondary_description': 'same-start SPY/IEF returns and residuals; correct policy prediction is not price alpha', 'unknown_future_policy': '2023 next annual original release missing; label null; no new download or imputation'},
    },
    'horizons': HORIZONS, 'primary_horizon': '12m', 'secondary_horizons': ['1w', '1m', '3m', '6m', '24m'],
    'label_accounting': 'shared phase2_benchmarks.evaluate_cutoff: SPY/IEF/BIL common observed next-open; exit OPEN after N full sessions; qualified ex-date dividend reinvestment',
    'cost_per_leg_bps': 25.0,
    'benchmarks': ['ALWAYS_SPY', 'ALWAYS_BIL', 'ALWAYS_IEF', 'FIXED_50_50_SPY_BIL', 'FIXED_60_40_SPY_IEF', 'FIXED_70_30_SPY_IEF'],
    'residual': 'paired arithmetic net-return differences; not regression alpha or causal effect',
    'risk_metrics': 'daily close wealth plus terminal open MDD, MAE, MFE; lowest observations and q10 residual descriptive, not estimated population tails',
    'placebos': {
        'seed': SEED, 'repetitions': 200,
        'random_signals': 'permute whole-year condition masks including null across 8 date clusters; no independent ETF shuffle',
        'paired_label_shuffle': 'permute whole-year paired asset outcome vectors and future-policy labels across 8 date clusters',
        'random_dates': 'one uniform Monday-Friday date per calendar year; reapply true publication/freshness gate, keep unavailable conditions null; eight controls only',
        'random_holdings': 'each repetition draws each annual year holding from fixed 126/252/504 session set; no selection of best horizon',
        'inference': 'null distributions descriptive only; tiny signal N prohibits statistical p-value or significance claim',
    },
    'perturbations': {'date_shift_calendar_days': [-5, 0, 5], 'holding_sessions': [231, 252, 273], 'headline_cpi_threshold_pct': [2.5, 3.0, 3.5], 'design': 'one factor at a time with primary unchanged; every version saved, no choosing best', 'market_industry': 'NOT_IDENTIFIED: US policy/inflation not transplanted to HK/JP or company-sector fundamentals'},
    'decision': 'n<5 signal years or fewer than two independently evidenced macro regimes => INSUFFICIENT_INDEPENDENT_REGIMES regardless attractive mean; observed sign contradictions retained',
    'independent_regimes': 'unknown: 2021-2023 inflation/policy cycle cannot count as three independent regimes',
    'parameter_searches': 0, 'new_rule_predictions': 0, 'confidence_ceiling': 'D for this study',
    'limitations': ['original official releases retrieved today, not external trusted archives', 'current corrected/backfilled quote vintages', 'provider-reported dividends only; ex-date reinvestment is an economic convention', 'BIL split administrative reconstruction', 'surviving USD ETF sample', 'normal-session clock/half-day/halts not exhaustively verified', 'assumed trading costs; taxes/FX unavailable', 'eight date clusters, overlapping horizons, unknown independent N', 'adaptive hypothesis choice and historical model memory', 'no valuation, credit, expectations, term premium or fundamental records'],
}

def now():
    return datetime.now(timezone.utc).isoformat()

def read(path):
    return json.loads(Path(path).read_text())

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_once(path, body):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(body, f, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False); f.write('\n')
    return sha(path)

def source_hashes():
    paths = [OFFICIAL, *SOURCE.values(), Path(__file__), ROOT / 'scripts/phase2_benchmarks.py', ROOT / 'scripts/analyze_cash_and_sell.py', ROOT / 'lab/schema.py']
    return {str(p.relative_to(ROOT)): sha(p) for p in paths}

def validate_official(records, verify_files=True):
    ids = set()
    for r in records:
        if r['record_id'] in ids: raise ValueError('duplicate official source record')
        ids.add(r['record_id'])
        if r.get('pit_status') != 'VERIFIED': continue
        if not r.get('publication_date_evidence') or not r.get('publication_time_evidence') or not r.get('availability_evidence'):
            raise ValueError('VERIFIED release lacks actual date/time publication evidence')
        if timestamp(r['published_at']) > timestamp(r['available_at']): raise ValueError('availability before publication')
        if verify_files and sha(ROOT / r['source_path']) != r['source_sha256']:
            raise ValueError('official original HTML hash mismatch')

def fresh_release(records, kind, at, freshness_days=45):
    at = timestamp(at)
    known = [r for r in records if r.get('release_type') == kind and r.get('pit_status') == 'VERIFIED' and r.get('published_at') and r.get('available_at') and timestamp(r['published_at']) <= timestamp(r['available_at']) <= at]
    if not known: return None
    latest = max(known, key=lambda r: timestamp(r['published_at']))
    return latest if at - timestamp(latest['published_at']) <= timedelta(days=freshness_days) else None

def annual_prior(records, current, at):
    if current is None: return None
    year = timestamp(current['published_at']).year - 1
    known = [r for r in records if r.get('release_type') == 'FOMC_STATEMENT' and r.get('pit_status') == 'VERIFIED' and timestamp(r['published_at']).year == year and timestamp(r['published_at']).month == 9 and timestamp(r['published_at']) <= timestamp(r['available_at']) <= timestamp(at)]
    return max(known, key=lambda r: timestamp(r['published_at'])) if known else None

def feature_packet(records, at, cpi_threshold=3.0):
    fed = fresh_release(records, 'FOMC_STATEMENT', at)
    cpi = fresh_release(records, 'CPI_FIRST_RELEASE', at)
    prior = annual_prior(records, fed, at)
    value = lambda r, k: r.get('value', {}).get(k) if r else None
    low, high = value(fed, 'fed_funds_target_low_pct'), value(fed, 'fed_funds_target_high_pct')
    plow = value(prior, 'fed_funds_target_low_pct')
    yoy = value(cpi, 'cpi_headline_yoy_pct_first_release')
    delta = low - plow if low is not None and plow is not None else None
    c1 = yoy >= cpi_threshold and delta > 0 if yoy is not None and delta is not None else None
    c2 = yoy >= cpi_threshold and high <= .5 if yoy is not None and high is not None else None
    proof = lambda r: {k: r[k] for k in ('record_id', 'published_at', 'available_at', 'source_url', 'source_sha256', 'vintage_id')} if r else None
    return {'cutoff_at': at, 'cpi_yoy_pct': yoy, 'fed_lower_pct': low, 'fed_upper_pct': high, 'annual_september_lower_delta_pp': delta, 'annual_direction_status': 'UNKNOWN' if delta is None else ('RISING' if delta > 0 else 'FALLING' if delta < 0 else 'UNCHANGED'), 'condition_C1': c1, 'condition_C2': c2, 'cpi_threshold_pct': cpi_threshold, 'source_proofs': {'current_fomc': proof(fed), 'first_cpi': proof(cpi), 'prior_annual_september_fomc': proof(prior)}, 'freshness_policy': '45 days for current releases; exact prior-year annual FOMC comparator intentionally older', 'no_current_meeting_rate_change_claim': True}

def future_policy_label(records, at, current_low):
    # Explicit label-only API. Later records cannot enter feature_packet.
    year = timestamp(at).year + 1
    future = [r for r in records if r.get('release_type') == 'FOMC_STATEMENT' and r.get('pit_status') == 'VERIFIED' and timestamp(r['published_at']).year == year and timestamp(r['published_at']).month == 9 and timestamp(r['published_at']) > timestamp(at)]
    if not future or current_low is None:
        return {'status': 'DATA_REQUIRED_FUTURE_ANNUAL_ORIGINAL_POLICY', 'delta_pp': None, 'increase_ge_half_pp': None, 'source_id': None}
    r = min(future, key=lambda r: timestamp(r['published_at']))
    delta = r['value']['fed_funds_target_low_pct'] - current_low
    return {'status': 'KNOWN_ONLY_AFTER_T', 'delta_pp': delta, 'increase_ge_half_pp': delta >= .5, 'source_id': r['record_id'], 'published_at': r['published_at'], 'source_sha256': r['source_sha256']}

def preregister():
    if PREREG.exists() or LOCK.exists():
        verify(); return {'status': 'EXISTING_EXPLORATORY_LOCK_PASS', 'sha256': sha(PREREG)}
    records = read(OFFICIAL); validate_official(records)
    features = [feature_packet(records, f'{y}-09-30T23:59:59+00:00') for y in YEARS]
    body = {'registered_at': now(), 'design': DESIGN, 'source_and_code_sha256': source_hashes(), 'normalized_KNOWN_AT_T_fields': features, 'honesty': 'Official collection and old trend-rule outcomes already inspected; adaptive exploration only. No new price labels computed before this version lock.'}
    h = write_once(PREREG, body)
    write_once(LOCK, {'locked_at': now(), 'preregistration_sha256': h, 'source_and_code_sha256': body['source_and_code_sha256'], 'trusted_external_timestamp': False, 'hash_does_not_prove_historical_blindness': True})
    return {'status': 'ADAPTIVE_EXPLORATORY_DESIGN_LOCKED', 'sha256': h, 'date_clusters': len(features), 'C1_true': sum(f['condition_C1'] is True for f in features), 'C1_unknown': sum(f['condition_C1'] is None for f in features), 'C2_true': sum(f['condition_C2'] is True for f in features)}

def verify():
    body, lock = read(PREREG), read(LOCK)
    if body['design'] != DESIGN or lock['preregistration_sha256'] != sha(PREREG) or source_hashes() != body['source_and_code_sha256'] or lock['source_and_code_sha256'] != body['source_and_code_sha256']:
        raise ValueError('immutable design/code/source changed; append a new version instead')
    records = read(OFFICIAL); validate_official(records)
    actual = [feature_packet(records, f'{y}-09-30T23:59:59+00:00') for y in YEARS]
    if actual != body['normalized_KNOWN_AT_T_fields']: raise ValueError('frozen normalized official field mismatch')

def percentile(values, p):
    if not values: return None
    ordered = sorted(values); x = (len(values) - 1) * p; i = int(x); j = min(i + 1, len(values) - 1)
    return ordered[i] * (j - x) + ordered[j] * (x - i) if i != j else ordered[i]

def describe(values):
    return {'n_date_clusters': len(values), 'mean': statistics.mean(values) if values else None, 'median': statistics.median(values) if values else None, 'min_observed': min(values) if values else None, 'max_observed': max(values) if values else None, 'q10_descriptive_not_population_tail': percentile(values, .1)}

def summarize(rows):
    output = {}
    for cond in ('C1', 'C2'):
        valid = [r for r in rows if r[f'condition_{cond}'] is not None and r.get('residual_IEF_minus_BIL') is not None]
        signal = [r for r in valid if r[f'condition_{cond}'] is True]
        controls = [r for r in valid if r[f'condition_{cond}'] is False]
        a = describe([r['residual_IEF_minus_BIL'] for r in signal]); b = describe([r['residual_IEF_minus_BIL'] for r in controls])
        labeled = [r for r in signal if r['policy_label'].get('increase_ge_half_pp') is not None]
        output[cond] = {'status': 'INSUFFICIENT_INDEPENDENT_REGIMES', 'hypothesis_id': f'Q-P2-{cond}', 'signal_years': [r['year'] for r in signal], 'control_years': [r['year'] for r in controls], 'unknown_condition_years': [r['year'] for r in rows if r[f'condition_{cond}'] is None], 'signal_residual': a, 'non_signal_residual': b, 'mean_residual_signal_minus_non_signal': a['mean'] - b['mean'] if a['mean'] is not None and b['mean'] is not None else None, 'signal_nonnegative_residual_counterexample_years': [r['year'] for r in signal if r['residual_IEF_minus_BIL'] >= 0], 'negative_residual_non_signal_years': [r['year'] for r in controls if r['residual_IEF_minus_BIL'] < 0], 'signal_IEF_MDD': describe([r['IEF']['net_max_drawdown'] for r in signal]), 'non_signal_IEF_MDD': describe([r['IEF']['net_max_drawdown'] for r in controls]), 'signal_IEF_MAE': describe([r['IEF']['close_wealth_MAE'] for r in signal]), 'signal_SPY_minus_BIL': describe([r['residual_SPY_minus_BIL'] for r in signal]), 'policy_prediction_labeled_n': len(labeled), 'policy_increase_ge_half_pp_count': sum(r['policy_label']['increase_ge_half_pp'] for r in labeled), 'policy_false_positive_years': [r['year'] for r in labeled if not r['policy_label']['increase_ge_half_pp']], 'policy_false_negative_years': [r['year'] for r in controls if r['policy_label'].get('increase_ge_half_pp') is True], 'actual_independent_regime_n': None, 'statistical_p_value': None, 'new_return_or_risk_edge_established': False, 'confidence': 'D'}
    return output

def year_block_shuffle(rows, rng, kind):
    shuffled = [dict(r) for r in rows]
    indices = list(range(len(rows))); rng.shuffle(indices)
    for i, j in enumerate(indices):
        if kind == 'signals':
            for key in ('condition_C1', 'condition_C2'): shuffled[i][key] = rows[j][key]
        elif kind == 'paired_labels':
            for key in ('SPY', 'IEF', 'BIL', 'portfolios', 'residual_IEF_minus_BIL', 'residual_SPY_minus_BIL', 'policy_label'): shuffled[i][key] = rows[j][key]
        else: raise ValueError('unknown placebo kind')
    return shuffled, indices

def uniform_weekday(year, rng):
    first = date(year, 1, 1)
    dates = [first + timedelta(days=i) for i in range((date(year + 1, 1, 1) - first).days) if (first + timedelta(days=i)).weekday() < 5]
    return rng.choice(dates).isoformat() + 'T23:59:59+00:00'

def execute():
    verify()
    records = read(OFFICIAL)
    assets = {a: load_asset(p, a) for a, p in SOURCE.items()}
    cache = {}
    def episode(year, at, n, threshold=3.0):
        f = feature_packet(records, at, threshold)
        key = (at, n)
        if key not in cache: cache[key] = evaluate_cutoff(assets, at, n, leg_bps=25.0)
        label = cache[key]
        out = {**f, 'year': year, 'horizon_sessions': n, 'label_status': label['status'], 'policy_label': future_policy_label(records, at, f['fed_lower_pct']), 'SPY': None, 'IEF': None, 'BIL': None, 'portfolios': None, 'residual_IEF_minus_BIL': None, 'residual_SPY_minus_BIL': None}
        if label.get('components'):
            slim = lambda x: {k: v for k, v in x.items() if k != 'daily_close_wealth_path'}
            out.update({a: slim(label['components'][a]) for a in ('SPY', 'IEF', 'BIL')})
            out['portfolios'] = {p: slim(v) for p, v in label['portfolios'].items()}
            out['residual_IEF_minus_BIL'] = out['IEF']['net_return'] - out['BIL']['net_return']
            out['residual_SPY_minus_BIL'] = out['SPY']['net_return'] - out['BIL']['net_return']
            out['entry_date'], out['exit_date'] = label['entry_date'], label['exit_date']
        return out
    episodes = []
    for h, n in HORIZONS.items():
        for y in YEARS: episodes.append({**episode(y, f'{y}-09-30T23:59:59+00:00', n), 'horizon': h})
    primary = [r for r in episodes if r['horizon'] == '12m']
    perturb = []
    for shift in DESIGN['perturbations']['date_shift_calendar_days']:
        rows = [episode(y, (timestamp(f'{y}-09-30T23:59:59+00:00') + timedelta(days=shift)).isoformat(), 252) for y in YEARS]
        perturb.append({'version': f'date_shift_{shift:+d}', 'changed_factor': 'cutoff_calendar_days', 'value': shift, 'rows': rows, 'summary': summarize(rows)})
    for n in DESIGN['perturbations']['holding_sessions']:
        rows = [episode(y, f'{y}-09-30T23:59:59+00:00', n) for y in YEARS]
        perturb.append({'version': f'holding_{n}', 'changed_factor': 'holding_sessions', 'value': n, 'rows': rows, 'summary': summarize(rows)})
    for t in DESIGN['perturbations']['headline_cpi_threshold_pct']:
        rows = [episode(y, f'{y}-09-30T23:59:59+00:00', 252, t) for y in YEARS]
        perturb.append({'version': f'cpi_anchor_{t}', 'changed_factor': 'cpi_threshold_pct', 'value': t, 'rows': rows, 'summary': summarize(rows)})
    rng = random.Random(SEED)
    placebos = []
    for kind in ('signals', 'paired_labels'):
        for rep in range(200):
            rows, mapping = year_block_shuffle(primary, rng, kind)
            placebos.append({'placebo_class': 'random_signals' if kind == 'signals' else 'paired_label_shuffle', 'repetition': rep, 'source_year_by_target_year': {str(YEARS[i]): YEARS[j] for i, j in enumerate(mapping)}, 'summary': summarize(rows)})
    control_dates = [episode(y, uniform_weekday(y, rng), 252) for y in YEARS]
    placebos.append({'placebo_class': 'random_dates', 'repetition': 0, 'rows': control_dates, 'summary': summarize(control_dates), 'control_count': 8, 'unavailable_macro_features_retained_null': True})
    for rep in range(200):
        holding = {y: rng.choice((126, 252, 504)) for y in YEARS}
        rows = [episode(y, f'{y}-09-30T23:59:59+00:00', holding[y]) for y in YEARS]
        placebos.append({'placebo_class': 'random_holdings', 'repetition': rep, 'holding_sessions_by_year': holding, 'summary': summarize(rows)})
    distributions = []
    for cls in ('random_signals', 'paired_label_shuffle', 'random_dates', 'random_holdings'):
        selected = [p for p in placebos if p['placebo_class'] == cls]
        for cond in ('C1', 'C2'):
            for metric in ('mean_residual_signal_minus_non_signal',):
                values = [p['summary'][cond][metric] for p in selected if p['summary'][cond][metric] is not None]
                stats = describe(values); stats.pop('n_date_clusters')
                distributions.append({'class': cls, 'condition': cond, 'metric': metric, **stats, 'n_repetitions_with_statistic': len(values), 'independent_investment_observation_count': 0, 'q05': percentile(values, .05), 'q95': percentile(values, .95), 'main_observed_statistic': summarize(primary)[cond][metric], 'statistical_p_value': None, 'interpretation': 'DESCRIPTIVE_NULL_DISTRIBUTION_NOT_INDEPENDENT_INVESTMENT_EVIDENCE'})
    summary = {'study_id': DESIGN['study_id'], 'status': 'NO_CONDITIONAL_EDGE_ESTABLISHED_INSUFFICIENT_INDEPENDENT_REGIMES', 'research_mode': DESIGN['research_mode'], 'n_date_clusters': 8, 'n_horizon_rows': len(episodes), 'independent_N': None, 'primary_horizon': '12m', 'primary': summarize(primary), 'by_horizon': {h: summarize([r for r in episodes if r['horizon'] == h]) for h in HORIZONS}, 'placebo_distributions': distributions, 'perturbations': [{'version': p['version'], 'changed_factor': p['changed_factor'], 'value': p['value'], 'summary': p['summary']} for p in perturb], 'cross_market_industry_status': 'NOT_IDENTIFIED_US_MACRO_NOT_PORTABLE', 'return_edge': 'NOT_ESTABLISHED', 'downside_protection_edge': 'NOT_ESTABLISHED', 'return_risk_edge': 'NOT_ESTABLISHED', 'new_independent_replays': 0, 'new_locked_model_predictions': 0, 'parameter_searches': 0, 'trusted_prospective_evidence': False, 'limitations': DESIGN['limitations']}
    hashes = {}
    hashes['conditional.results.v001.json'] = write_once(OUT / 'conditional.results.v001.json', {'created_at': now(), 'preregistration_sha256': sha(PREREG), 'episodes': episodes, 'summary': summary})
    hashes['conditional.perturbations.v001.json'] = write_once(OUT / 'conditional.perturbations.v001.json', {'versions': perturb, 'all_versions_retained': True})
    hashes['conditional.placebos.v001.json'] = write_once(OUT / 'conditional.placebos.v001.json', {'seed': SEED, 'real_investment_evidence': False, 'p_values_not_reported': True, 'placebos': placebos})
    flat = []
    for r in episodes:
        flat.append({k: r[k] for k in ('year', 'cutoff_at', 'horizon', 'horizon_sessions', 'cpi_yoy_pct', 'fed_lower_pct', 'fed_upper_pct', 'annual_september_lower_delta_pp', 'annual_direction_status', 'condition_C1', 'condition_C2', 'entry_date', 'exit_date', 'residual_IEF_minus_BIL', 'residual_SPY_minus_BIL')} | {'SPY_net': r['SPY']['net_return'], 'IEF_net': r['IEF']['net_return'], 'BIL_net': r['BIL']['net_return'], 'IEF_MDD': r['IEF']['net_max_drawdown'], 'IEF_MAE': r['IEF']['close_wealth_MAE'], 'future_annual_policy_delta_pp': r['policy_label']['delta_pp'], 'future_annual_policy_label_status': r['policy_label']['status']})
    csvpath = OUT / 'conditional.outcomes.v001.csv'
    with csvpath.open('x', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(flat[0])); writer.writeheader(); writer.writerows(flat)
    hashes[csvpath.name] = sha(csvpath)
    reportpath = OUT / 'conditional.evidence.v001.md'
    with reportpath.open('x') as f: f.write(render_report(summary, primary))
    hashes[reportpath.name] = sha(reportpath)
    write_once(OUT / 'conditional.artifact_manifest.v001.json', {'created_at': now(), 'preregistration_sha256': sha(PREREG), 'artifact_sha256': hashes, 'source_and_code_sha256': source_hashes(), 'self_test': self_test(), 'benchmark_label_computations_cached': len(cache)})
    return {'status': summary['status'], 'date_clusters': 8, 'horizon_rows': len(episodes), 'placebo_runs': len(placebos), 'primary': summary['primary'], 'artifact_count': len(hashes) + 1}

def pct(x):
    return 'null' if x is None else f'{100*x:.2f}%'

def render_report(summary, primary):
    c1, c2 = summary['primary']['C1'], summary['primary']['C2']
    lines = ['# 两个有限宏观条件实验', '', '状态：**NO CONDITIONAL EDGE ESTABLISHED / INSUFFICIENT_INDEPENDENT_REGIMES**。这是读过旧结果后的有限探索，不是新的盲预测或独立样本验证。原简单趋势规则、旧Stage A和阈值均未改。', '', '固定2016–2023年9月30日，共8日期簇。CPI使用当时原发布同比；利率使用原FOMC目标上下限。当前发布45日新鲜度；政策方向只比较上一年度9月目标，不把它写成当前一次会议加息。2016年政策方向unknown，2023年的下一年度原FOMC标签missing，均保留null。', '', '|Year|CPI yoy %|Fed lower %|annual lower Δ pp|C1|C2|12m IEF−BIL|12m SPY−BIL|next annual lower Δ pp|', '|---|---:|---:|---:|---|---|---:|---:|---:|']
    for r in primary:
        lines.append(f"|{r['year']}|{r['cpi_yoy_pct']}|{r['fed_lower_pct']}|{r['annual_september_lower_delta_pp']}|{r['condition_C1']}|{r['condition_C2']}|{pct(r['residual_IEF_minus_BIL'])}|{pct(r['residual_SPY_minus_BIL'])}|{r['policy_label']['delta_pp']}|")
    lines += ['', f"C1只有{c1['signal_residual']['n_date_clusters']}个触发年份（{c1['signal_years']}），非触发{c1['non_signal_residual']['n_date_clusters']}，unknown年份{c1['unknown_condition_years']}。触发IEF−BIL均值{pct(c1['signal_residual']['mean'])}，非触发均值{pct(c1['non_signal_residual']['mean'])}；组间差{pct(c1['mean_residual_signal_minus_non_signal'])}。原方向的局部反例：{c1['signal_nonnegative_residual_counterexample_years']}。非触发却IEF弱于短债：{c1['negative_residual_non_signal_years']}。正负结果不能靠重复列SPY、IEF、BIL变成更多独立N。", '', f"C2只有{c2['signal_residual']['n_date_clusters']}个触发年份（{c2['signal_years']}），未来原政策可评分{c2['policy_prediction_labeled_n']}，目标下限至少上升0.5个百分点{c2['policy_increase_ge_half_pp_count']}次。即使政策方向正确，也不能推出价格尚未反映；同期SPY−BIL均值{pct(c2['signal_SPY_minus_BIL']['mean'])}，IEF−BIL均值{pct(c2['signal_residual']['mean'])}只是揭晓后的市场结果。非触发但同样出现政策上升：{c2['policy_false_negative_years']}。", '', '全部四类placebo保留：200次年份簇信号洗牌、200次完整配对标签洗牌、每年1个共8个随机工作日起点、200次固定126/252/504持有期抽签。随机日期重新通过真实发布时间与45日新鲜度；资料缺失不把9月信息偷偷搬到更早日期。结果是描述性null分布，不能变成独立投资证据；触发N太小，不给p值。', '', '|Placebo|Condition|available repetitions|mean signal−control residual|q05|q95|', '|---|---|---:|---:|---:|---:|']
    for d in summary['placebo_distributions']:
        lines.append(f"|{d['class']}|{d['condition']}|{d['n_repetitions_with_statistic']}|{pct(d['mean'])}|{pct(d['q05'])}|{pct(d['q95'])}|")
    lines += ['', '轻微扰动逐项保存，不能选最好版本或改变主条件。', '', '|Version|C1 signal N|C1 signal−control|C1 nonnegative residual counterexamples|C2 signal N|', '|---|---:|---:|---|---:|']
    for p in summary['perturbations']:
        a,b=p['summary']['C1'],p['summary']['C2']
        lines.append(f"|{p['version']}|{a['signal_residual']['n_date_clusters']}|{pct(a['mean_residual_signal_minus_non_signal'])}|{a['signal_nonnegative_residual_counterexample_years']}|{b['signal_residual']['n_date_clusters']}|")
    lines += ['', '资产benchmark全部使用同一SPY/IEF/BIL共同交易日下一开盘入场、同样252完整交易日后开盘退出、每腿25bp成本，固定50/50股票短债、60/40和70/30股票国债初始权重漂移持有。分红为供应商除息日经济再投资，未知付款日，不宣称当日现金可执行。IEF−BIL是配对差，不是严格alpha。MDD/MAE基于日收盘财富与末次开盘，不能写成日内最差跌幅。', '', '没有建立RETURN EDGE、DOWNSIDE PROTECTION EDGE或RETURN/RISK EDGE。2021–2023可能仅同一通胀政策周期，独立regime数量未知。US通胀/利率条件不能移植成香港、日本或公司行业基本面，跨市场/行业为NOT_IDENTIFIED。当前报价版本、供方股息和幸存ETF偏差仍在；估值、信用、起始收益率、期限溢价与当时市场预期缺失，不能确定失效原因。', '', '下一项最便宜反证：按原规则扩充有发布证据的独立高通胀加息/零利率政策缺口时期，连同同起点市场隐含政策路径和久期收益率；先回答是否政策变化可预测，再回答变化是否未被价格反映。不能因本次薄样本晋升原则。', '']
    return '\n'.join(lines)

def self_test():
    def r(kind, at, low=0, high=.25, yoy=5):
        return {'record_id': kind + at, 'release_type': kind, 'pit_status': 'VERIFIED', 'published_at': at, 'available_at': at, 'publication_date_evidence': at[:10], 'publication_time_evidence': 'actual original publication time', 'availability_evidence': 'original release', 'source_url': 'https://example.invalid', 'source_sha256': '0'*64, 'vintage_id': 'ORIGINAL', 'value': {'fed_funds_target_low_pct': low, 'fed_funds_target_high_pct': high, 'cpi_headline_yoy_pct_first_release': yoy}}
    cutoff = '2021-09-30T23:59:59+00:00'
    fed = r('FOMC_STATEMENT', '2021-09-22T18:00:00+00:00')
    cpi = r('CPI_FIRST_RELEASE', '2021-09-14T12:30:00+00:00')
    prior = r('FOMC_STATEMENT', '2020-09-16T18:00:00+00:00')
    future = r('FOMC_STATEMENT', '2022-09-21T18:00:00+00:00', 3, 3.25)
    data = [fed,cpi,prior,future]
    p = feature_packet(data,cutoff)
    assert p['fed_lower_pct'] == 0 and p['annual_september_lower_delta_pp'] == 0 and p['condition_C2'] is True
    assert feature_packet([fed,cpi], cutoff)['condition_C1'] is None
    assert feature_packet(data, '2021-09-21T23:59:59+00:00')['fed_lower_pct'] is None
    assert feature_packet(data, '2021-11-30T23:59:59+00:00')['condition_C2'] is None
    altered = dict(cpi, published_at='2021-10-01T12:30:00+00:00', available_at='2021-10-01T12:30:00+00:00')
    assert feature_packet([fed,prior,altered], cutoff)['cpi_yoy_pct'] is None
    delayed = dict(cpi, available_at='2021-10-01T12:30:00+00:00')
    assert feature_packet([fed,prior,delayed], cutoff)['cpi_yoy_pct'] is None
    assert feature_packet([fed,prior,dict(cpi,pit_status='POINT_IN_TIME_UNCERTAIN')],cutoff)['cpi_yoy_pct'] is None
    missing = dict(cpi); missing.pop('published_at')
    assert feature_packet([fed,missing,prior],cutoff)['cpi_yoy_pct'] is None
    validate_official(data,False)
    rejected=False
    try: validate_official([dict(cpi,available_at='2021-09-13T12:30:00+00:00')],False)
    except ValueError: rejected=True
    assert rejected
    futurelabel=future_policy_label(data,cutoff,0)
    assert futurelabel['delta_pp'] == 3 and futurelabel['increase_ge_half_pp'] is True and feature_packet(data,cutoff)==p
    assert future_policy_label(data,'2023-09-30T23:59:59+00:00',5.25)['delta_pp'] is None
    rows = [{'year':y,'condition_C1':i<2,'condition_C2':i==3,'residual_IEF_minus_BIL':i,'residual_SPY_minus_BIL':-i,'SPY':{'year':y},'IEF':{'year':y},'BIL':{'year':y},'portfolios':{'year':y},'policy_label':{'year':y}} for i,y in enumerate(YEARS)]
    shuffled,indices=year_block_shuffle(rows,random.Random(SEED),'signals')
    assert sum(r['condition_C1'] for r in shuffled)==2 and sorted(indices)==list(range(8)) and all(shuffled[i]['SPY']==rows[i]['SPY'] for i in range(8))
    shuffled,indices=year_block_shuffle(rows,random.Random(SEED),'paired_labels')
    assert all(shuffled[i]['SPY']['year']==shuffled[i]['IEF']['year']==shuffled[i]['BIL']['year'] and shuffled[i]['residual_IEF_minus_BIL']==-shuffled[i]['residual_SPY_minus_BIL'] for i in range(8))
    d=timestamp(uniform_weekday(2021,random.Random(SEED)))
    assert d.year==2021 and d.weekday()<5
    assert percentile([1,2],.1)==1.1 and describe([])['mean'] is None
    return {'status':'SYNTHETIC_ENGINEERING_ONLY_PASS','checks':15,'real_market_files_opened':False,'investment_evidence':False}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['self-test','preregister','execute','verify']); args=parser.parse_args()
    if args.action=='self-test': result=self_test()
    elif args.action=='preregister': result=preregister()
    elif args.action=='verify': verify(); result={'status':'IMMUTABLE_LOCK_INTEGRITY_PASS'}
    else: result=execute()
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))

if __name__=='__main__': main()
