#!/usr/bin/env python3
"""Locked Phase 3 descriptive distributions, dependence assessment and controls.

No model fitting, parameter search, old 63/252 rule or probability predictions.
Register this code before reading new outcome labels. Development is immutable;
the later-label partition cannot be read until its development lock is verified.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/phase3'
OUT = BASE / 'analysis'
FEATURES = BASE / 'features/decision_points.v001.json'
DESIGN = BASE / 'design.v001.json'
REGISTRATION = OUT / 'code_registration.v001.json'
DEVLOCK = OUT / 'development.lock.v001.json'
HORIZONS = ['1w', '1m', '3m', '6m', '12m', '24m']
VARIABLES = {
    'H-P3-TREND': ('features', 'trend_group', 'POSITIVE', 'NONPOSITIVE'),
    'H-P3-DRAWDOWN': ('features', 'drawdown_group', 'LARGE_DRAWDOWN', 'OTHER'),
    'H-P3-VOL': ('features', 'vol_group', 'HIGH', 'NOT_HIGH'),
    'H-P3-CREDIT': ('credit', 'group', 'TIGHTENING', 'NOT_TIGHTENING'),
}
BENCHMARKS = ['OWN_PASSIVE', 'PAIRED_ASSET_BENCHMARK',
              'FIXED_50_50_SPY_BIL', 'FIXED_60_40_SPY_IEF', 'FIXED_70_30_SPY_IEF']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    return str(Path(path).relative_to(ROOT))


def read(path):
    return json.loads(Path(path).read_text())


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and np.isfinite(x)


def clean(obj):
    if isinstance(obj, dict):
        return {str(k): clean(v) for k, v in obj.items()}
    if isinstance(obj, (tuple, list, np.ndarray)):
        return [clean(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj) if np.isfinite(obj) else None
    return obj


def write_once(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(clean(obj), ensure_ascii=False, sort_keys=True, indent=2,
                      allow_nan=False) + '\n').encode()
    if path.exists() and path.read_bytes() != raw:
        raise RuntimeError('Refusing overwrite: ' + str(path))
    if not path.exists():
        path.write_bytes(raw)


def write_csv_once(path, rows):
    import io
    target = io.StringIO()
    keys = list(rows[0]) if rows else ['status']
    writer = csv.DictWriter(target, fieldnames=keys)
    writer.writeheader()
    writer.writerows(rows)
    raw = target.getvalue().encode()
    if path.exists() and path.read_bytes() != raw:
        raise RuntimeError('Refusing overwrite: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(raw)


def register():
    write_once(REGISTRATION, {
        'registered_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'code_path': rel(Path(__file__)), 'code_sha256': digest(__file__),
        'design_sha256': digest(DESIGN),
        'labels_read_before_registration': False,
        'estimands': 'Raw distributions and date-equal group differences; not strategy returns or alpha.',
        'variables': list(VARIABLES), 'horizons': HORIZONS,
        'vol_endpoint_interpretation': {'registered_question': 'H-P3-VOL-ENDPOINT-v001',
            'formula': '252 previous rolling252-return vol observations, excludes current; requires505 price bars.',
            '504_bar_point': 'Other features kept; relative-vol comparison UNKNOWN.'},
        'bootstrap': {'repetitions': 500, 'seed': 20261009,
                      'unit': 'fixed joint two-calendar-year blocks, every asset sampled together'},
        'cohorts': ['ALL', 'asset', 'market', 'industry', 'era', 'validation_scope', 'fixed_Q4',
                    'prior_exposure', 'asset_x_era', 'market_x_era', 'industry_x_era'],
        'holdout_rule': 'No holdout read before development.lock.v001.json and its file SHAs verified.',
        'optimization': False, 'operative_framework_change': False,
    })
    print(json.dumps({'registered': rel(REGISTRATION), 'sha256': digest(__file__)}))


def verify_registration():
    reg = read(REGISTRATION)
    if reg['code_sha256'] != digest(__file__) or reg['design_sha256'] != digest(DESIGN):
        raise RuntimeError('Registered code/design changed; new preregistration required.')


def verify_devlock():
    lock = read(DEVLOCK)
    if lock['status'] != 'DEVELOPMENT_ANALYSIS_LOCKED_BEFORE_HOLDOUT':
        raise RuntimeError('Development not locked.')
    if lock['feature_sha256'] != digest(FEATURES):
        raise RuntimeError('Features changed after development.')
    for path, expected in lock['files'].items():
        if digest(ROOT / path) != expected:
            raise RuntimeError('Development artifact changed: ' + path)
    return lock


def verify_panel_inputs(partition):
    lock = read(BASE / 'features/decision_points.v001.SHA.lock.json')
    if lock['feature_sha256'] != digest(FEATURES) or lock['feature_count'] != 2704:
        raise RuntimeError('Full frozen feature panel does not match lock.')
    label_path = BASE / f'labels/{partition}.v001.json'
    label_lock = read(BASE / f'labels/{partition}.v001.SHA.lock.json')
    if (label_lock['label_sha256'] != digest(label_path) or
            label_lock['feature_sha256'] != digest(FEATURES) or
            label_lock['partition'] != partition):
        raise RuntimeError('Frozen labels do not match feature/partition lock.')


def era(year):
    return '2000-2009' if year < 2010 else '2010-2019' if year < 2020 else '2020-2025'


def validation_scope(year):
    if year <= 2015:
        return 'PREREGISTERED_CROSS_TIME_RECONSTRUCTION'
    if year <= 2023:
        return 'DEVELOPMENT_CONTEXT_ALREADY_EXPOSED'
    return 'COMPUTATIONAL_LATER_LABEL_HOLDOUT_WITH_PRIOR_PATH_EXPOSURE'


def rows_from_labels(points, labels, partition):
    features = {p['point_id']: p for p in points}
    if len(features) != len(points):
        raise RuntimeError('Duplicate feature point_id.')
    rows = []
    for label in labels['points']:
        p = features[label['point_id']]
        expected = p['year'] <= 2023 if partition == 'development' else p['year'] >= 2024
        if not expected:
            raise RuntimeError('Partition contamination: ' + p['point_id'])
        for horizon in HORIZONS:
            y = label['horizons'][horizon]
            row = {
                'point_id': p['point_id'], 'asset_id': p['asset_id'],
                'market': p['market'], 'industry': p['industry'],
                'instrument_type': p['instrument_type'], 'currency': p['currency'],
                'year': p['year'], 'quarter': p['quarter'],
                'calendar_quarter': p['calendar_quarter'],
                'era': era(p['year']), 'validation_scope': validation_scope(p['year']),
                'prior_exposure': p.get('prior_exposure', 'UNKNOWN'),
                'horizon': horizon, 'feature_eligible': bool(p['feature_eligible']),
                'feature_status': p['status'], 'label_status': y['status'],
                'entry_date': y.get('entry_date'), 'exit_date': y.get('exit_date'),
                'net_return': y.get('net_return'), 'max_drawdown': y.get('max_drawdown'),
                'return_basis': y.get('return_basis', p.get('return_basis')),
                'max_adverse_excursion': y.get('max_adverse_excursion'),
                'max_favorable_excursion': y.get('max_favorable_excursion'),
                'groups': {}, 'benchmark_differences': {},
            }
            for variable, (section, key, yes, no) in VARIABLES.items():
                value = p.get(section, {}).get(key)
                if variable == 'H-P3-CREDIT':
                    credit = p.get('credit', {})
                    if p['market'] != 'US' or credit.get('status') != 'KNOWN_AT_T':
                        value = None
                    if value is not None and (not finite(credit.get('value')) or
                                               not finite(credit.get('age_days')) or
                                               credit['age_days'] > 180):
                        raise RuntimeError('Unqualified credit group: ' + p['point_id'])
                row['groups'][variable] = 1 if value == yes else 0 if value == no else None
            if finite(row['net_return']):
                row['benchmark_differences']['OWN_PASSIVE'] = 0.0
            bench = y.get('benchmark', {})
            if bench.get('status') == 'SAME_EXECUTION' and finite(bench.get('difference_net_return')):
                row['benchmark_differences']['PAIRED_ASSET_BENCHMARK'] = bench['difference_net_return']
            for key, value in y.get('fixed_allocation_benchmarks', {}).items():
                if value.get('status') == 'SAME_EXECUTION' and finite(value.get('difference_net_return')):
                    row['benchmark_differences'][key] = value['difference_net_return']
            rows.append(row)
    if len({(r['point_id'], r['horizon']) for r in rows}) != len(rows):
        raise RuntimeError('Duplicate label row.')
    return rows


def summary(values, mdds=None):
    a = np.array([x for x in values if finite(x)], dtype=float)
    if not len(a):
        return {'n_raw': 0, 'mean': None, 'median': None, 'win_rate': None,
                'p25': None, 'p75': None, 'worst_decile_p10': None,
                'best_decile_p90': None, 'mean_max_drawdown': None,
                'worst_max_drawdown': None}
    draw = np.array([x for x in (mdds or []) if finite(x)], dtype=float)
    return {'n_raw': len(a), 'mean': a.mean(), 'median': np.median(a),
            'win_rate': np.mean(a > 0), 'p25': np.quantile(a, .25),
            'p75': np.quantile(a, .75), 'worst_decile_p10': np.quantile(a, .1),
            'best_decile_p90': np.quantile(a, .9),
            'mean_max_drawdown': draw.mean() if len(draw) else None,
            'worst_max_drawdown': draw.min() if len(draw) else None}


def cohort_definitions(design):
    assets = [a['asset_id'] for a in design['assets']]
    markets = sorted({a['market'] for a in design['assets']})
    industries = sorted({a['industry'] for a in design['assets']})
    eras = ['2000-2009', '2010-2019', '2020-2025']
    specs = [('ALL', 'ALL', {})]
    specs.append(('fixed_Q4', 'Q4', {'quarter': 4}))
    for key, values in [('asset_id', assets), ('market', markets), ('industry', industries),
                        ('era', eras), ('validation_scope', [
                            'PREREGISTERED_CROSS_TIME_RECONSTRUCTION',
                            'DEVELOPMENT_CONTEXT_ALREADY_EXPOSED',
                            'COMPUTATIONAL_LATER_LABEL_HOLDOUT_WITH_PRIOR_PATH_EXPOSURE']),
                        ('prior_exposure', ['ALREADY_USED_ASSET_CALENDAR_QUARTER',
                                           'NOT_ALREADY_USED_ASSET_CALENDAR_QUARTER'])]:
        for value in values:
            specs.append((key, value, {key: value}))
    for key, values in [('asset_id', assets), ('market', markets), ('industry', industries)]:
        for value in values:
            for e in eras:
                specs.append((key + '_x_era', value + '|' + e, {key: value, 'era': e}))
    return specs


def independence(rows):
    return {'n_raw': len(rows), 'n_effective': None,
            'calendar_quarter_clusters': len({r['calendar_quarter'] for r in rows}),
            'year_clusters': len({r['year'] for r in rows}),
            'two_year_calendar_blocks': len({(r['year'] - 2000) // 2 for r in rows}),
            'same_date_asset_correlation': 'NOT_INDEPENDENT',
            'overlapping_returns': 'Quarterly starting points overlap at 12m/24m.',
            'common_global_regime': 'Cross-country and cross-sector dependence remains.',
            'bootstrap_effective_n_claim': False}


def date_means(rows, value_key='net_return', benchmark=None):
    cells = {}
    for r in rows:
        x = r[value_key] if benchmark is None else r['benchmark_differences'].get(benchmark)
        if finite(x):
            cells.setdefault(r['calendar_quarter'], []).append(x)
    return {q: float(np.mean(x)) for q, x in cells.items()}


def block_ci(group1, group0, design, benchmark=None):
    """Joint block draws for both groups; date-equal, no cross-FX portfolio."""
    d1, d0 = date_means(group1, benchmark=benchmark), date_means(group0, benchmark=benchmark)
    blocks = sorted({(int(q[:4]) - 2000) // 2 for q in set(d1) | set(d0)})
    if not d1 or not d0 or not blocks:
        return {'status': 'NO_TWO_GROUP_COMPARISON', 'difference_date_equal': None,
                'ci95': None, 'group1_date_equal_mean': np.mean(list(d1.values())) if d1 else None,
                'group0_date_equal_mean': np.mean(list(d0.values())) if d0 else None,
                'group1_ci95': None, 'group0_ci95': None, 'n_blocks': len(blocks)}
    def aggregate(data):
        sums, counts = [], []
        for block in blocks:
            values = [x for q, x in data.items() if (int(q[:4]) - 2000) // 2 == block]
            sums.append(sum(values))
            counts.append(len(values))
        return np.array(sums), np.array(counts)
    s1, n1 = aggregate(d1)
    s0, n0 = aggregate(d0)
    draws = np.random.default_rng(design['bootstrap_seed']).integers(
        0, len(blocks), size=(design['bootstrap_reps'], len(blocks)))
    den1, den0 = n1[draws].sum(axis=1), n0[draws].sum(axis=1)
    with np.errstate(invalid='ignore', divide='ignore'):
        m1, m0 = s1[draws].sum(axis=1) / den1, s0[draws].sum(axis=1) / den0
    diff = m1 - m0
    def ci(values):
        values = values[np.isfinite(values)]
        return np.quantile(values, [.025, .975]).tolist() if len(values) else None
    b1 = len({(int(q[:4]) - 2000) // 2 for q in d1})
    b0 = len({(int(q[:4]) - 2000) // 2 for q in d0})
    return {'status': 'DESCRIPTIVE_BLOCK_INTERVAL' if min(b1, b0) >= 4 else 'UNRELIABLE_FEWER_THAN_4_BLOCKS',
            'difference_date_equal': float(np.mean(list(d1.values())) - np.mean(list(d0.values()))),
            'ci95': ci(diff), 'group1_date_equal_mean': np.mean(list(d1.values())),
            'group0_date_equal_mean': np.mean(list(d0.values())),
            'group1_ci95': ci(m1), 'group0_ci95': ci(m0), 'n_blocks': len(blocks),
            'group1_blocks': b1, 'group0_blocks': b0,
            'valid_bootstrap_repetitions': int(np.isfinite(diff).sum()),
            'pooled_local_return_is_portfolio': False}


def distributions(rows, design):
    results, controls, comparisons = [], [], []
    for kind, name, filt in cohort_definitions(design):
        selected = [r for r in rows if all(r[k] == v for k, v in filt.items())]
        for horizon in HORIZONS:
            window = [r for r in selected if r['horizon'] == horizon]
            for variable, (_, _, yes, no) in VARIABLES.items():
                eligible = [r for r in window if r['feature_eligible'] and
                            finite(r['net_return']) and r['groups'][variable] is not None]
                groups = [[r for r in eligible if r['groups'][variable] == g] for g in [1, 0]]
                item = {'cohort_type': kind, 'cohort': name, 'horizon': horizon,
                        'variable': variable, 'group1_label': yes, 'group0_label': no,
                        'status': 'COMPARISON_AVAILABLE' if all(groups) else 'ONE_OR_BOTH_GROUPS_MISSING',
                        'selected_point_count': len(window),
                        'excluded_feature_or_label_or_variable': len(window) - len(eligible),
                        'group1': summary([r['net_return'] for r in groups[0]],
                                          [r['max_drawdown'] for r in groups[0]]),
                        'group0': summary([r['net_return'] for r in groups[1]],
                                          [r['max_drawdown'] for r in groups[1]]),
                        'independence': independence(eligible),
                        'group_difference': block_ci(groups[0], groups[1], design),
                        'benchmarks': {}}
                for benchmark in BENCHMARKS:
                    matched = [[r for r in g if finite(r['benchmark_differences'].get(benchmark))]
                               for g in groups]
                    item['benchmarks'][benchmark] = {
                        'group1': summary([r['benchmark_differences'][benchmark] for r in matched[0]]),
                        'group0': summary([r['benchmark_differences'][benchmark] for r in matched[1]]),
                        'group_difference': block_ci(matched[0], matched[1], design, benchmark=benchmark)}
                results.append(item)
                comparisons.append({'cohort_type': kind, 'cohort': name, 'horizon': horizon,
                                    'variable': variable, 'comparison_available': bool(all(groups)),
                                    'group1_n': len(groups[0]), 'group0_n': len(groups[1]),
                                    'difference_date_equal': item['group_difference']['difference_date_equal'],
                                    'ci95_lower': (item['group_difference']['ci95'] or [None, None])[0],
                                    'ci95_upper': (item['group_difference']['ci95'] or [None, None])[1],
                                    'n_effective': None})
    # Complete row-level controls, not hand-selected supportive cases.
    for r in rows:
        if not r['feature_eligible'] or not finite(r['net_return']):
            continue
        for variable in VARIABLES:
            group = r['groups'][variable]
            if group is None:
                continue
            controls.append({k: r[k] for k in ['point_id', 'asset_id', 'market', 'industry',
                                              'year', 'quarter', 'horizon', 'net_return']} | {
                'variable': variable, 'group': group,
                'outcome_class': ('GROUP1_NONPOSITIVE' if group and r['net_return'] <= 0 else
                                  'GROUP0_POSITIVE' if not group and r['net_return'] > 0 else
                                  'GROUP1_POSITIVE' if group else 'GROUP0_NONPOSITIVE'),
                'interpretation': 'Outcome category only; variables do not all prespecify a bullish signal.'})
    return results, controls, comparisons


def nonoverlap(rows, design):
    answers = []
    for horizon in ['12m', '24m']:
        for asset in sorted({r['asset_id'] for r in rows}):
            candidates = sorted([r for r in rows if r['asset_id'] == asset and
                                 r['horizon'] == horizon and r['feature_eligible'] and
                                 finite(r['net_return']) and r['entry_date'] and r['exit_date']],
                                key=lambda r: (r['entry_date'], r['point_id']))
            picked, end = [], None
            for r in candidates:
                if end is None or r['entry_date'] >= end:
                    picked.append(r)
                    end = r['exit_date']
            variable_results = {}
            for variable in VARIABLES:
                groups = [[r for r in picked if r['groups'][variable] == g] for g in [1, 0]]
                variable_results[variable] = {
                    'group1': summary([r['net_return'] for r in groups[0]],
                                      [r['max_drawdown'] for r in groups[0]]),
                    'group0': summary([r['net_return'] for r in groups[1]],
                                      [r['max_drawdown'] for r in groups[1]]),
                    'group_difference': block_ci(groups[0], groups[1], design)}
            answers.append({'asset_id': asset, 'horizon': horizon,
                            'n_raw_eligible': len(candidates), 'n_actual_nonoverlap': len(picked),
                            'point_ids': [r['point_id'] for r in picked],
                            'selection': 'Greedy earliest actual entry; entry>=previous exit; no return selection.',
                            'n_effective': None,
                            'variable_results': variable_results,
                            'summary': summary([r['net_return'] for r in picked],
                                               [r['max_drawdown'] for r in picked])})
    return answers


def opposite_cohort_controls(results):
    answers = []
    for variable in VARIABLES:
        for horizon in HORIZONS:
            pooled = next(x for x in results if x['cohort_type'] == 'ALL' and
                          x['variable'] == variable and x['horizon'] == horizon)
            all_difference = pooled['group_difference']['difference_date_equal']
            for x in results:
                if x['variable'] != variable or x['horizon'] != horizon or x['cohort_type'] not in [
                        'market', 'industry', 'market_x_era', 'industry_x_era']:
                    continue
                difference = x['group_difference']['difference_date_equal']
                answers.append({'variable': variable, 'horizon': horizon,
                    'cohort_type': x['cohort_type'], 'cohort': x['cohort'],
                    'pooled_difference': all_difference, 'cohort_difference': difference,
                    'opposite_sign_to_pooled': bool(all_difference * difference < 0)
                        if finite(all_difference) and finite(difference) else None,
                    'interpretation': 'Marginal association differences; not proof of industry causal mechanism.'})
    return answers


def credit_gate(rows, design):
    gate, evidence = design['credit_interaction_gate'], []
    for start, end in gate['decades']:
        allrows = [r for r in rows if start <= r['year'] <= end and r['market'] == 'US' and
                   r['horizon'] == '12m' and r['feature_eligible'] and finite(r['net_return']) and
                   r['groups']['H-P3-CREDIT'] is not None]
        groups = [[r for r in allrows if r['groups']['H-P3-CREDIT'] == g] for g in [1, 0]]
        comparison = block_ci(groups[0], groups[1], design)
        evidence.append({'decade': f'{start}-{end}', 'date_clusters': len({r['calendar_quarter'] for r in allrows}),
                         'group1_dates': len({r['calendar_quarter'] for r in groups[0]}),
                         'group0_dates': len({r['calendar_quarter'] for r in groups[1]}),
                         'difference': comparison['difference_date_equal']})
    passed = all(e['date_clusters'] >= gate['minimum_dates_per_decade'] and
                 e['group1_dates'] > 0 and e['group0_dates'] > 0 and finite(e['difference'])
                 for e in evidence)
    if passed:
        passed = evidence[0]['difference'] * evidence[1]['difference'] > 0
    return {'hypothesis_id': gate['id'], 'status': 'GATE_PASSED_EXPLORATORY_ONLY' if passed else 'NOT_RUN_GATE_FAILED',
            'evidence': evidence, 'gate_threshold_changed': False}


def interaction_results(rows, gate):
    if gate['status'] != 'GATE_PASSED_EXPLORATORY_ONLY':
        return []
    answers = []
    for horizon in HORIZONS:
        for e in ['ALL', '2000-2009', '2010-2019', '2020-2025']:
            cohort = [r for r in rows if r['market'] == 'US' and r['horizon'] == horizon and
                      (e == 'ALL' or r['era'] == e) and r['feature_eligible'] and
                      finite(r['net_return']) and all(r['groups'][v] is not None for v in
                                                     ['H-P3-DRAWDOWN', 'H-P3-CREDIT'])]
            for draw in [1, 0]:
                for credit in [1, 0]:
                    group = [r for r in cohort if r['groups']['H-P3-DRAWDOWN'] == draw and
                             r['groups']['H-P3-CREDIT'] == credit]
                    answers.append({'horizon': horizon, 'era': e, 'drawdown_group': draw,
                                    'credit_group': credit, 'independence': independence(group),
                                    'distribution': summary([r['net_return'] for r in group],
                                                            [r['max_drawdown'] for r in group]),
                                    'level': 'LEVEL1_DESCRIPTIVE_NOT_INVESTMENT_PRINCIPLE'})
    return answers


def run(partition):
    verify_registration()
    if partition == 'holdout':
        verify_devlock()
    verify_panel_inputs(partition)
    design = read(DESIGN)
    feature_obj = read(FEATURES)
    label_path = BASE / f'labels/{partition}.v001.json'
    labels = read(label_path)
    rows = rows_from_labels(feature_obj['points'], labels, partition)
    results, controls, comparison_rows = distributions(rows, design)
    eligible12 = [r for r in rows if r['feature_eligible'] and r['horizon'] == '12m' and finite(r['net_return'])]
    gate = credit_gate(rows, design) if partition == 'development' else read(OUT / 'development.results.v001.json')['credit_interaction_gate']
    response = {'study_id': design['study_id'], 'partition': partition,
                'feature_sha256': digest(FEATURES), 'label_sha256': digest(label_path),
                'code_sha256': digest(__file__), 'n_selected_points': len(labels['points']),
                'n_raw_horizon_records': len(rows), 'n_feature_eligible_points': len({r['point_id'] for r in rows if r['feature_eligible']}),
                'n_mature_12m_feature_eligible': len(eligible12),
                'mature_labels_by_horizon': {h: sum(finite(r['net_return']) for r in rows if r['horizon'] == h) for h in HORIZONS},
                'feature_eligible_mature_by_horizon': {h: sum(r['feature_eligible'] and finite(r['net_return']) for r in rows if r['horizon'] == h) for h in HORIZONS},
                'label_status_counts': {s: sum(r['label_status'] == s for r in rows) for s in sorted({r['label_status'] for r in rows})},
                'independence_12m': independence(eligible12), 'n_effective': None,
                'all_results': results, 'actual_nonoverlap': nonoverlap(rows, design),
                'market_industry_opposite_controls': opposite_cohort_controls(results),
                'credit_interaction_gate': gate, 'credit_interaction': interaction_results(rows, gate),
                'multiple_testing': {'registered_single_variables': 4,
                    'price_variables': 3, 'credit_available': any(r['groups']['H-P3-CREDIT'] is not None for r in rows),
                    'cohort_specs': len(cohort_definitions(design)), 'horizons': len(HORIZONS),
                    'single_variable_comparison_slots': len(results),
                    'available_two_group_comparisons': sum(x['comparison_available'] for x in comparison_rows),
                    'benchmark_comparison_slots': len(results) * len(BENCHMARKS),
                    'actual_nonoverlap_variable_comparison_slots': len({r['asset_id'] for r in rows}) * 2 * len(VARIABLES),
                    'registered_interactions': 1, 'interaction_cells_run': len(interaction_results(rows, gate)),
                    'parameter_searches': 0, 'new_investment_principles': 0},
                'constraints': ['RECONSTRUCTED_NOT_ARCHIVED', 'SURVIVING_INSTRUMENT_UNIVERSE',
                    'NOT_FUTURE_OOS', 'NO_CAUSAL_IDENTIFICATION', 'NO_ALPHA_IDENTIFICATION',
                    'LOCAL_CURRENCY_POOLED_MEAN_NOT_PORTFOLIO', 'NO_NEW_STRATEGY', 'NO_PARAMETER_SEARCH']}
    result_path = OUT / f'{partition}.results.v001.json'
    controls_path = OUT / f'{partition}.negative_controls.v001.csv'
    comparison_path = OUT / f'{partition}.comparisons.v001.csv'
    write_once(result_path, response)
    write_csv_once(controls_path, controls)
    write_csv_once(comparison_path, comparison_rows)
    if partition == 'development':
        write_once(DEVLOCK, {'status': 'DEVELOPMENT_ANALYSIS_LOCKED_BEFORE_HOLDOUT',
                            'locked_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                            'feature_sha256': digest(FEATURES), 'code_sha256': digest(__file__),
                            'files': {rel(p): digest(p) for p in [result_path, controls_path, comparison_path]}})
    else:
        write_once(OUT / 'holdout.lock.v001.json', {
            'status': 'SINGLE_LATER_LABEL_REVEAL_COMPLETED', 'locked_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            'development_lock_sha256': digest(DEVLOCK), 'code_sha256': digest(__file__),
            'files': {rel(p): digest(p) for p in [result_path, controls_path, comparison_path]}})
    print(json.dumps(clean({k: response[k] for k in ['partition', 'n_selected_points',
                           'n_raw_horizon_records', 'n_mature_12m_feature_eligible',
                           'independence_12m', 'credit_interaction_gate', 'multiple_testing']})))


def percentage(x):
    return 'UNKNOWN' if x is None else f'{100*x:.2f}%'


def metric_row(x):
    d, g1, g0 = x['group_difference'], x['group1'], x['group0']
    interval = d['ci95']
    return '|'.join([x['variable'], str(g1['n_raw']), str(g0['n_raw']),
                     percentage(g1['mean']), percentage(g0['mean']),
                     percentage(d['difference_date_equal']),
                     'UNKNOWN' if interval is None else f'[{percentage(interval[0])}, {percentage(interval[1])}]',
                     d['status']])


def report_write(name, lines):
    path = ROOT / name
    path.write_text('\n'.join(lines) + '\n')


def reports():
    verify_registration()
    verify_devlock()
    dev = read(OUT / 'development.results.v001.json')
    later = read(OUT / 'holdout.results.v001.json') if (OUT / 'holdout.lock.v001.json').exists() else None
    partitions = [dev] + ([later] if later else [])
    selected = sum(r['n_selected_points'] for r in partitions)
    eligible = sum(r['n_feature_eligible_points'] for r in partitions)
    mature = sum(r['n_mature_12m_feature_eligible'] for r in partitions)
    report = ['# Phase 3 扩展面板报告', '',
              '状态：LEVEL 1 — DESCRIPTIVE；没有运行或调参旧择时规则，没有新增投资原则。', '',
              '## RAW OBSERVATIONS', '',
              f'已分析固定选择格 {selected}；价格feature合格 {eligible}；合格且成熟12m {mature}。六期限记录是同一起点的重复标签，不是六次独立决策。', '',
              '## EFFECTIVE SAMPLE ASSESSMENT', '',
              'N_effective = null。按同季度、年度和固定两年块共同抽样；跨资产同一全球冲击、行业相关和12/24m持有期重叠仍存在。混合当地币的日期等权均值只描述分布，不是可交易组合、alpha或独立实验数。', '',
              '价格源属于今天重构历史，非当时vendor vintage；当前存续ETF/指数无退市证券池。指数多为当地价格回报，DAX为performance index内含分红，不能当普通price-only指数横比。ETF股息是provider条件性除息日再投资，非真实付款日执行。', '',
              '## 预登记变量及全部结果', '',
              'r252正/非正、252session峰值回撤≤−20%、当前vol高于过去滚动vol中位数，以及合格原SLOOS收紧/未收紧。没有阈值优化；收益不冒充估值，回撤不证明便宜。相对vol采用H-P3-VOL-ENDPOINT-v001：252个此前rolling252vol严格排当前，需要505prices；只有504条时该比较UNKNOWN，其他features不删除。']
    for p in partitions:
        report += ['', f"### {p['partition']}：主12m全资产日期等权", '',
                   '|变量|组1 N raw|组0 N raw|组1均值|组0均值|日期等权差|95%两年块区间|区间状态|',
                   '|---|---:|---:|---:|---:|---:|---|---|']
        for x in p['all_results']:
            if x['cohort_type'] == 'ALL' and x['horizon'] == '12m':
                report.append('|' + metric_row(x) + '|')
        report += ['', f"成熟标签六期限：{json.dumps(p['mature_labels_by_horizon'], ensure_ascii=False)}；只有价格feature合格起点进入变量比较。", '',
                   f"所有 {p['multiple_testing']['single_variable_comparison_slots']} 分组槽位（含不可判定）、所有六期限/资产/市场/行业/年代交叉均保存于 `research/phase3/analysis/{p['partition']}.results.v001.json`，摘要CSV与完整逐行负对照旁置。", '',
                   '组内分布均值、中位数、正收益比例、P25/P75/P10/P90、平均及最差MDD与同执行基准差均保存；自身被动基准差恒为0，不能据此称edge。']
    report += ['', '## 反例与稳定性边界', '',
               '逐行负对照保留GROUP1_NONPOSITIVE、GROUP0_POSITIVE及其相反两类；不同市场/行业/年代的方向相反不被删去。波动和信用不自动假设组1看涨。', '',
               '相对SPY/BIL或固定50/50、60/40、70/30只能在同执行日期和同币种可配对时报告，海外缺当地现金为UNKNOWN；这些比较仍不控制全部beta、风险/生存差异，不证明错误定价。', '',
               '主12m、副24m，其余期限描述。统计区间是探索性依赖敏感区间，少于4块标不可靠；多重比较没有校正成确认性发现。']
    report_write('EXPANDED_PANEL_REPORT.md', report)
    eff = ['# 有效样本与独立性报告', '', '## RAW OBSERVATIONS', '',
           f'固定选择格已分析 {selected}，feature合格 {eligible}，成熟主12m {mature}。', '',
           '## EFFECTIVE SAMPLE ASSESSMENT', '',
           'N_effective始终null。日期簇、年度簇、两年块和贪心无重叠数只是独立性诊断，不是有效N估计。美国行业/跨市场均有共同风险，不能把资产数乘日期数当独立世界。', '',
           '|分区|主12m raw|季度簇|年度簇|两年块|12m实际无重叠资产记录合计|24m实际无重叠资产记录合计|',
           '|---|---:|---:|---:|---:|---:|---:|']
    for p in partitions:
        i = p['independence_12m']
        totals = [sum(v['n_actual_nonoverlap'] for v in p['actual_nonoverlap'] if v['horizon'] == h) for h in ['12m', '24m']]
        eff.append(f"|{p['partition']}|{i['n_raw']}|{i['calendar_quarter_clusters']}|{i['year_clusters']}|{i['two_year_calendar_blocks']}|{totals[0]}|{totals[1]}|")
    eff += ['', '每资产按实际entry/exit排序，取最早entry，下一entry≥上一exit才能入选；不看收益挑选。不同资产无重叠总和仍受共同宏观影响。完整point_id清单与子样本分布在各分区results的actual_nonoverlap。', '',
            '固定Q4稀疏切片不能保证252session恰好无重叠。季度末的观察会话不是完整交易日历证明，停牌/极端行情执行不确定仍保留。', '',
            '500次固定seed 20261009、非重叠固定两年calendar块，所有资产同抽块；组内每季度先等权，再跨季度等权。只有1–3块的区间是UNRELIABLE，不做显著性结论。', '',
            '没有计算虚构clustered独立N，没有用p-value或记录增长给候选升级。2000–2025共26个年度标签不等于26个独立全球经济制度。']
    report_write('EFFECTIVE_SAMPLE_REPORT.md', eff)
    cross = ['# 跨时期验证报告', '', '## RAW OBSERVATIONS', '',
             f'开发选择格 {dev["n_selected_points"]}；较晚计算holdout选择格 {later["n_selected_points"] if later else 0}。', '',
             '## EFFECTIVE SAMPLE ASSESSMENT', '',
             '较早年度与较晚年度也有全球共同regime及重叠收益，独立N未知。既有研究已读2003–2025若干起点及2002以后价格路径；2000–2015不是整体未见external OOS。', '',
             '≤2023结果先保存并锁定，开发锁的全部SHA在holdout打开前核验。2024–2025只称COMPUTATIONAL_LATER_LABEL_HOLDOUT_WITH_PRIOR_PATH_EXPOSURE；不是严格未来OOS。没有看holdout后重新拟合、改阈值、改市场或择优期限。', '',
             '## 固定年代：12m全资产组间日期等权差', '',
             '|分区|年代|变量|组1 N|组0 N|组间差|95%区间|', '|---|---|---|---:|---:|---:|---|']
    for p in partitions:
        for x in p['all_results']:
            if x['cohort_type'] == 'era' and x['horizon'] == '12m':
                ci = x['group_difference']['ci95']
                cross.append(f"|{p['partition']}|{x['cohort']}|{x['variable']}|{x['group1']['n_raw']}|{x['group0']['n_raw']}|{percentage(x['group_difference']['difference_date_equal'])}|{'UNKNOWN' if ci is None else '['+percentage(ci[0])+', '+percentage(ci[1])+']'}|")
    cross += ['', '## 保留下来的旧结论', '',
              'Phase2失败的63/252概率规则、每周SPY/BIL切换和两个宏观组合不在本实验重新运行；本研究不能把单变量某一组高收益解释为旧策略复活。估值、盈利修正、Price-In和资本周期缺连续PIT值，不能下时间尺度或增量信息结论。', '',
              '价格趋势只是一种可见状态：即使某年代组间收益差为正，也必须与被动、同风险和信用/基本面匹配才能判断独立预测贡献。大跌后的高平均回报也可能是风险溢价、尾部反弹或幸存者偏差；MDD与失败案例不能省略。', '',
              '## 下一步隔离', '',
              '真正LIVE FORWARD自2026-10-09冻结后启动；首月末2026-10-30尚未来到，应为PENDING_DECISION。不为历史已见价格重新贴live标签，不填月末未发生的预测。']
    report_write('CROSS_TIME_VALIDATION.md', cross)
    testing = ['# 多重检验账本', '', '## RAW OBSERVATIONS', '',
               f'本阶段 {selected} 固定起点，主12m合格成熟 {mature}；六期限与多分组不是独立样本。', '',
               '## EFFECTIVE SAMPLE ASSESSMENT', '',
               '有效N未识别。检验次数与样本次数不同；大量交叉切片共用同一价格和共同regime。所有槽位包括不可判定与失败，不只保存正差。', '',
               '|分区|单变量登记|价格变量|分组规格|期限|单变量比较槽位|两组可比槽位|基准比较槽位|交互登记|运行交互格|参数搜索|',
               '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for p in partitions:
        m = p['multiple_testing']
        testing.append(f"|{p['partition']}|4|3|{m['cohort_specs']}|6|{m['single_variable_comparison_slots']}|{m['available_two_group_comparisons']}|{m['benchmark_comparison_slots']}|1|{m['interaction_cells_run']}|0|")
    testing += ['', f"H-P3-DD-CREDIT开发门槛：{dev['credit_interaction_gate']['status']}；证据：{json.dumps(dev['credit_interaction_gate']['evidence'], ensure_ascii=False)}。门槛固定，两年代各≥8可用日期、信用两组均存在、主12m信用组差同向；失败不调门槛。", '',
                '前阶段多个价格规则、宏观条件、placebo和扰动均已被看过，不能把本阶段当研究者从未筛选过假说的独立实验。这里没有把所有相关比较折算成p值，也没有做最佳组合选择。', '',
                '最多一种预登记经济二元交互；未满足gate则NOT_RUN_GATE_FAILED。没有三变量组合、策略择时或Sharpe优化。所有正差仅LEVEL1_DESCRIPTIVE，未经独立新样本不得晋升。']
    report_write('MULTIPLE_TESTING_LEDGER.md', testing)
    write_once(OUT / ('reports.after_holdout.v001.json' if later else 'reports.development.v001.json'), {
        'report_paths': ['EXPANDED_PANEL_REPORT.md', 'EFFECTIVE_SAMPLE_REPORT.md',
                         'CROSS_TIME_VALIDATION.md', 'MULTIPLE_TESTING_LEDGER.md'],
        'report_sha256': {name: digest(ROOT / name) for name in [
            'EXPANDED_PANEL_REPORT.md', 'EFFECTIVE_SAMPLE_REPORT.md',
            'CROSS_TIME_VALIDATION.md', 'MULTIPLE_TESTING_LEDGER.md']},
        'raw_observations': selected, 'n_effective': None,
        'research_level': 'LEVEL1_DESCRIPTIVE', 'operational_change': False})
    print(json.dumps({'reports_written': 4, 'selected': selected, 'mature12m': mature}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['register', 'development', 'holdout', 'reports'])
    args = parser.parse_args()
    if args.mode == 'register':
        register()
    elif args.mode == 'reports':
        reports()
    else:
        run(args.mode)


if __name__ == '__main__':
    main()
