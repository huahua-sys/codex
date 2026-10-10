#!/usr/bin/env python3
"""Append-only v002 actual-time monthly collection; no historical import as LIVE.

No scheduler is installed. `register` creates pending appointments, not decisions.
`capture` downloads raw bytes now, and `evaluate` can append later outcome labels.
There is intentionally no --as-of / --now override or historic import option.
"""
from __future__ import annotations
import argparse
import calendar
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import tempfile
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lab.schema import historical_wealth, json_bytes, sha256, timestamp, write_once
from lab.evaluate import evaluate_path

UTC = dt.timezone.utc
BASE = ROOT / 'research/phase3/forward_v002'
PARENT_BASE = ROOT / 'research/phase3/forward'
OPERATIVE_KEYS = ('validated_principles', 'candidate_principles', 'regime_rules',
                  'industry_specific_rules', 'signals_to_monitor', 'sell_signals',
                  'risk_signals', 'price_in_checks', 'live_signal_generation_enabled')
WATCHLIST = ('SPY', 'SSE', 'HSI', 'N225', 'STOXX50E', 'GLD', 'BIL')
UNKNOWN_FIELDS = ('Valuation', 'EarningsRevision', 'EarningsQuality', 'Breadth',
                  'Credit', 'CapitalCycle', 'PriceIn', 'LocalCashReturn', 'FX')
MONTHS = 24  # finite initial appointments; additions require an append-only version
CLOCKS = {'US': (9, 30, 16, 0), 'CN': (9, 30, 15, 0),
          'HK': (9, 30, 16, 0), 'JP': (9, 0, 15, 30), 'EU': (9, 0, 18, 0)}


def now():
    return dt.datetime.now(UTC)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def verify(lock):
    for relative, digest in lock['files'].items():
        if sha256(ROOT / relative) != digest:
            raise ValueError('Locked dependency changed: ' + relative)


def month_anchor(month):
    day = dt.date.fromisoformat(month + '-01')
    day = day.replace(day=calendar.monthrange(day.year, day.month)[1])
    while day.weekday() >= 5:
        day -= dt.timedelta(days=1)
    return day


def assert_capture_window(month, actual):
    """Calendar appointment, not a fabricated exchange holiday calendar."""
    anchor = month_anchor(month)
    # US16:00 is20:00UTC in summer,21:00UTC in winter. No early winter lock.
    start = dt.datetime.combine(anchor, dt.time(16), ZoneInfo('America/New_York')).astimezone(UTC)
    end = dt.datetime.combine(anchor + dt.timedelta(days=4), dt.time(0), UTC)
    if not start <= actual < end:
        raise ValueError('PENDING_OR_MISSED_DECISION: actual UTC time must be '
                         'month-end weekday after US16:00 close or within next 3 calendar days')
    return anchor


def operative_guard():
    prior = read(ROOT / 'research/phase3/audit/PRIOR_OPERATIVE_FRAMEWORK.v001.json')['operative_framework']
    current = read(ROOT / 'CURRENT_FRAMEWORK.json')
    if {key: current.get(key) for key in OPERATIVE_KEYS} != {key: prior.get(key) for key in OPERATIVE_KEYS}:
        raise ValueError('Operative framework changed; new forward hypothesis/version required')
    if prior['validated_principles'] or prior['live_signal_generation_enabled']:
        raise ValueError('No permission for operational investment signal')
    return prior


def registration():
    lock = read(BASE / 'REGISTRATION.lock.v002.json')
    verify(lock)
    return read(BASE / 'REGISTRATION.v002.json')


def register():
    verify(read(PARENT_BASE / 'REGISTRATION.lock.v001.json'))
    verify(read(ROOT / 'research/phase3/PROTOCOL.lock.v001.json'))
    if (BASE / 'REGISTRATION.lock.v002.json').exists():
        reg = registration()
        return {'status': 'ALREADY_REGISTERED_VERIFIED', 'pending_months': len(reg['months'])}
    design = read(ROOT / 'research/phase3/design.v001.json')
    if design['forward_decision'] != 'NO_RESEARCH_TRADE_BENCHMARK_ONLY_NO_VALIDATED_EDGE':
        raise ValueError('Unexpected operative forward instruction')
    by_id = {a['asset_id']: a for a in design['assets']}
    operative = operative_guard()
    if operative['validated_principles'] or operative['live_signal_generation_enabled']:
        raise ValueError('Current frozen framework does not permit benchmark-only protocol')
    year, mon = map(int, design['first_live_month_end'][:7].split('-'))
    appointments = []
    for offset in range(MONTHS):
        y, m = year + (mon - 1 + offset) // 12, (mon - 1 + offset) % 12 + 1
        month = f'{y:04d}-{m:02d}'
        appointments.append({'month': month, 'calendar_weekday_anchor': str(month_anchor(month)),
                             'status': 'PENDING_DECISION', 'decision_at': None,
                             'asset_decisions': [], 'predictions': []})
    reg = {'study_id': 'PHASE3-LIVE-FORWARD-v002', 'registered_at': now().isoformat(),
           'parent_registration_sha256': sha256(PARENT_BASE / 'REGISTRATION.lock.v001.json'),
           'parent_status': 'V001_ENGINEERING_BETA_NOT_ACTIVATED_NO_REAL_CAPTURE',
           'correction_scope': 'Feature-definition parity and complete held-session benchmark fail-closed; no investment rule change',
           'operative_keys': list(OPERATIVE_KEYS),
           'assets': [by_id[a] for a in WATCHLIST], 'months': appointments,
           'horizons': design['horizons'], 'roundtrip_cost_bps_assumed': 50,
           'decision_policy': design['forward_decision'],
           'features': ['r252_known_action_wealth', 'drawdown252', 'vol252', 'vol252_prior252_median', 'vol_group'],
           'feature_definition': 'r252=W[-1]/W[-253]-1; drawdown252=W[-1]/max(W[-252:])-1; vol252=sample_stdev(last252 simple daily wealth returns)*sqrt252; reference=median252 prior rolling252 estimates excludingcurrent, needs505 prices',
           'benchmark_alignment': 'Two REVEALED positive-n USD outcomes with same entry/exit, n_sessions and full held-session-date sequence SHA; missing proof yields UNKNOWN',
           'corporate_action_policy': 'All unverified splits quarantined; no ordinary-split override for fixed seven assets',
           'valuation_earnings_credit_unavailable_policy': 'UNKNOWN_NOT_IMPUTED',
           'capture_window': 'Month-end weekday after US16:00 close through next3 calendar days, summer20/winter21UTC',
           'actual_decision_time': 'REAL_LOCK_TIME_AFTER_ALL_CURRENT_RAW_SOURCE_RETRIEVALS',
           'late_capture_policy': 'Label actual delayed decision; next observed open after real lock time',
           'calendar_limit': 'Anchor is last weekday; per-market session is last full source-observed month bar, not exchange-calendar audited',
           'raw_observations': 0, 'genuine_locked_decisions': 0, 'probability_predictions': 0,
           'effective_sample_assessment': {'n_effective': None, 'live_month_clusters': 0,
                 'mature_labels': 0, 'warning': 'Seven assets are correlated; monthly 12/24m returns overlap'},
           'scheduler_deployed': False,
           'trust_limit': 'Current UTC and local append-only SHA, not externally witnessed timestamp or tamper-proof storage'}
    reg_path = BASE / 'REGISTRATION.v002.json'
    write_once(reg_path, reg)
    files = ['scripts/phase3_forward_v002.py', 'scripts/phase3_forward.py',
             'scripts/phase3_panel.py', 'lab/schema.py', 'lab/evaluate.py',
             'research/phase3/H-P3-VOL-ENDPOINT-v001.json',
             'research/phase3/H-P3-VOL-ENDPOINT-v001.lock.json',
             'research/phase3/forward/REGISTRATION.v001.json',
             'research/phase3/forward/REGISTRATION.lock.v001.json',
             'research/phase3/forward_v002/CORRECTION.md',
             'SAMPLE_EXPANSION_PROTOCOL.md', 'research/phase3/design.v001.json',
             'research/phase3/PROTOCOL.lock.v001.json',
             'research/phase3/audit/PRIOR_OPERATIVE_FRAMEWORK.v001.json', str(reg_path.relative_to(ROOT))]
    write_once(BASE / 'REGISTRATION.lock.v002.json',
               {'locked_at': now().isoformat(), 'files': {f: sha256(ROOT / f) for f in files},
                'scope': 'Appointments/policy locked; pending appointments contain no decision or forecast'})
    return {'status': 'PENDING_DECISION', 'pending_months': MONTHS,
            'scheduled_asset_slots': MONTHS * len(WATCHLIST), 'actual_live_decisions': 0}


def decode_snapshot(body, asset, retained_at, received_at=None):
    """Only full observed OHLC; no AdjClose; unknown split units quarantined."""
    chart = json.loads(body)['chart']
    if chart.get('error') or not chart.get('result'):
        raise ValueError('Source returned no valid chart')
    data = chart['result'][0]
    if data.get('meta', {}).get('symbol') != asset['symbol']:
        raise ValueError('SOURCE_SYMBOL_MISMATCH_OR_MISSING')
    quotes = data['indicators']['quote'][0]
    zone = ZoneInfo(asset['timezone'])
    source = 'LIVE_YAHOO_' + asset['asset_id']
    digest = hashlib.sha256(body).hexdigest()
    prices, actions, rejected = [], [], []
    for i, stamp in enumerate(data.get('timestamp', [])):
        day = dt.datetime.fromtimestamp(stamp, zone).date()
        o_h, o_m, c_h, c_m = CLOCKS[asset['market']]
        opening = dt.datetime.combine(day, dt.time(o_h, o_m), zone).astimezone(UTC)
        closing = dt.datetime.combine(day, dt.time(c_h, c_m), zone).astimezone(UTC)
        values = {k: quotes.get(k, [None] * len(data['timestamp']))[i]
                  for k in ('open', 'high', 'low', 'close')}
        if closing > (received_at or retained_at) or not all(isinstance(v, (int, float)) and math.isfinite(v) and v > 0 for v in values.values()):
            rejected.append({'date': str(day), 'reason': 'INCOMPLETE_OR_INVALID_OHLC'})
            continue
        if values['high'] < max(values.values()) or values['low'] > min(values.values()):
            raise ValueError('Inconsistent OHLC')
        prices.append({'record_id': source + ':' + str(day), 'asset_id': asset['asset_id'],
                       'date': str(day), 'session_open_at': opening.isoformat(),
                       'session_close_at': closing.isoformat(),
                       'available_at': retained_at.isoformat(), **values,
                       'source_id': source, 'source_sha256': digest,
                       'pit_status': 'RETAINED_IN_ACTUAL_FORWARD_CAPTURE',
                       'quality_flags': ['CURRENT_PROVIDER_HISTORY_AT_REAL_CAPTURE',
                                         'NORMAL_SESSION_CLOCK_NOT_COMPLETE_CALENDAR']})
    for category, kind in (('dividends', 'dividend'), ('splits', 'split')):
        for event in data.get('events', {}).get(category, {}).values():
            if asset['instrument_type'] != 'ETF':
                raise ValueError('Unexpected index action; price-only units require quarantine')
            day = dt.datetime.fromtimestamp(event['date'], zone).date()
            if day > retained_at.astimezone(zone).date():
                raise ValueError('Future-dated action: unavailable action units require quarantine')
            action = {'record_id': source + ':' + kind + ':' + str(day),
                      'asset_id': asset['asset_id'], 'date': str(day), 'action_type': kind,
                      'available_at': retained_at.isoformat(), 'source_id': source,
                      'source_sha256': digest}
            if kind == 'dividend':
                action['amount'] = float(event['amount'])
                if not math.isfinite(action['amount']) or action['amount'] < 0:
                    raise ValueError('Invalid dividend')
            else:
                action['ratio'] = float(event['numerator']) / float(event['denominator'])
            actions.append(action)
    prices.sort(key=lambda r: r['date'])
    if len({r['date'] for r in prices}) != len(prices):
        raise ValueError('Duplicate observed session')
    no_splits = not any(a['action_type'] == 'split' for a in actions)
    return {'asset_id': asset['asset_id'], 'prices': prices, 'actions': actions,
            'metadata': {'price_basis': 'AS_REPORTED_OHLC_NO_ADJCLOSE',
                         'no_splits_in_analysis_interval_confirmed': no_splits,
                         'split_action_validation_required': not no_splits,
                         'total_return_eligible': no_splits and asset['instrument_type'] == 'ETF',
                         'source_symbol': data['meta']['symbol'],
                         'original_vintage_status': 'CURRENT_PROVIDER_BYTES_RETAINED_AT_ACTUAL_TIME'},
            'split_units_verified': no_splits,
            'retained_at': retained_at.isoformat(), 'source_sha256': digest,
            'adjclose_used': False, 'rejected_rows': rejected,
            'action_coverage': 'COMPLETE' if asset['instrument_type'] == 'ETF' else 'NOT_APPLICABLE_PRICE_INDEX',
            'return_quality': 'CONDITIONAL_PROVIDER_REPORTED_EXDATE_RETURN' if asset['instrument_type'] == 'ETF' else 'NONTRADEABLE_NATIVE_PRICE_INDEX'}


def snapshot(asset, directory, start):
    """Raw bytes and local retrieval evidence saved before decoding."""
    requested = now()
    period1 = int(dt.datetime.combine(start, dt.time(), UTC).timestamp())
    url = ('https://query1.finance.yahoo.com/v8/finance/chart/' +
           urllib.parse.quote(asset['symbol'], safe='') + '?' +
           urllib.parse.urlencode({'period1': period1, 'period2': int(requested.timestamp()) + 1,
                                   'interval': '1d', 'events': 'div,splits'}))
    evidence = {'asset_id': asset['asset_id'], 'source_url': url,
                'requested_at': requested.isoformat(), 'status': 'SOURCE_UNAVAILABLE'}
    directory.mkdir(parents=True, exist_ok=True)
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 InvestmentResearchLab Live/0.1'})
        with urllib.request.urlopen(request, timeout=25) as response:
            body = response.read()
            headers = {k: v for k, v in response.headers.items() if k.lower() in ('date', 'etag', 'last-modified', 'content-type')}
        received = now()
        raw = directory / (asset['asset_id'] + '.raw.json')
        with raw.open('xb') as stream:
            stream.write(body)
        retained = now()
        evidence.update(received_at=received.isoformat(), retained_at=retained.isoformat(), source_sha256=sha256(raw),
                        raw_path=str(raw.relative_to(ROOT)), response_headers=headers)
        bundle = decode_snapshot(body, asset, retained, received)
        canonical = directory / (asset['asset_id'] + '.snapshot.json')
        write_once(canonical, bundle)
        evidence.update(status='SOURCE_RETAINED', canonical_path=str(canonical.relative_to(ROOT)),
                        canonical_sha256=sha256(canonical))
    except Exception as error:
        evidence.update(error_type=type(error).__name__, error=str(error), failed_at=now().isoformat())
    write_once(directory / (asset['asset_id'] + '.retrieval.json'), evidence)
    return evidence


def source_qualification(bundle):
    """Same conservative unit/action policy as panel; no proof-free split override."""
    metadata = bundle.get('metadata', {})
    if metadata.get('price_basis') != 'AS_REPORTED_OHLC_NO_ADJCLOSE' or bundle.get('adjclose_used') is not False:
        return 'UNRESOLVED_PRICE_UNITS'
    if (not bundle.get('split_units_verified') or not metadata.get('no_splits_in_analysis_interval_confirmed')
            or metadata.get('split_action_validation_required') or any(a.get('action_type') == 'split' for a in bundle.get('actions', []))):
        return 'UNRESOLVED_SPLIT_UNITS'
    if bundle.get('action_coverage') == 'COMPLETE' and not metadata.get('total_return_eligible'):
        return 'UNRESOLVED_CORPORATE_ACTION_COVERAGE'
    if bundle.get('action_coverage') not in ('COMPLETE', 'NOT_APPLICABLE_PRICE_INDEX'):
        return 'UNRESOLVED_CORPORATE_ACTION_COVERAGE'
    return None


def validate_actual_records(rows, actions, cutoff_at):
    """Actual retention markers are not relabelled as historic original vintages."""
    cutoff = timestamp(cutoff_at)
    seen, dates, action_keys = set(), set(), set()
    for row in rows + actions:
        if row.get('record_id') in seen or not row.get('record_id'):
            raise ValueError('Missing/duplicate actual snapshot record')
        seen.add(row['record_id'])
        if row.get('pit_status', 'RETAINED_IN_ACTUAL_FORWARD_CAPTURE') != 'RETAINED_IN_ACTUAL_FORWARD_CAPTURE':
            raise ValueError('Unexpected actual retention PIT marker')
        available = timestamp(row['available_at'])
        if available > cutoff or dt.date.fromisoformat(row['date']) > available.date():
            raise ValueError('POST_ACTUAL_CUTOFF record rejected')
        if not row.get('source_id') or not row.get('source_sha256'):
            raise ValueError('Missing actual retained provenance')
        if 'close' in row:
            opening, closing = timestamp(row['session_open_at']), timestamp(row['session_close_at'])
            if not opening < closing <= available:
                raise ValueError('Incomplete session or unavailable OHLC')
            if row['date'] in dates:
                raise ValueError('Duplicate actual session')
            dates.add(row['date'])
            values = [row[k] for k in ('open', 'high', 'low', 'close')]
            if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v > 0 for v in values):
                raise ValueError('Invalid actual OHLC')
            if row['high'] < max(values) or row['low'] > min(values):
                raise ValueError('Inconsistent actual OHLC')
        else:
            key = (row['date'], row.get('action_type'))
            if key in action_keys or row.get('action_type') != 'dividend':
                raise ValueError('Duplicate or unqualified actual action')
            action_keys.add(key)
            amount = row.get('amount')
            if not isinstance(amount, (int, float)) or not math.isfinite(amount) or amount < 0:
                raise ValueError('Invalid actual dividend')


def features(bundle, month, anchor, cutoff_at=None):
    rows = [r for r in bundle['prices'] if r['date'][:7] <= month]
    unknown = {'r252_known_action_wealth': None, 'drawdown252': None, 'vol252': None,
               'vol252_prior252_median': None, 'vol_group': None,
               'volatility_reference_estimates': 0, 'relative_vol_status': 'INSUFFICIENT_HISTORY'}
    reason = source_qualification(bundle)
    if reason:
        return {**unknown, 'status': reason}
    if not rows or (anchor - dt.date.fromisoformat(rows[-1]['date'])).days > 10:
        return {**unknown, 'status': 'STALE_OR_MISSING_MONTH_SOURCE'}
    if rows[-1]['date'][:7] != month or len(rows) < 253:
        return {**unknown, 'status': 'INSUFFICIENT_COMPLETE_MONTH_HISTORY'}
    dates = {r['date'] for r in rows}
    actions = [a for a in bundle['actions'] if a['date'] in dates]
    actual_cutoff = cutoff_at or bundle['retained_at']
    validate_actual_records(rows, actions, actual_cutoff)
    chain = historical_wealth(rows, actions)
    wealth = [value for _, value in chain]
    daily = [wealth[i] / wealth[i - 1] - 1 for i in range(1, len(wealth))]
    vol = statistics.stdev(daily[-252:]) * math.sqrt(252)
    result = {**unknown, 'status': 'KNOWN_AT_ACTUAL_CAPTURE',
              'last_month_observed_session': rows[-1]['date'],
              'month_session_quality': 'LAST_SOURCE_OBSERVED_NOT_CALENDAR_VERIFIED',
              'r252_known_action_wealth': wealth[-1] / wealth[-253] - 1,
              'drawdown252': wealth[-1] / max(wealth[-252:]) - 1,
              'vol252': vol, 'relative_vol_status': 'INSUFFICIENT_252_PRIOR_ESTIMATES',
              'historical_provider_revision_limit': 'Historical inputs as exposed in now-retained live source, not earlier original vintages'}
    if len(wealth) >= 505:
        tail = daily[-504:]
        first, second = [0.0], [0.0]
        for value in tail:
            first.append(first[-1] + value)
            second.append(second[-1] + value * value)
        rolling = []
        for i in range(252):
            total, squares = first[i + 252] - first[i], second[i + 252] - second[i]
            variance = max(0.0, (squares - total * total / 252) / 251)
            rolling.append(math.sqrt(variance * 252))
        ref = statistics.median(rolling)
        result.update(vol252_prior252_median=ref,
                      vol_group='HIGH' if vol > ref else 'NOT_HIGH',
                      volatility_reference_estimates=252,
                      relative_vol_status='AVAILABLE_252_PRIOR_ESTIMATES_EXCLUDING_CURRENT')
    return result


def object_digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def execution_label(bundle, asset, cutoff_at, sessions, cost_bps):
    """Outcome session proof includes entry, each held date, and exit date."""
    if isinstance(sessions, bool) or not isinstance(sessions, int) or sessions < 1:
        raise ValueError('Outcome sessions must be positive integer')
    reason = source_qualification(bundle)
    if reason:
        return {'status': reason, 'net_return': None, 'execution_session_dates_sha256': None}
    validate_actual_records(bundle['prices'], bundle['actions'], bundle['retained_at'])
    rows = sorted([r for r in bundle['prices'] if timestamp(r['session_open_at']) > timestamp(cutoff_at)],
                  key=lambda r: timestamp(r['session_open_at']))
    outcome = evaluate_path(bundle['prices'], bundle['actions'], cutoff_at, sessions,
                           bundle['action_coverage'], 'TOTAL_RETURN' if asset['instrument_type'] == 'ETF' else 'PRICE_ONLY',
                           cost_bps, 'EXCHANGE_TRADED_ETF' if asset['instrument_type'] == 'ETF' else 'NONTRADEABLE_INDEX_BENCHMARK_ONLY')
    dates = [r['date'] for r in rows[:sessions + 1]]
    if outcome['status'] == 'REVEALED':
        if len(dates) != sessions + 1 or len(set(dates)) != len(dates) or dates[0] != outcome['entry_date'] or dates[-1] != outcome['exit_date']:
            raise ValueError('Outcome complete execution-session proof failed')
        outcome.update(execution_session_dates=dates, execution_session_dates_sha256=object_digest(dates),
                       execution_session_proof='FULL_ORDERED_ENTRY_THROUGH_EXIT_OBSERVED_SESSION_DATES')
    else:
        outcome.update(execution_session_dates=None, execution_session_dates_sha256=None)
    return outcome


def aligned_bil(label, cash, currency, benchmark_currency):
    if currency != benchmark_currency or currency != 'USD':
        return False
    for value in (label, cash):
        digest = value.get('execution_session_dates_sha256')
        sessions = value.get('sessions_held')
        dates = value.get('execution_session_dates')
        if (value.get('status') != 'REVEALED' or not isinstance(digest, str) or len(digest) != 64
                or any(char not in '0123456789abcdef' for char in digest)
                or isinstance(sessions, bool) or not isinstance(sessions, int) or sessions < 1
                or not isinstance(dates, list) or len(dates) != sessions + 1
                or len(set(dates)) != len(dates) or dates != sorted(dates)
                or not value.get('entry_date') or not value.get('exit_date')
                or dates[0] != value['entry_date'] or dates[-1] != value['exit_date']
                or object_digest(dates) != digest):
            return False
        net = value.get('net_return')
        if not isinstance(net, (int, float)) or isinstance(net, bool) or not math.isfinite(net):
            return False
    return all(label.get(key) == cash.get(key) for key in
               ('entry_date', 'exit_date', 'sessions_held', 'execution_session_dates_sha256'))


def capture(month):
    reg = registration()
    operative_guard()
    if month not in {m['month'] for m in reg['months']}:
        raise ValueError('Month not in frozen appointments')
    anchor = assert_capture_window(month, now())  # before any network/data read
    directory = BASE / 'decisions' / month
    if directory.exists():
        raise ValueError('Month already attempted; append-only evidence forbids replacement. New attempt requires new hypothesis/version')
    directory.mkdir(parents=True)
    start = dt.date.fromisoformat(month + '-01') - dt.timedelta(days=1200)
    sources = [snapshot(asset, directory / 'sources', start) for asset in reg['assets']]
    decision_at = now()
    assert_capture_window(month, decision_at)
    decisions = []
    for asset, source in zip(reg['assets'], sources):
        record = {'asset_id': asset['asset_id'], 'market': asset['market'], 'currency': asset['currency'],
                  'decision': 'NO_RESEARCH_TRADE', 'decision_scope': 'BENCHMARK_ONLY_NOT_EXECUTED_ORDER',
                  'p_up': None, 'probability_range': None, 'source': source,
                  'unknown_fields': {f: 'UNKNOWN_NOT_IMPUTED' for f in UNKNOWN_FIELDS},
                  'features': {'status': 'SOURCE_UNAVAILABLE', 'r252_known_action_wealth': None,
                               'drawdown252': None, 'vol252': None}}
        if source['status'] == 'SOURCE_RETAINED':
            if timestamp(source['retained_at']) > decision_at:
                raise ValueError('Source retained after decision')
            record['features'] = features(read(ROOT / source['canonical_path']), month, anchor, decision_at.isoformat())
        decisions.append(record)
    path = directory / 'DECISION.v001.json'
    write_once(path, {'month': month, 'decision_at': decision_at.isoformat(),
              'cutoff_at': decision_at.isoformat(), 'calendar_anchor': str(anchor),
              'timing_status': 'ACTUAL_MONTH_END_CAPTURE' if decision_at.date() == anchor else 'ACTUAL_DELAYED_CAPTURE_NOT_BACKDATED',
              'registered_policy': reg['decision_policy'], 'decisions': decisions,
              'information_set': 'KNOWN_AT_ACTUAL_RETAINED_TIME', 'future_outcomes_accessed': False,
              'raw_observations': len(decisions), 'probability_predictions': 0,
              'effective_sample_assessment': {'n_effective': None, 'month_clusters': 1,
                   'warning': 'Correlated seven-asset decision contexts; no probabilistic forecasts or executed portfolio'},
              'entry_convention': 'First complete observed session open strictly after this actual cutoff; never retroactive month-end execution'})
    paths = [path] + list((directory / 'sources').glob('*'))
    write_once(directory / 'DECISION.lock.v001.json',
               {'locked_at': now().isoformat(), 'files': {str(p.relative_to(ROOT)): sha256(p) for p in paths},
                'registration_sha256': sha256(BASE / 'REGISTRATION.lock.v002.json')})
    return {'status': 'ACTUAL_FORWARD_CONTEXT_LOCKED', 'month': month, 'p_up_forecasts': 0}


def evaluate(month):
    reg = registration()
    directory = BASE / 'decisions' / month
    verify(read(directory / 'DECISION.lock.v001.json'))
    decision = read(directory / 'DECISION.v001.json')
    if timestamp(decision['cutoff_at']) >= now():
        raise ValueError('Outcome evaluation requires real time after locked decision')
    stamp = now().strftime('%Y%m%dT%H%M%S%fZ')
    target = BASE / 'labels' / month / stamp
    start = timestamp(decision['cutoff_at']).date() - dt.timedelta(days=2)
    sources = [snapshot(asset, target / 'sources', start) for asset in reg['assets']]
    results = []
    for asset, source in zip(reg['assets'], sources):
        one = {'asset_id': asset['asset_id'], 'currency': asset['currency'],
               'source': source, 'horizons': {}, 'actual_decision_return': None,
               'decision_scoring_status': 'NO_PROBABILITY_OR_PORTFOLIO_FORECAST_TO_SCORE'}
        if source['status'] == 'SOURCE_RETAINED':
            bundle = read(ROOT / source['canonical_path'])
            for h, sessions in reg['horizons'].items():
                outcome = execution_label(bundle, asset, decision['cutoff_at'], sessions,
                                          reg['roundtrip_cost_bps_assumed'])
                one['horizons'][h] = outcome
        results.append(one)
    bil = next(x for x in results if x['asset_id'] == 'BIL')
    for one in results:
        for h, value in one['horizons'].items():
            cash = bil['horizons'].get(h, {})
            aligned = aligned_bil(value, cash, one['currency'], bil['currency'])
            value['benchmark_difference_vs_BIL'] = value['net_return'] - cash['net_return'] if aligned else None
            value['benchmark_status'] = 'USD_IDENTICAL_SESSIONS_CONDITIONAL_PROVIDER_RETURN' if aligned else 'UNKNOWN_LOCAL_CASH_FX_OR_UNALIGNED_SESSIONS'
    output = {'month': month, 'revealed_at': now().isoformat(), 'decision_sha256': sha256(directory / 'DECISION.v001.json'),
              'role': 'KNOWN_ONLY_AFTER_T_OUTCOME_LABELS', 'decision_modified': False,
              'raw_observations': sum(v.get('status') == 'REVEALED' for r in results for v in r['horizons'].values()),
              'effective_sample_assessment': {'n_effective': None, 'decision_month_clusters': 1,
                    'warning': 'Six horizons overlap; seven assets share global shocks; labels are benchmark outcomes, not edge evidence'},
              'results': results}
    path = target / 'OUTCOMES.v001.json'
    write_once(path, output)
    paths = [path] + list((target / 'sources').glob('*'))
    write_once(target / 'OUTCOMES.lock.v001.json',
               {'locked_at': now().isoformat(), 'files': {str(p.relative_to(ROOT)): sha256(p) for p in paths}})
    return {'status': 'APPENDED_OUTCOME_LABELS', 'month': month,
            'mature_asset_horizon_labels': output['raw_observations'], 'decision_sha256': output['decision_sha256']}


def selftest():
    """Engineering safety checks only; synthetic observations never form principles."""
    checks = {}
    for label, instant in [('before_month_end', '2026-10-09T12:00:00+00:00'),
                           ('early_month_end', '2026-10-30T19:59:59+00:00'),
                           ('missed_window', '2026-11-03T00:00:00+00:00')]:
        try:
            assert_capture_window('2026-10', timestamp(instant))
        except ValueError:
            checks[label + '_rejected'] = True
        else:
            raise AssertionError('Unsafe time accepted')
    assert_capture_window('2026-10', timestamp('2026-10-30T20:01:00+00:00'))
    assert_capture_window('2026-10', timestamp('2026-11-02T23:59:59+00:00'))
    checks['permitted_real_capture_window'] = True
    try:
        assert_capture_window('2026-11', timestamp('2026-11-30T20:30:00+00:00'))
    except ValueError:
        checks['winter_us_close_not_early'] = True
    else:
        raise AssertionError('Early winter capture accepted')
    asset = {'asset_id': 'TEST_SYNTHETIC', 'symbol': 'TEST_SYNTHETIC', 'market': 'US', 'timezone': 'America/New_York', 'instrument_type': 'ETF'}
    body = json_bytes({'chart': {'error': None, 'result': [{'meta': {'symbol': 'TEST_SYNTHETIC'}, 'timestamp': [int(timestamp('2026-10-30T13:30:00+00:00').timestamp())],
            'indicators': {'quote': [{'open': [10], 'high': [11], 'low': [9], 'close': [10]}]}}]}})
    assert decode_snapshot(body, asset, timestamp('2026-10-30T19:00:00+00:00'))['prices'] == []
    checks['incomplete_session_excluded'] = True
    with tempfile.TemporaryDirectory(prefix='phase3_forward_engineering_') as temp:
        path = Path(temp) / 'synthetic.lock.json'
        write_once(path, {'synthetic': True})
        digest = sha256(path)
        try:
            write_once(path, {'synthetic': False})
        except FileExistsError:
            pass
        else:
            raise AssertionError('Overwrite succeeded')
        assert sha256(path) == digest
    checks['append_only_overwrite_rejected_hash_preserved'] = True
    from scripts.phase3_panel import compute_features
    price_rows = []
    day = dt.date(2023, 1, 2)
    for i in range(505):
        while day.weekday() >= 5:
            day += dt.timedelta(days=1)
        opening = dt.datetime.combine(day, dt.time(14), UTC)
        closing = dt.datetime.combine(day, dt.time(21), UTC)
        value = 100 + i * .01 + math.sin(i / 13) * 4
        if i == 252:
            value = 2000.0  # excluded 253rd-old peak distinguishes endpoint convention
        price_rows.append({'record_id': 'SYNTHETIC:' + str(day), 'date': str(day),
                           'session_open_at': opening.isoformat(), 'session_close_at': closing.isoformat(),
                           'available_at': '2026-10-30T22:00:00+00:00',
                           'open': value, 'high': value * 1.001, 'low': value * .999, 'close': value,
                           'source_id': 'SYNTHETIC', 'source_sha256': '0' * 64,
                           'pit_status': 'RETAINED_IN_ACTUAL_FORWARD_CAPTURE'})
        day += dt.timedelta(days=1)
    month = price_rows[-1]['date'][:7]
    anchor = dt.date.fromisoformat(price_rows[-1]['date'])
    bundle = {'prices': price_rows, 'actions': [], 'retained_at': '2026-10-30T22:00:00+00:00',
              'split_units_verified': True, 'adjclose_used': False, 'action_coverage': 'COMPLETE',
              'metadata': {'price_basis': 'AS_REPORTED_OHLC_NO_ADJCLOSE',
                           'no_splits_in_analysis_interval_confirmed': True,
                           'total_return_eligible': True, 'split_action_validation_required': False}}
    observed = features(bundle, month, anchor)
    # Only synthetic markers adapt for main helper contract; real snapshots retain own status.
    main = compute_features([dict(row, pit_status='VERIFIED') for row in price_rows], [],
                            '2026-10-30T22:00:00+00:00', 'TOTAL_RETURN')
    for name, main_name in (('r252_known_action_wealth', 'r252'), ('drawdown252', 'drawdown252'),
                           ('vol252', 'vol252'), ('vol252_prior252_median', 'vol252_prior252_median')):
        assert math.isclose(observed[name], main[main_name], rel_tol=1e-12, abs_tol=1e-12)
    assert observed['vol_group'] == main['vol_group']
    assert observed['volatility_reference_estimates'] == 252
    checks['simple_returns_last252_peak_full_505_parity_with_frozen_panel'] = True
    subset = dict(bundle, prices=price_rows[:504])
    reference_missing = features(subset, price_rows[503]['date'][:7], dt.date.fromisoformat(price_rows[503]['date']))
    assert reference_missing['vol_group'] is None and reference_missing['volatility_reference_estimates'] == 0
    assert reference_missing['r252_known_action_wealth'] is not None
    checks['504_keeps_other_features_relative_vol_unknown'] = True
    try:
        features(bundle, month, anchor, '2026-10-30T21:59:59+00:00')
    except ValueError:
        checks['post_actual_cutoff_retention_rejected'] = True
    else:
        raise AssertionError('Future retained source accepted')
    split = {'date': price_rows[-1]['date'], 'action_type': 'split', 'ratio': 2.0}
    assert features(dict(bundle, actions=[split]), month, anchor)['status'] == 'UNRESOLVED_SPLIT_UNITS'
    checks['ordinary_split_without_independent_admission_quarantined'] = True
    synthetic_label = execution_label(bundle, {'instrument_type': 'ETF'},
                                      price_rows[0]['session_close_at'], 5, 50)
    assert aligned_bil(synthetic_label, dict(synthetic_label), 'USD', 'USD')
    different_dates = list(synthetic_label['execution_session_dates'])
    different_dates[2] = different_dates[1]  # same first/last, missing internal session evidence
    assert not aligned_bil(synthetic_label, dict(synthetic_label, execution_session_dates=different_dates,
                                               execution_session_dates_sha256=object_digest(different_dates)), 'USD', 'USD')
    for change in ({'execution_session_dates_sha256': None}, {'sessions_held': 0},
                   {'sessions_held': True}, {'status': 'PENDING_HORIZON'},
                   {'execution_session_dates': None}):
        assert not aligned_bil(synthetic_label, dict(synthetic_label, **change), 'USD', 'USD')
    assert not aligned_bil(synthetic_label, synthetic_label, 'EUR', 'USD')
    assert not aligned_bil(synthetic_label, synthetic_label, 'USD', 'EUR')
    checks['complete_session_sha_benchmark_fail_closed'] = True
    verify(read(PARENT_BASE / 'REGISTRATION.lock.v001.json'))
    checks['parent_v001_registration_and_sources_unchanged'] = True
    return {'status': 'ENGINEERING_SAFETY_PASS', 'data_kind': 'SYNTHETIC_ONLY_NOT_INVESTMENT_EVIDENCE',
            'checks': checks, 'raw_real_observations': 0, 'effective_real_sample': 0}


def status():
    reg = registration()
    months = []
    for appointment in reg['months']:
        month = appointment['month']
        lock = BASE / 'decisions' / month / 'DECISION.lock.v001.json'
        if lock.exists():
            verify(read(lock))
            value = 'ACTUAL_FORWARD_CONTEXT_LOCKED'
        else:
            anchor = month_anchor(month)
            deadline = dt.datetime.combine(anchor + dt.timedelta(days=4), dt.time(), UTC)
            value = 'PENDING_DECISION' if now() < deadline else 'MISSED_CAPTURE_NOT_BACKFILLED'
        months.append({'month': month, 'current_status': value})
    captured = sum(m['current_status'] == 'ACTUAL_FORWARD_CONTEXT_LOCKED' for m in months)
    return {'status': 'APPEND_ONLY_CURRENT_STATUS', 'as_of': now().isoformat(),
            'months': months, 'raw_observations': captured * len(WATCHLIST),
            'probability_predictions': 0, 'effective_sample_assessment': {
                'n_effective': None, 'month_clusters': captured,
                'warning': 'Correlated contexts are not independent investments'},
            'scheduler_deployed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('register', 'capture', 'evaluate', 'selftest', 'status'))
    parser.add_argument('--month', help='Frozen YYYY-MM appointment, required for capture/evaluate')
    args = parser.parse_args()
    if args.action in ('capture', 'evaluate') and not args.month:
        parser.error('--month is required')
    result = {'register': register, 'selftest': selftest, 'status': status}.get(args.action)
    output = result() if result else (capture(args.month) if args.action == 'capture' else evaluate(args.month))
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    main()
