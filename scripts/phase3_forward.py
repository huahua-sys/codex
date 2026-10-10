#!/usr/bin/env python3
"""Append-only, actual-time monthly collection; no historical import as LIVE.

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
BASE = ROOT / 'research/phase3/forward'
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


def registration():
    lock = read(BASE / 'REGISTRATION.lock.v001.json')
    verify(lock)
    return read(BASE / 'REGISTRATION.v001.json')


def register():
    verify(read(ROOT / 'research/phase3/PROTOCOL.lock.v001.json'))
    if (BASE / 'REGISTRATION.lock.v001.json').exists():
        reg = registration()
        return {'status': 'ALREADY_REGISTERED_VERIFIED', 'pending_months': len(reg['months'])}
    design = read(ROOT / 'research/phase3/design.v001.json')
    if design['forward_decision'] != 'NO_RESEARCH_TRADE_BENCHMARK_ONLY_NO_VALIDATED_EDGE':
        raise ValueError('Unexpected operative forward instruction')
    by_id = {a['asset_id']: a for a in design['assets']}
    operative = read(ROOT / 'research/phase3/audit/PRIOR_OPERATIVE_FRAMEWORK.v001.json')['operative_framework']
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
    reg = {'study_id': 'PHASE3-LIVE-FORWARD-v001', 'registered_at': now().isoformat(),
           'assets': [by_id[a] for a in WATCHLIST], 'months': appointments,
           'horizons': design['horizons'], 'roundtrip_cost_bps_assumed': 50,
           'decision_policy': design['forward_decision'],
           'features': ['r252_known_action_wealth', 'drawdown252', 'vol252'],
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
    reg_path = BASE / 'REGISTRATION.v001.json'
    write_once(reg_path, reg)
    files = ['scripts/phase3_forward.py', 'lab/schema.py', 'lab/evaluate.py',
             'SAMPLE_EXPANSION_PROTOCOL.md', 'research/phase3/design.v001.json',
             'research/phase3/PROTOCOL.lock.v001.json',
             'research/phase3/audit/PRIOR_OPERATIVE_FRAMEWORK.v001.json', str(reg_path.relative_to(ROOT))]
    write_once(BASE / 'REGISTRATION.lock.v001.json',
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
    return {'asset_id': asset['asset_id'], 'prices': prices, 'actions': actions,
            'split_units_verified': not any(a['action_type'] == 'split' for a in actions),
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


def features(bundle, month, anchor):
    rows = [r for r in bundle['prices'] if r['date'][:7] <= month]
    unknown = {'r252_known_action_wealth': None, 'drawdown252': None, 'vol252': None}
    if not bundle['split_units_verified']:
        return {**unknown, 'status': 'UNRESOLVED_SPLIT_UNITS'}
    if not rows or (anchor - dt.date.fromisoformat(rows[-1]['date'])).days > 10:
        return {**unknown, 'status': 'STALE_OR_MISSING_MONTH_SOURCE'}
    if rows[-1]['date'][:7] != month or len(rows) < 253:
        return {**unknown, 'status': 'INSUFFICIENT_COMPLETE_MONTH_HISTORY'}
    dates = {r['date'] for r in rows}
    actions = [a for a in bundle['actions'] if a['date'] in dates]
    chain = historical_wealth(rows, actions)
    wealth = [value for _, value in chain[-253:]]
    log_returns = [math.log(b / a) for a, b in zip(wealth[:-1], wealth[1:])]
    return {'status': 'KNOWN_AT_ACTUAL_CAPTURE', 'last_month_observed_session': rows[-1]['date'],
            'month_session_quality': 'LAST_SOURCE_OBSERVED_NOT_CALENDAR_VERIFIED',
            'r252_known_action_wealth': wealth[-1] / wealth[0] - 1,
            'drawdown252': wealth[-1] / max(wealth) - 1,
            'vol252': statistics.stdev(log_returns) * math.sqrt(252),
            'historical_provider_revision_limit': 'Historical inputs as exposed in now-retained live source, not earlier original vintages'}


def capture(month):
    reg = registration()
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
            record['features'] = features(read(ROOT / source['canonical_path']), month, anchor)
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
                'registration_sha256': sha256(BASE / 'REGISTRATION.lock.v001.json')})
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
                if not bundle['split_units_verified']:
                    outcome = {'status': 'UNRESOLVED_SPLIT_UNITS', 'net_return': None}
                else:
                    outcome = evaluate_path(bundle['prices'], bundle['actions'], decision['cutoff_at'], sessions,
                              bundle['action_coverage'], 'TOTAL_RETURN' if asset['instrument_type'] == 'ETF' else 'PRICE_ONLY',
                              reg['roundtrip_cost_bps_assumed'], 'EXCHANGE_TRADED_ETF' if asset['instrument_type'] == 'ETF' else 'NONTRADEABLE_INDEX_BENCHMARK_ONLY')
                one['horizons'][h] = outcome
        results.append(one)
    bil = next(x for x in results if x['asset_id'] == 'BIL')
    for one in results:
        for h, value in one['horizons'].items():
            cash = bil['horizons'].get(h, {})
            aligned = (one['currency'] == 'USD' and value.get('status') == cash.get('status') == 'REVEALED'
                       and value['entry_date'] == cash['entry_date'] and value['exit_date'] == cash['exit_date'])
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
    asset = {'asset_id': 'TEST_SYNTHETIC', 'market': 'US', 'timezone': 'America/New_York', 'instrument_type': 'ETF'}
    body = json_bytes({'chart': {'error': None, 'result': [{'timestamp': [int(timestamp('2026-10-30T13:30:00+00:00').timestamp())],
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
