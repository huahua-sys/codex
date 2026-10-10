#!/usr/bin/env python3
"""Read-only forward engineering review; synthetic fixtures never investment evidence."""
import copy
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location('forward_qa_target', ROOT / 'scripts/phase3_forward_v002.py')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text())

base = ROOT / 'research/phase3/forward_v002'
lock = read(base / 'REGISTRATION.lock.v002.json')
f.verify(lock)
f.verify(read(base / 'ENGINEERING_SAFETY.lock.v002.json'))
f.verify(read(ROOT / 'research/phase3/forward/REGISTRATION.lock.v001.json'))
reg = f.registration()
safety = read(base / 'ENGINEERING_SAFETY.v002.json')
selftest = f.selftest()
assert all(selftest['checks'].values()) and all(safety['checks'].values())
assert safety['actual_early_capture_rejection']['rejected_before_network_and_decision_directory_creation']
assert safety['actual_early_capture_rejection']['network_path_calls'] == 0
assert len(reg['months']) == 24 and len(reg['assets']) == 7
assert reg['genuine_locked_decisions'] == reg['probability_predictions'] == 0
assert not reg['scheduler_deployed']
status = f.status()
assert status['raw_observations'] == status['probability_predictions'] == 0
assert not list((base / 'decisions').glob('**/DECISION.v001.json'))
assert not list((base / 'labels').glob('**/OUTCOMES.v001.json'))
assert not list((ROOT / 'research/phase3/forward/decisions').glob('**/DECISION.v001.json'))
assert not list((ROOT / 'research/phase3/forward/labels').glob('**/OUTCOMES.v001.json'))
f.operative_guard()

# Independently derive all feature formulae from simple synthetic close returns.
rows = []
day = dt.date(2020, 1, 2)
for i in range(505):
    while day.weekday() >= 5:
        day += dt.timedelta(days=1)
    value = 100 + i * .01 + np.sin(i / 9) * 3
    if i == 252:
        value = 1700.0
    rows.append({'record_id': 'SYNTHETIC:' + str(day), 'date': str(day),
        'session_open_at': str(day) + 'T14:00:00+00:00',
        'session_close_at': str(day) + 'T21:00:00+00:00',
        'available_at': '2026-10-09T12:00:00+00:00',
        'open': float(value), 'high': float(value * 1.01),
        'low': float(value * .99), 'close': float(value),
        'source_id': 'SYNTHETIC', 'source_sha256': '0' * 64,
        'pit_status': 'RETAINED_IN_ACTUAL_FORWARD_CAPTURE'})
    day += dt.timedelta(days=1)
bundle = {'prices': rows, 'actions': [], 'retained_at': '2026-10-09T12:00:00+00:00',
    'split_units_verified': True, 'adjclose_used': False, 'action_coverage': 'COMPLETE',
    'metadata': {'price_basis': 'AS_REPORTED_OHLC_NO_ADJCLOSE',
        'no_splits_in_analysis_interval_confirmed': True,
        'total_return_eligible': True, 'split_action_validation_required': False}}
values = np.array([r['close'] for r in rows])
returns = values[1:] / values[:-1] - 1
expected = {'r252_known_action_wealth': values[-1] / values[-253] - 1,
    'drawdown252': values[-1] / max(values[-252:]) - 1,
    'vol252': np.std(returns[-252:], ddof=1) * np.sqrt(252),
    'vol252_prior252_median': np.median([
        np.std(returns[i:i+252], ddof=1) * np.sqrt(252) for i in range(252)])}
observed = f.features(bundle, rows[-1]['date'][:7], dt.date.fromisoformat(rows[-1]['date']))
for key, value in expected.items():
    assert np.isclose(observed[key], value, rtol=1e-12, atol=1e-12), key
assert observed['vol_group'] == ('HIGH' if expected['vol252'] > expected['vol252_prior252_median'] else 'NOT_HIGH')
short = dict(bundle, prices=rows[:-1])
assert f.features(short, rows[-2]['date'][:7], dt.date.fromisoformat(rows[-2]['date']))['vol_group'] is None

# Complete valid but different internal sequences, with identical endpoints/count.
dates = ['2026-10-01', '2026-10-02', '2026-10-05', '2026-10-06']
label = {'status': 'REVEALED', 'sessions_held': 3, 'entry_date': dates[0], 'exit_date': dates[-1],
    'execution_session_dates': dates, 'execution_session_dates_sha256': f.object_digest(dates), 'net_return': .03}
assert f.aligned_bil(label, copy.deepcopy(label), 'USD', 'USD')
changed_dates = ['2026-10-01', '2026-10-03', '2026-10-05', '2026-10-06']
other = dict(label, execution_session_dates=changed_dates,
    execution_session_dates_sha256=f.object_digest(changed_dates))
assert not f.aligned_bil(label, other, 'USD', 'USD')
for change in ({'execution_session_dates_sha256': None}, {'sessions_held': 0},
    {'sessions_held': True}, {'status': 'PENDING_HORIZON'}, {'net_return': None}):
    assert not f.aligned_bil(label, dict(label, **change), 'USD', 'USD')
assert not f.aligned_bil(label, label, 'HKD', 'USD')
assert not f.aligned_bil(label, label, 'USD', 'EUR')

# Final full baseline preservation: authorized mutable root memory is excluded.
prior = read(ROOT / 'research/phase3/audit/PRIOR_STATE.v001.json')
changed = []
for relative, details in prior['immutable_file_hashes'].items():
    path = ROOT / relative
    if not path.exists() or path.stat().st_size != details['bytes'] or digest(path) != details['sha256']:
        changed.append(relative)
assert not changed, changed
report = {'audit_id': 'PHASE3_FORWARD_V002_FINAL_QA_V008', 'status': 'PASS',
    'reviewed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
    'audit_code_sha256': digest(Path(__file__)),
    'RAW OBSERVATIONS': {'real_captures': 0, 'real_decisions': 0, 'probability_forecasts': 0,
        'mature_forward_labels': 0, 'pending_months': 24, 'pending_asset_slots': 168,
        'synthetic_selftest_checks': len(selftest['checks']),
        'frozen_safety_checks': len(safety['checks']), 'old_immutable_files_verified': len(prior['immutable_file_hashes'])},
    'EFFECTIVE SAMPLE ASSESSMENT': {'independent_real_n': None, 'completed_real_month_clusters': 0,
        'notes': ['Appointments and synthetic engineering tests are not historical or forward investment observations.',
            'Future monthly horizons overlap; seven assets share shocks; no externally witnessed timestamps or scheduler.']},
    'registration_dependency_hashes_verified': len(lock['files']),
    'script_sha256': digest(ROOT / 'scripts/phase3_forward_v002.py'),
    'registration_lock_sha256': digest(base / 'REGISTRATION.lock.v002.json'),
    'v001_preserved_and_not_activated': True,
    'operative_9_fields_equal_to_phase2': True,
    'features_independent_numpy_parity': dict(zip(expected, [True] * len(expected))),
    'strict_505_price_endpoint_504_unknown': True,
    'same_endpoints_different_valid_internal_session_sequences_rejected': True,
    'missing_session_proofs_fail_closed': True,
    'actual_early_capture_rejection_verified_from_locked_evidence': True,
    'old_immutable_changed': changed,
    'limitations': ['Per-market observed sessions use normal clocks rather than full exchange calendars.',
        'ETF return remains conditional provider-reported ex-date reinvestment, with fixed 50bp assumption.',
        'No live probability forecasts, trades, calibration evidence, local foreign-market cash or FX comparators.',
        'Current-retained historical provider history is not an original historical vendor vintage.']}
target = ROOT / 'research/phase3/audit/FORWARD_V002_FINAL_QA.v008.json'
assert not target.exists()
target.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'report': str(target),
    'source_locks': len(lock['files']), 'old_immutable_files': len(prior['immutable_file_hashes']),
    'raw_real_observations': 0, 'synthetic_only': True}))
