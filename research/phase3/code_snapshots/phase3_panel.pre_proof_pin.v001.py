#!/usr/bin/env python3
"""Phase 3 fixed panel, with separately locked past features and future labels.

This implements the registered protocol rather than the failed timing rule.
The administrator reads canonical source files, but compute_features accepts
only cutoff-filtered rows and rejects any post-cutoff observation. This is
logical historical reconstruction, not original-vintage or cognitive blindness.
No source acquisition, fitting, probability forecast, or threshold search occurs.
"""
from __future__ import annotations

import argparse
import bisect
import calendar
import hashlib
import json
import math
import statistics
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lab.schema import (historical_wealth, timestamp, utc_now, validate_actions,
                        validate_records)

BASE = ROOT / "research/phase3"
DESIGN_PATH = BASE / "design.v001.json"
PROTOCOL_LOCK = BASE / "PROTOCOL.lock.v001.json"
REGISTRATION = BASE / "panel.registration.v001.json"
REGISTRATION_LOCK = BASE / "panel.registration.v001.lock.json"
FEATURES = BASE / "features/decision_points.v001.json"
FEATURE_LOCK = BASE / "features/decision_points.v001.SHA.lock.json"
DEEP_INDEX = BASE / "deep/index.v001.json"
DATA = BASE / "data/market"
CREDIT = BASE / "data/credit/credit.records.v001.json"
ACTION_ADMISSION = BASE / "data/ACTION_ADMISSION.v001.json"
VOL_ENDPOINT = BASE / "H-P3-VOL-ENDPOINT-v001.json"
VOL_ENDPOINT_LOCK = BASE / "H-P3-VOL-ENDPOINT-v001.lock.json"
CORE_CODE = ("scripts/phase3_panel.py", "lab/schema.py", "lab/evaluate.py",
             "scripts/phase2_benchmarks.py", "scripts/analyze_cash_and_sell.py")
CREDIT_SERIES = "SLOOS_CI_LARGE_MIDDLE_NET_TIGHTENING"
VALID_CREDIT = {"VERIFIED", "VERIFIED_CONSERVATIVE_SESSION_LAG"}
UNKNOWN_FIELDS = ("valuation", "earnings_revision", "earnings_quality", "rates",
                  "inflation", "credit_spread", "liquidity", "breadth",
                  "capital_cycle", "price_in", "orders", "local_policy")
FIXED_PORTFOLIOS = ("FIXED_50_50_SPY_BIL", "FIXED_60_40_SPY_IEF",
                    "FIXED_70_30_SPY_IEF")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def object_digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def write_once(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2,
                          allow_nan=False) + "\n").encode()
    with path.open("xb") as output:
        output.write(payload)
    return digest(path)


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def protocol():
    lock = read(PROTOCOL_LOCK)
    for name, expected in lock["files"].items():
        if digest(ROOT / name) != expected:
            raise ValueError("frozen protocol changed: " + name)
    design = read(DESIGN_PATH)
    if len(design["assets"]) != 26 or len(design["years"]) != 26 or design["quarters"] != [1, 2, 3, 4]:
        raise ValueError("unexpected v001 selection contract; use a new hypothesis/version")
    if read(VOL_ENDPOINT_LOCK)["sha256"] != digest(VOL_ENDPOINT):
        raise ValueError("registered volatility endpoint explanation changed")
    return design


def input_manifest(design):
    paths = [ROOT / p for p in CORE_CODE]
    paths.extend((VOL_ENDPOINT, VOL_ENDPOINT_LOCK))
    paths.extend(DATA / (a["asset_id"] + ".canonical.json")
                 for a in design["assets"] if (DATA / (a["asset_id"] + ".canonical.json")).exists())
    for asset in design["assets"]:
        canonical = DATA / (asset["asset_id"] + ".canonical.json")
        if canonical.exists():
            meta = read(canonical).get("metadata", {})
            raw = ROOT / meta["raw_path"] if meta.get("raw_path") else None
            if raw is not None and raw.is_file():
                if meta.get("source_sha256") and digest(raw) != meta["source_sha256"]:
                    raise ValueError("canonical/raw source SHA mismatch: " + asset["asset_id"])
                paths.append(raw)
    if ACTION_ADMISSION.exists():
        paths.append(ACTION_ADMISSION)
        for row in read(ACTION_ADMISSION).get("records", []):
            p = (ROOT / row["source_path"]).resolve()
            if ROOT not in p.parents or digest(p) != row["source_sha256"]:
                raise ValueError("action admission primary proof hash mismatch")
            paths.append(p)
    if CREDIT.exists():
        paths.append(CREDIT)
        for row in read(CREDIT).get("records", []):
            if row.get("source_path") and row.get("source_sha256"):
                p = (ROOT / row["source_path"]).resolve()
                if ROOT not in p.parents or digest(p) != row["source_sha256"]:
                    raise ValueError("credit original source hash mismatch")
                paths.append(p)
    # Selection descriptors only, never old predictions or outcome labels.
    paths.extend(sorted((ROOT / "research/replays").glob("*/selection.v001.json")))
    return {relative(p): digest(p) for p in paths}


def register():
    design = protocol()
    if REGISTRATION.exists() or REGISTRATION_LOCK.exists():
        verify_registration()
        return {"status": "EXISTING_REGISTRATION_INTEGRITY_PASS", "sha256": digest(REGISTRATION)}
    body = {
        "study_id": design["study_id"], "registered_at": utc_now(),
        "state": "ENGINE_AND_INPUTS_LOCKED_BEFORE_NEW_LABELS",
        "protocol_sha256": digest(PROTOCOL_LOCK), "design_sha256": digest(DESIGN_PATH),
        "source_and_code_sha256": input_manifest(design),
        "missing_assets": [a["asset_id"] for a in design["assets"]
                           if not (DATA / (a["asset_id"] + ".canonical.json")).exists()],
        "credit_source_state": "PRESENT" if CREDIT.exists() else "DATA_REQUIRED",
        "features_only_before_label_phase": True, "parameter_searches": 0,
        "old_timing_rule_run": False, "old_replays_modified": False,
        "external_trusted_timestamp": False,
        "sample_independence": "Raw grid is not independent experiments; effective N unknown",
        "volatility_reference_definition": "252 prior rolling 252-return sample vol estimates strictly excluding current; requires505 closes; H-P3-VOL-ENDPOINT-v001",
        "source_quality": "RECONSTRUCTED_NOT_ARCHIVED; current vendor correction, survivor, cash-exdate and calendar limitations remain",
    }
    sha = write_once(REGISTRATION, body)
    write_once(REGISTRATION_LOCK, {"registered_at": body["registered_at"],
                                   "registration_sha256": sha,
                                   "source_and_code_sha256": body["source_and_code_sha256"]})
    return {"status": body["state"], "registration_sha256": sha}


def verify_registration():
    design = protocol()
    reg, lock = read(REGISTRATION), read(REGISTRATION_LOCK)
    if digest(REGISTRATION) != lock["registration_sha256"]:
        raise ValueError("registration lock hash mismatch")
    actual = input_manifest(design)
    if reg["source_and_code_sha256"] != actual or lock["source_and_code_sha256"] != actual:
        raise ValueError("registered code/source set changed; append a new version, never overwrite")
    if reg["design_sha256"] != digest(DESIGN_PATH) or reg["protocol_sha256"] != digest(PROTOCOL_LOCK):
        raise ValueError("protocol/registration mismatch")
    return design, reg


def basis(asset, bundle):
    if asset["instrument_type"] == "ETF":
        return "TOTAL_RETURN"
    if asset["asset_id"] == "DAX":
        return "INDEX_PERFORMANCE_EMBEDDED_DIVIDENDS"
    return bundle.get("metadata", {}).get("return_basis", "PRICE_ONLY")


def ordinary_qqq_admission(bundle):
    """Administrator-only unit proof; never a historical news feature."""
    if bundle.get("asset_id") != "QQQ" or not ACTION_ADMISSION.exists():
        return False
    matches = [r for r in read(ACTION_ADMISSION).get("records", []) if r.get("asset_id") == "QQQ"]
    if len(matches) != 1:
        return False
    row = matches[0]
    path = DATA / "QQQ.canonical.json"
    proof = (ROOT / row["source_path"]).resolve()
    if ROOT not in proof.parents or digest(proof) != row["source_sha256"] or digest(path) != row["canonical_sha256"]:
        raise ValueError("QQQ ordinary split admission proof changed")
    splits = [a for a in bundle.get("actions", []) if a["action_type"] == "split"]
    return (row.get("eligibility_override") == "ALLOW_ORDINARY_SPLIT_RECONSTRUCTED_UNITS_AND_PROVIDER_CONDITIONAL_TR"
            and len(splits) == 1 and splits[0]["date"] == row["trading_effective_date"]
            and float(splits[0]["ratio"]) == float(row["ratio"]) == 2.0)


def quarantine_reason(asset, bundle):
    if asset["asset_id"] == "XLF":
        return "XLF_IN_KIND_SPINOFF_UNRESOLVED_ALL_PERIODS_QUARANTINED"
    meta = bundle.get("metadata", {})
    if bundle.get("asset_id") != asset["asset_id"]:
        return "SOURCE_ASSET_MISMATCH"
    if meta.get("price_basis") not in {"UNADJUSTED", "AS_REPORTED_OHLC_NO_ADJCLOSE"}:
        return "UNRESOLVED_PRICE_UNITS"
    if meta.get("price_basis") == "AS_REPORTED_OHLC_NO_ADJCLOSE" and not meta.get("no_splits_in_analysis_interval_confirmed"):
        return "AS_REPORTED_PRICE_WITHOUT_NO_SPLIT_AUDIT"
    if asset["instrument_type"] == "ETF":
        admitted = ordinary_qqq_admission(bundle)
        if bundle.get("action_coverage") != "COMPLETE" or not (meta.get("total_return_eligible") or admitted):
            return "UNRESOLVED_CORPORATE_ACTION_COVERAGE"
        if meta.get("split_action_validation_required") and not admitted:
            return "UNVERIFIED_SPLIT_OR_SPECIAL_ACTION"
    if meta.get("data_eligibility", "").startswith("DATA_REQUIRED"):
        return "ADMINISTRATIVE_SOURCE_QUARANTINE:" + meta["data_eligibility"]
    try:
        validate_records(bundle["prices"], require_prices=True)
        validate_actions(bundle.get("actions", []))
        if len({r["date"] for r in bundle["prices"]}) != len(bundle["prices"]):
            raise ValueError("duplicate price date")
        for row in bundle["prices"] + bundle.get("actions", []):
            if row.get("asset_id") != asset["asset_id"]:
                raise ValueError("record asset mismatch")
    except (KeyError, ValueError, TypeError) as exc:
        return "SOURCE_CONTRACT_FAILED:" + str(exc)
    return None


def load_sources(design):
    sources = {}
    for asset in design["assets"]:
        path = DATA / (asset["asset_id"] + ".canonical.json")
        if not path.exists():
            continue
        bundle = read(path)
        reason = quarantine_reason(asset, bundle)
        sources[asset["asset_id"]] = {"bundle": bundle, "path": path,
                                     "sha256": digest(path), "quarantine_reason": reason}
    return sources


def credit_rows():
    if not CREDIT.exists():
        return []
    body = read(CREDIT)
    candidates = body.get("records", []) if isinstance(body, dict) else body
    accepted = []
    for row in candidates:
        value = row.get("value")
        if row.get("series_id") != CREDIT_SERIES or row.get("pit_status") not in VALID_CREDIT:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            continue
        if row.get("approximate") or row.get("value_status") in {"APPROXIMATE", "POINT_IN_TIME_UNCERTAIN"}:
            continue
        if not all(row.get(k) for k in ("record_id", "published_at", "available_at", "source_sha256", "source_id", "availability_evidence")):
            continue
        try:
            if timestamp(row["published_at"]) > timestamp(row["available_at"]):
                continue
        except (TypeError, ValueError):
            continue
        accepted.append(row)
    if len({r["record_id"] for r in accepted}) != len(accepted):
        raise ValueError("duplicate accepted credit record_id")
    return sorted(accepted, key=lambda r: (timestamp(r["available_at"]), r["record_id"]))


def credit_at(rows, cutoff_at, market):
    out = {"value": None, "group": None, "status": "UNKNOWN", "record_id": None,
           "published_at": None, "available_at": None, "age_days": None,
           "source_sha256": None}
    if market != "US":
        out["status"] = "NOT_APPLICABLE_LOCAL_CREDIT"
        return out
    known = [r for r in rows if timestamp(r["available_at"]) <= timestamp(cutoff_at)]
    if not known:
        return out
    row = known[-1]
    age = (timestamp(cutoff_at) - timestamp(row["published_at"])).total_seconds() / 86400
    if age < 0 or age > 180:
        out.update(status="STALE_RELEASE_EXCLUDED", age_days=age)
        return out
    out.update(value=float(row["value"]), group="TIGHTENING" if row["value"] > 0 else "NOT_TIGHTENING",
               status="KNOWN_AT_T", age_days=age)
    for key in ("record_id", "published_at", "available_at", "source_sha256", "source_id",
                "source_path", "availability_evidence", "pit_status"):
        if key in row:
            out[key] = row[key]
    return out


def compute_features(prices, actions, cutoff_at, return_basis):
    """Feature module takes only past records; future input raises, never leaks."""
    validate_records(prices, cutoff_at, require_prices=True)
    validate_actions(actions, cutoff_at)
    used_actions = actions if return_basis == "TOTAL_RETURN" else [a for a in actions if a["action_type"] == "split"]
    chain = historical_wealth(prices, used_actions)
    wealth = [w for _, w in chain]
    result = {"r63": None, "r252": None, "vol252": None, "drawdown252": None,
              "vol252_prior252_median": None, "trend_group": None,
              "drawdown_group": None, "vol_group": None,
              "volatility_reference_estimates": 0, "relative_vol_status": "INSUFFICIENT_HISTORY"}
    if len(wealth) >= 64:
        result["r63"] = wealth[-1] / wealth[-64] - 1
    if len(wealth) < 253:
        return result
    daily = [wealth[i] / wealth[i - 1] - 1 for i in range(1, len(wealth))]
    r252 = wealth[-1] / wealth[-253] - 1
    vol = statistics.stdev(daily[-252:]) * math.sqrt(252)
    dd = wealth[-1] / max(wealth[-252:]) - 1
    result.update(r252=r252, vol252=vol, drawdown252=dd,
                  trend_group="POSITIVE" if r252 > 0 else "NONPOSITIVE",
                  drawdown_group="LARGE_DRAWDOWN" if dd <= -.20 else "OTHER",
                  relative_vol_status="INSUFFICIENT_252_PRIOR_ESTIMATES")
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
                      vol_group="HIGH" if vol > ref else "NOT_HIGH",
                      volatility_reference_estimates=252, relative_vol_status="AVAILABLE_252_PRIOR_ESTIMATES_EXCLUDING_CURRENT")
    return result


def prior_exposure():
    used = set()
    for path in sorted((ROOT / "research/replays").glob("*/selection.v001.json")):
        body = read(path)
        for row in body.get("episodes", []):
            if not row.get("asset_id") or not row.get("cutoff_at"):
                continue
            d = timestamp(row["cutoff_at"])
            used.add((row["asset_id"], d.year, (d.month - 1) // 3 + 1))
    return used


def quarter_end(year, quarter):
    month = quarter * 3
    return date(year, month, calendar.monthrange(year, month)[1])


def local_cutoff(session_date, tz):
    return datetime.combine(date.fromisoformat(session_date) + timedelta(days=1), time(0),
                            tzinfo=ZoneInfo(tz)).astimezone(timezone.utc).isoformat()


def blank_features():
    return {"r63": None, "r252": None, "vol252": None, "drawdown252": None,
            "vol252_prior252_median": None, "trend_group": None,
            "drawdown_group": None, "vol_group": None,
            "volatility_reference_estimates": 0, "relative_vol_status": "INSUFFICIENT_HISTORY"}


def make_point(asset, year, quarter, source, credits, used):
    end = quarter_end(year, quarter)
    start = date(year, (quarter - 1) * 3 + 1, 1)
    row = {"point_id": f"P3-{asset['asset_id']}-{year}Q{quarter}",
           **asset, "year": year, "quarter": quarter, "calendar_quarter": f"{year}Q{quarter}",
           "quarter_end_date": end.isoformat(), "decision_session_date": None,
           "cutoff_at": local_cutoff(end.isoformat(), asset["timezone"]),
           "status": "NO_SOURCE", "feature_eligible": False,
           "information_set": "KNOWN_AT_T", "features": blank_features(),
           "source": None, "evidence": {"known_price_rows": 0},
           "return_basis": None, "unknowns": {k: None for k in UNKNOWN_FIELDS},
           "prior_exposure": "ALREADY_USED_ASSET_CALENDAR_QUARTER" if (asset["asset_id"], year, quarter) in used else "NOT_ALREADY_USED_ASSET_CALENDAR_QUARTER",
           "validation_role": "COMPUTATIONAL_LATER_LABEL_HOLDOUT_WITH_PRIOR_PATH_EXPOSURE" if year >= 2024 else "DEVELOPMENT_CONTEXT" if year >= 2016 else "PREREGISTERED_CROSS_TIME_RECONSTRUCTION",
           "tradability": "EXCHANGE_TRADED_ETF" if asset["instrument_type"] == "ETF" else "NONTRADEABLE_INDEX",
           "price_in_status": "UNKNOWN_NOT_INFERRED_FROM_PRICE_TREND"}
    if source is None:
        row["credit"] = credit_at(credits, row["cutoff_at"], asset["market"])
        return row
    bundle = source["bundle"]
    row["source"] = {"canonical_path": relative(source["path"]), "canonical_sha256": source["sha256"],
                     "price_source_sha256": bundle.get("metadata", {}).get("source_sha256"),
                     "source_id": bundle.get("metadata", {}).get("source_id"),
                     "vintage_status": "RECONSTRUCTED_NOT_ARCHIVED",
                     "return_quality": "CONDITIONAL_PROVIDER_REPORTED_EXDATE_REINVESTMENT" if asset["instrument_type"] == "ETF" else "NATIVE_INDEX_LEVEL_NOT_TRADABLE",
                     "provenance_hashes_are_not_predictive_features": True}
    row["return_basis"] = basis(asset, bundle)
    qrows = [p for p in bundle.get("prices", []) if start.isoformat() <= p.get("date", "") <= end.isoformat()]
    if qrows:
        last = max(qrows, key=lambda p: p["date"])
        row.update(decision_session_date=last["date"], cutoff_at=local_cutoff(last["date"], asset["timezone"]))
    row["credit"] = credit_at(credits, row["cutoff_at"], asset["market"])
    if source["quarantine_reason"]:
        row.update(status="EXCLUDED_INSTRUMENT", exclusion_reason=source["quarantine_reason"])
        return row
    if not qrows:
        row["missing_reason"] = "NO_OBSERVED_COMPLETE_SESSION_IN_FIXED_QUARTER"
        return row
    cut = timestamp(row["cutoff_at"])
    known_prices = sorted([p for p in bundle["prices"] if timestamp(p["available_at"]) <= cut], key=lambda p: p["date"])
    known_actions = [a for a in bundle.get("actions", []) if timestamp(a["available_at"]) <= cut]
    row["features"] = compute_features(known_prices, known_actions, row["cutoff_at"], row["return_basis"])
    row["feature_eligible"] = len(known_prices) >= 253
    row["status"] = "FEATURES_AVAILABLE" if row["feature_eligible"] else "INSUFFICIENT_HISTORY"
    evidence = {"known_price_rows": len(known_prices),
                "known_price_record_ids_sha256": object_digest([p["record_id"] for p in known_prices]),
                "known_action_record_ids": [a["record_id"] for a in known_actions],
                "known_actions_sha256": object_digest(known_actions),
                "max_known_available_at": max(p["available_at"] for p in known_prices),
                "feature_formula": "r252=W[-1]/W[-253]-1; vol252=sample_stdev(last252 daily simple wealth returns)*sqrt252; drawdown252=W[-1]/max(W[-252:])-1; volreference=median(252 prior rolling252 estimates strictly excluding current); requires505 prices (H-P3-VOL-ENDPOINT-v001)",
                "selection_clock": "last complete observed quarter session; following local midnight, normal-session historical calendar not exhaustively verified"}
    for lag, name in ((0, "last_price_record"), (63, "r63_start_record"), (252, "r252_start_record"), (504, "vol_reference_start_record")):
        evidence[name] = {k: known_prices[-1 - lag][k] for k in ("record_id", "date", "close", "available_at", "source_sha256")} if len(known_prices) > lag else None
    row["evidence"] = evidence
    return row


def build_features():
    design, reg = verify_registration()
    if FEATURES.exists() or FEATURE_LOCK.exists():
        verify_features()
        return {"status": "EXISTING_ALL_FEATURES_LOCK_INTEGRITY_PASS", "sha256": digest(FEATURES)}
    sources = load_sources(design)
    credits, used = credit_rows(), prior_exposure()
    points = [make_point(asset, year, quarter, sources.get(asset["asset_id"]), credits, used)
              for year in design["years"] for quarter in design["quarters"] for asset in design["assets"]]
    if len(points) != 2704 or len({p["point_id"] for p in points}) != 2704:
        raise ValueError("fixed selection grid changed")
    selected = [p for p in points if (p["asset_id"] in design["deep_industry_assets"] and p["quarter"] == design["deep_industry_quarter"]) or (p["asset_id"] in design["deep_broad_assets"] and p["quarter"] == design["deep_broad_quarter"] and p["year"] % 2 == 0)]
    if len(selected) != 273:
        raise ValueError("deep index contract changed")
    deep = {"study_id": design["study_id"], "selection": "FIXED_BEFORE_OUTCOMES_NOT_EVENT_OR_WINNER_SELECTED",
            "RAW_OBSERVATIONS": len(selected), "EFFECTIVE_SAMPLE_ASSESSMENT": "273 grid rows, independent N unknown; same-quarter/global overlap and sector correlation",
            "dossier_quality_not_assumed": True,
            "points": [{k: p[k] for k in ("point_id", "asset_id", "market", "industry", "year", "quarter", "cutoff_at", "status", "feature_eligible")} for p in selected]}
    write_once(DEEP_INDEX, deep)
    counts = {key: sum(p["status"] == key for p in points)
              for key in ("FEATURES_AVAILABLE", "INSUFFICIENT_HISTORY", "NO_SOURCE", "EXCLUDED_INSTRUMENT")}
    body = {"study_id": design["study_id"], "created_at": utc_now(),
            "information_set": "KNOWN_AT_T", "stage": "ALL_FEATURES_LOCKED_BEFORE_NEW_LABELS",
            "registration_sha256": digest(REGISTRATION), "protocol_sha256": digest(PROTOCOL_LOCK),
            "RAW_OBSERVATIONS": len(points), "EFFECTIVE_SAMPLE_ASSESSMENT": {"N_effective": None, "reason": "same date, country/industry correlation, overlapping forward horizons and global regimes; raw observations are not independent bets"},
            "status_counts": counts, "original_credit_records_available": len(credits),
            "no_prediction_or_trading_rule": True, "points": points}
    sha = write_once(FEATURES, body)
    write_once(FEATURE_LOCK, {"status": "ALL_2704_STAGE_A_FEATURES_LOCKED", "locked_at": utc_now(),
                             "feature_sha256": sha, "feature_count": 2704,
                             "deep_index_sha256": digest(DEEP_INDEX),
                             "registration_sha256": digest(REGISTRATION),
                             "source_and_code_sha256": reg["source_and_code_sha256"],
                             "external_trusted_timestamp": False,
                             "separation": "LOGICAL_RECONSTRUCTION_ONLY_NO_COGNITIVE_BLINDNESS"})
    return {"status": "ALL_2704_STAGE_A_FEATURES_LOCKED", "feature_sha256": sha, "status_counts": counts, "deep_rows": 273}


def verify_features():
    design, reg = verify_registration()
    body, lock = read(FEATURES), read(FEATURE_LOCK)
    if lock["feature_sha256"] != digest(FEATURES) or lock["deep_index_sha256"] != digest(DEEP_INDEX):
        raise ValueError("frozen features/deep index changed")
    if lock["registration_sha256"] != digest(REGISTRATION) or lock["source_and_code_sha256"] != reg["source_and_code_sha256"]:
        raise ValueError("feature registration mismatch")
    if len(body["points"]) != 2704 or lock["feature_count"] != 2704:
        raise ValueError("all fixed grid features must be locked before any labels")
    return design, body


def matched(label, benchmark):
    for value in (label, benchmark):
        h = value.get("execution_session_dates_sha256")
        n = value.get("sessions_held")
        if not isinstance(h, str) or len(h) != 64 or any(c not in "0123456789abcdef" for c in h):
            return False
        if isinstance(n, bool) or not isinstance(n, int) or n < 1:
            return False
        if not value.get("entry_date") or not value.get("exit_date"):
            return False
    return label.get("status") == "REVEALED" and benchmark.get("status") == "REVEALED" and all(label.get(k) == benchmark.get(k) for k in ("entry_date", "exit_date", "sessions_held", "execution_session_dates_sha256"))


def benchmark_pair(label, benchmark, benchmark_id):
    out = {"benchmark_id": benchmark_id, "status": "MISSING_SAME_EXECUTION_BENCHMARK", "net_return": None,
           "difference_net_return": None, "entry_date": None, "exit_date": None, "max_drawdown": None}
    if not benchmark_id:
        out["status"] = "UNKNOWN_LOCAL_CASH_FX_OR_TRADEABLE_BENCHMARK"
    elif matched(label, benchmark):
        out.update(status="SAME_EXECUTION", net_return=benchmark["net_return"],
                   difference_net_return=label["net_return"] - benchmark["net_return"],
                   entry_date=benchmark["entry_date"], exit_date=benchmark["exit_date"],
                   max_drawdown=benchmark["max_drawdown"])
    return out


def compact_label(label):
    result = dict(label)
    ids = result.pop("price_evidence_record_ids", [])
    result["price_evidence_record_count"] = len(ids)
    result["price_evidence_record_ids_sha256"] = object_digest(ids)
    result["first_price_evidence_record_id"] = ids[0] if ids else None
    result["last_price_evidence_record_id"] = ids[-1] if ids else None
    return result


def validate_development_analysis_lock(path):
    path = Path(path).resolve()
    proof = read(path)
    if proof.get("status", proof.get("state")) != "DEVELOPMENT_ANALYSIS_LOCKED_BEFORE_HOLDOUT":
        raise ValueError("holdout requires an explicit completed-development-analysis lock")
    if proof.get("feature_sha256") != digest(FEATURES):
        raise ValueError("development analysis lock is not tied to frozen feature panel")
    if not proof.get("files"):
        raise ValueError("development result hashes missing")
    timestamp(proof["locked_at"])
    for name, expected in proof["files"].items():
        p = (ROOT / name).resolve()
        if ROOT not in p.parents or not p.is_file() or digest(p) != expected:
            raise ValueError("development analysis result hash mismatch: " + name)
    development = BASE / "labels/development.v001.json"
    dlock = BASE / "labels/development.v001.SHA.lock.json"
    if not development.exists() or not dlock.exists() or read(dlock)["label_sha256"] != digest(development):
        raise ValueError("development label lock missing or changed")
    return {"path": relative(path), "sha256": digest(path), "locked_at": proof["locked_at"]}


def reveal_labels(partition, development_lock=None):
    design, feature_body = verify_features()
    proof = validate_development_analysis_lock(development_lock) if partition == "holdout" and development_lock else None
    if partition == "holdout" and proof is None:
        raise ValueError("holdout may run only after development analysis is locked, via --development-lock")
    output = BASE / "labels" / (partition + ".v001.json")
    lock_path = BASE / "labels" / (partition + ".v001.SHA.lock.json")
    if output.exists() or lock_path.exists():
        if read(lock_path)["label_sha256"] != digest(output) or read(lock_path)["feature_sha256"] != digest(FEATURES):
            raise ValueError("existing label lock hash mismatch")
        return {"status": "EXISTING_LABEL_INTEGRITY_PASS", "partition": partition, "sha256": digest(output)}
    # The only imports of outcome evaluators are below the verified all-A lock.
    from lab.evaluate import evaluate_path
    from scripts.phase2_benchmarks import evaluate_cutoff, single_asset_path
    sources = load_sources(design)
    assets = {a["asset_id"]: a for a in design["assets"]}
    selected = [p for p in feature_body["points"] if (p["year"] > design["development_end_year"]) == (partition == "holdout")]
    market_cache, allocation_cache, comparable_asset_cache = {}, {}, {}
    prepared = {}
    for asset_id, source in sources.items():
        if source["quarantine_reason"]:
            continue
        bundle = source["bundle"]
        prices = sorted(bundle["prices"], key=lambda r: timestamp(r["session_open_at"]))
        prepared[asset_id] = (prices, [timestamp(r["session_open_at"]) for r in prices], bundle)

    def market_label(asset_id, cutoff_at, n):
        key = (asset_id, cutoff_at, n)
        if key in market_cache:
            return market_cache[key]
        if asset_id not in prepared:
            return {"status": "NO_SOURCE", "net_return": None}
        prices, opens, bundle = prepared[asset_id]
        start = bisect.bisect_right(opens, timestamp(cutoff_at))
        chosen = prices[start:start + n + 1]
        actions = bundle.get("actions", [])
        if chosen:
            actions = [a for a in actions if chosen[0]["date"] < a["date"] <= chosen[-1]["date"]]
        asset = assets[asset_id]
        value = evaluate_path(chosen, actions, cutoff_at, n, bundle.get("action_coverage", "UNKNOWN"),
                              basis(asset, bundle), design["cost_roundtrip_bps"],
                              "EXCHANGE_TRADED_ETF" if asset["instrument_type"] == "ETF" else "NONTRADEABLE_INDEX")
        value["execution_session_dates_sha256"] = object_digest([r["date"] for r in chosen]) if value["status"] == "REVEALED" else None
        market_cache[key] = value
        return value

    fixed_sources = {a: sources[a]["bundle"] for a in ("SPY", "IEF", "BIL")
                     if a in sources and not sources[a]["quarantine_reason"]}
    fixed_dates = sorted(set.intersection(*(set(r["date"] for r in b["prices"]) for b in fixed_sources.values()))) if len(fixed_sources) == 3 else []
    spy_opens = {r["date"]: timestamp(r["session_open_at"]) for r in fixed_sources.get("SPY", {}).get("prices", [])}
    fixed_opens = [spy_opens[d] for d in fixed_dates]

    def allocations(asset_id, cutoff_at, n, label):
        result = {p: {"status": "MISSING_SAME_EXECUTION_BENCHMARK", "net_return": None,
                      "net_max_drawdown": None, "difference_net_return": None,
                      "asset_comparable_net_return": None, "asset_comparable_mdd": None} for p in FIXED_PORTFOLIOS}
        if label.get("status") != "REVEALED" or len(fixed_sources) != 3:
            return result
        key = (cutoff_at, n)
        if key not in allocation_cache:
            allocation_cache[key] = evaluate_cutoff(fixed_sources, cutoff_at, n, 25.0)
        fixed = allocation_cache[key]
        if fixed.get("entry_date") != label.get("entry_date") or fixed.get("exit_date") != label.get("exit_date"):
            return result
        first = bisect.bisect_right(fixed_opens, timestamp(cutoff_at))
        if object_digest(fixed_dates[first:first + n + 1]) != label.get("execution_session_dates_sha256"):
            return result
        asset_key = (asset_id, cutoff_at, n)
        if asset_key not in comparable_asset_cache:
            prices, opens, bundle = prepared[asset_id]
            asset_first = bisect.bisect_right(opens, timestamp(cutoff_at))
            held = prices[asset_first:asset_first + n + 1]
            if object_digest([r["date"] for r in held]) != label["execution_session_dates_sha256"]:
                raise ValueError("same-helper asset comparison session mismatch")
            comparable_asset_cache[asset_key] = single_asset_path(held, bundle.get("actions", []), 25.0)
        comparable = comparable_asset_cache[asset_key]
        for portfolio in FIXED_PORTFOLIOS:
            value = fixed.get("portfolios", {}).get(portfolio)
            if value is not None:
                result[portfolio] = {"status": "SAME_EXECUTION", "net_return": value["net_return"],
                                     "net_max_drawdown": value["net_max_drawdown"],
                                     "difference_net_return": comparable["net_return"] - value["net_return"],
                                     "asset_comparable_net_return": comparable["net_return"],
                                     "asset_comparable_mdd": comparable["net_max_drawdown"],
                                     "gross_to_comparable_net_return_difference": comparable["net_return"] - label["gross_return"],
                                     "primary_net_to_comparable_net_return_difference": comparable["net_return"] - label["net_return"],
                                     "gross_to_comparable_mdd_difference": comparable["net_max_drawdown"] - label["max_drawdown"],
                                     "entry_date": fixed["entry_date"], "exit_date": fixed["exit_date"],
                                     "method": "fixed initial weights, no rebalance, exdate cash reinvestment, 25bp per order leg",
                                     "difference_definition": "same-helper asset_comparable_net_return minus fixed benchmark net_return; excludes liquidation cost on terminal dividend receivable; main frozen-evaluator label unchanged",
                                     "mdd_comparison_definition": "asset_comparable_mdd and benchmark net_max_drawdown both same-helper after-cost NAV; main max_drawdown is gross and must not be directly subtracted"}
        return result

    rows = []
    for point in selected:
        horizons = {}
        eligible_source = point["status"] not in {"NO_SOURCE", "EXCLUDED_INSTRUMENT"}
        for horizon, n in design["horizons"].items():
            value = market_label(point["asset_id"], point["cutoff_at"], n) if eligible_source else {"status": point["status"], "net_return": None, "gross_return": None, "max_drawdown": None}
            benchmark_id = None
            if point["market"] == "US":
                benchmark_id = "SPY" if point["industry"] in {"Technology", "Semiconductor", "Financials_Quarantined", "Financials_Banks", "Industrials", "Consumer", "Healthcare", "Energy_Resources", "Utilities", "Growth"} else "BIL" if point["asset_id"] != "SPY" else "SPY"
            benchmark = market_label(benchmark_id, point["cutoff_at"], n) if benchmark_id else {}
            value = compact_label(value)
            value["benchmark"] = benchmark_pair(value, benchmark, benchmark_id)
            value["fixed_allocation_benchmarks"] = allocations(point["asset_id"], point["cutoff_at"], n, value) if point["market"] == "US" else {}
            horizons[horizon] = value
        rows.append({k: point[k] for k in ("point_id", "asset_id", "market", "industry", "year", "quarter", "cutoff_at", "feature_eligible")} | {"horizons": horizons})
    count = {h: sum(r["horizons"][h]["status"] == "REVEALED" for r in rows) for h in design["horizons"]}
    body = {"study_id": design["study_id"], "partition": partition, "revealed_at": utc_now(),
            "information_set": "KNOWN_ONLY_AFTER_T", "feature_sha256": digest(FEATURES),
            "registration_sha256": digest(REGISTRATION), "development_analysis_lock": proof,
            "RAW_OBSERVATIONS": len(rows), "EFFECTIVE_SAMPLE_ASSESSMENT": "Not independent: common quarters, industries/markets, global regimes, overlapping returns; effective N unknown",
            "mature_label_counts": count, "attribution": "OUTCOME_LABEL_ONLY_NO_CAUSAL_STORY_INFERRED",
            "points": rows}
    sha = write_once(output, body)
    write_once(lock_path, {"status": "FUTURE_LABELS_REVEALED_AFTER_FEATURE_LOCK", "locked_at": utc_now(),
                           "partition": partition, "label_sha256": sha, "feature_sha256": digest(FEATURES),
                           "registration_sha256": digest(REGISTRATION), "development_analysis_lock": proof})
    return {"status": "FUTURE_LABELS_REVEALED_AFTER_FEATURE_LOCK", "partition": partition,
            "raw_points": len(rows), "mature_label_counts": count, "sha256": sha}


def pct(value):
    return "UNKNOWN" if value is None else f"{value * 100:.2f}%"


def render_dossiers():
    _, feature_body = verify_features()
    feature_map = {p["point_id"]: p for p in feature_body["points"]}
    labels = {}
    label_hashes = {}
    for partition in ("development", "holdout"):
        path = BASE / "labels" / (partition + ".v001.json")
        if path.exists():
            lock = read(path.with_name(partition + ".v001.SHA.lock.json"))
            if lock["label_sha256"] != digest(path) or lock["feature_sha256"] != digest(FEATURES):
                raise ValueError("dossier label lock mismatch")
            labels.update({p["point_id"]: p for p in read(path)["points"]})
            label_hashes[partition] = digest(path)
    deep = read(DEEP_INDEX)
    index = []
    for selected in deep["points"]:
        p = feature_map[selected["point_id"]]
        label = labels.get(p["point_id"])
        quality = "MISSING_OR_EXCLUDED_HISTORY" if not p["feature_eligible"] else "ORIGINAL_CREDIT_CONTEXT_PLUS_RECONSTRUCTED_PRICE_FUNDAMENTALS_MISSING" if p["credit"]["status"] == "KNOWN_AT_T" else "RECONSTRUCTED_PRICE_ONLY_FUNDAMENTALS_MISSING"
        lines = [f"# {p['point_id']}", "", "RAW OBSERVATIONS: 1 fixed selected dossier. EFFECTIVE SAMPLE ASSESSMENT: independent N unknown; shared calendar/global/industry effects and overlap.", "",
                 f"资产 {p['asset_id']}；市场 {p['market']}；行业 {p['industry']}；质量 {quality}。", "",
                 "## KNOWN_AT_T — 原冻结特征", "", f"Cutoff `{p['cutoff_at']}`；状态 `{p['status']}`；既有暴露 `{p['prior_exposure']}`。",
                 "", f"r252 {pct(p['features']['r252'])}；r63（仅描述）{pct(p['features']['r63'])}；252peak drawdown {pct(p['features']['drawdown252'])}；vol252 {pct(p['features']['vol252'])}。",
                 "", f"信用状态 `{p['credit']['status']}`；值 {p['credit']['value']}；原发布日期 {p['credit']['published_at']}；可用时间 {p['credit']['available_at']}；记录 {p['credit']['record_id']}。",
                 "", "正面证据：已知上涨趋势/非大跌仅是价格观察，若信号不成立则无此证据。没有虚构基本面支持。",
                 "", "反面证据：已知负趋势/大跌仅是价格观察，不能据此诊断资产负债表危机。估值和盈利缺失是限制而非反向经济事实。",
                 "", "未知：Valuation、Earnings Revision、ROIC、FCF、订单、资本周期、市场隐含预期。过去上涨不证明估值昂贵。",
                 "", "Kill / invalidation: source units, corporate action or publication evidence disproved ⇒ invalidate measurement; signal/distribution instability ⇒ reject candidate association. No dynamic trading thesis was declared.",
                 "", f"已知证据 `{json.dumps(p['evidence'], ensure_ascii=False, sort_keys=True)}`。",
                 "", f"来源与SHA `{json.dumps(p['source'], ensure_ascii=False, sort_keys=True)}`。",
                 "", f"原A文件SHA `{digest(FEATURES)}`；信用sourceSHA `{p['credit']['source_sha256']}`。",
                 "", "## KNOWN_ONLY_AFTER_T — outcome labels", "", "|Horizon|Status|Net|MDD|MAE|MFE|Same-execution benchmark difference|", "|---|---|---|---|---|---|---|"]
        if label:
            for h, r in label["horizons"].items():
                lines.append(f"|{h}|{r['status']}|{pct(r.get('net_return'))}|{pct(r.get('max_drawdown'))}|{pct(r.get('max_adverse_excursion'))}|{pct(r.get('max_favorable_excursion'))}|{pct(r.get('benchmark',{}).get('difference_net_return'))}|")
        else:
            lines.append("|all six|LABEL_PARTITION_NOT_REVEALED|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|")
        lines += ["", "经济机制：UNRESOLVED。原信用上下文说明贷款供给调查方向，价格结果不能证明因果或盈利渠道。该dossier不等于经济机制已识别的高质量episode。", "",
                  "可用的反例必须由全样本同信号未涨、无信号上涨及跨行业/市场分布自动列举；不因本案例结果改写A。", ""]
        target = BASE / "deep/dossiers" / (p["point_id"] + ".v001.md")
        payload = "\n".join(lines).encode()
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.read_bytes() != payload:
                raise ValueError("existing dossier changed; reveal all intended partitions first or append new version")
        else:
            with target.open("xb") as out:
                out.write(payload)
        index.append({"point_id": p["point_id"], "quality": quality, "path": relative(target), "sha256": digest(target),
                      "labels_available": label is not None, "credit_original_context": p["credit"]["status"] == "KNOWN_AT_T"})
    manifest = BASE / "deep/dossiers.manifest.v001.json"
    body = {"created_at": utc_now(), "RAW_OBSERVATIONS": len(index),
            "EFFECTIVE_SAMPLE_ASSESSMENT": "Independent N unknown; text count is not identified mechanisms",
            "feature_sha256": digest(FEATURES), "label_sha256": label_hashes,
            "mechanism_identified_count": 0, "dossiers": index}
    if manifest.exists():
        raise ValueError("dossier manifest already exists; do not rewrite")
    write_once(manifest, body)
    return {"status": "FIXED_DEEP_DOSSIERS_SAVED", "dossiers": len(index), "mechanisms_identified": 0}


def synthetic_self_test():
    """Engineering fixtures only; no real historical outcomes opened."""
    cutoff = "2020-12-31T23:59:59+00:00"
    prices = []
    for i in range(505):
        day = date(2018, 1, 1) + timedelta(days=i)
        close = 100.0 if i < 252 else 50.0
        prices.append({"record_id": f"TEST:{i}", "asset_id": "TEST", "date": day.isoformat(),
                       "session_open_at": day.isoformat() + "T09:00:00+00:00",
                       "session_close_at": day.isoformat() + "T16:00:00+00:00",
                       "available_at": (day + timedelta(days=1)).isoformat() + "T00:00:00+00:00",
                       "open": close, "high": close, "low": close, "close": close,
                       "source_id": "SYNTHETIC", "source_sha256": "synthetic-not-market-data",
                       "pit_status": "KNOWN_MARKET_OBSERVATION_RECONSTRUCTED"})
    split = {"record_id": "TEST:SPLIT", "date": prices[252]["date"], "available_at": prices[252]["available_at"],
             "action_type": "split", "ratio": 2.0, "source_id": "SYNTHETIC",
             "source_sha256": "synthetic-not-market-data", "pit_status": "KNOWN_CORPORATE_ACTION_RECONSTRUCTED"}
    feature = compute_features(prices, [split], cutoff, "TOTAL_RETURN")
    assert abs(feature["r252"]) < 1e-12 and abs(feature["vol252"]) < 1e-12
    assert feature["volatility_reference_estimates"] == 252 and feature["drawdown252"] == 0
    late = dict(prices[-1], record_id="TEST:FUTURE", available_at="2021-01-01T00:00:00+00:00")
    try:
        compute_features(prices + [late], [split], cutoff, "TOTAL_RETURN")
    except ValueError as exc:
        assert "POST_CUTOFF" in str(exc)
    else:
        raise AssertionError("future OHLC accepted")
    label = {"status": "REVEALED", "entry_date": "2020-01-02", "exit_date": "2021-01-02", "sessions_held": 252, "net_return": .1, "max_drawdown": -.1,
             "execution_session_dates_sha256": object_digest(["SYNTHETIC_SAME_HELD_SESSION_SEQUENCE"])}
    other = dict(label, entry_date="2020-01-03")
    assert benchmark_pair(label, other, "SPY")["difference_net_return"] is None
    assert benchmark_pair(label, label, "SPY")["difference_net_return"] == 0
    assert benchmark_pair(label, dict(label, execution_session_dates_sha256=None), "SPY")["difference_net_return"] is None
    assert benchmark_pair(label, dict(label, execution_session_dates_sha256=object_digest(["SYNTHETIC_DIFFERENT_INTERNAL_SESSION_SEQUENCE"])), "SPY")["difference_net_return"] is None
    assert compute_features(prices[:504], [split], cutoff, "TOTAL_RETURN")["vol_group"] is None
    # A source published after cutoff cannot enter even if its quarter was earlier.
    future_credit = [{"record_id": "TEST:CREDIT", "published_at": "2021-01-01T00:00:00+00:00",
                      "available_at": "2021-01-02T00:00:00+00:00", "value": 10}]
    assert credit_at(future_credit, cutoff, "US")["value"] is None
    assert credit_at(future_credit, cutoff, "HK")["status"] == "NOT_APPLICABLE_LOCAL_CREDIT"
    return {"status": "SYNTHETIC_ENGINEERING_ONLY_PASS", "checks": ["cutoff rejection", "split-neutral wealth and volatility", "same-execution benchmark rejection", "credit publication rejection and no overseas transplant"], "real_market_labels_read": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("self-test", "register", "features", "labels", "dossiers", "verify"))
    parser.add_argument("--partition", choices=("development", "holdout"))
    parser.add_argument("--development-lock", type=Path)
    args = parser.parse_args()
    if args.stage == "self-test":
        result = synthetic_self_test()
    elif args.stage == "register":
        result = register()
    elif args.stage == "features":
        result = build_features()
    elif args.stage == "labels":
        if not args.partition:
            parser.error("labels requires --partition")
        result = reveal_labels(args.partition, args.development_lock)
    elif args.stage == "dossiers":
        result = render_dossiers()
    else:
        _, body = verify_features()
        result = {"status": "ALL_FEATURES_AND_REGISTRATION_INTEGRITY_PASS", "points": len(body["points"])}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
