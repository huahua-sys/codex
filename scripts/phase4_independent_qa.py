#!/usr/bin/env python3
"""Independent, read-only Phase 4 QA; audit receipts alone are created.

Does not import the event extraction or label/statistics implementation.  A
SHA establishes byte identity, not historical availability or causal truth.
Each run needs a new audit version; failed receipts are deliberately retained.
"""
from __future__ import annotations

import argparse
import calendar
import collections
import datetime as dt
import hashlib
import html
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import statistics
import subprocess
from zoneinfo import ZoneInfo
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "research/phase4/audit/PRE_PHASE4_BASELINE.v001.json"
APPEND_ONLY = {
    "RESEARCH_LEDGER.md", "HYPOTHESIS_REGISTRY.md", "FAILED_HYPOTHESES.md",
    "CANDIDATE_PRINCIPLES.md", "OPEN_QUESTIONS.md", "CHANGELOG.md",
    "PREDICTION_LEDGER.md", "MULTIPLE_TESTING_LEDGER.md", "research/status/LATEST.md",
}
OPERATIVE = (
    "candidate_principles", "industry_specific_rules", "live_signal_generation_enabled",
    "price_in_checks", "regime_rules", "risk_signals", "sell_signals",
    "signals_to_monitor", "validated_principles",
)
REQUIRED_DOCS = (
    "MARKET_ECOLOGY_US.md", "MARKET_ECOLOGY_CHINA.md", "MARKET_ECOLOGY_JAPAN.md",
    "MARGINAL_PLAYER_MAP_US.md", "MARGINAL_PLAYER_MAP_CHINA.md",
    "MARGINAL_PLAYER_MAP_JAPAN.md", "CONSTRAINED_CAPITAL_FRAMEWORK.md",
    "MARKET_FOOTPRINTS.md", "PANIC_AND_FORCED_LIQUIDATION_FRAMEWORK.md",
    "SLOW_MONEY_TREND_FRAMEWORK.md", "EXPECTATION_GAP_FRAMEWORK.md",
    "CAPITAL_CYCLE_FRAMEWORK.md", "REVEALED_PREFERENCE_FRAMEWORK.md",
    "RULE_CHANGE_MONITOR.md", "HUMAN_DECISION_ARCHITECTURE.md",
    "FAILED_MECHANISM_CASES.md", "PHASE4_MARKET_ECOLOGY_REPORT.md", "README_PHASE4.md",
)
ALIASES = {"SHCOMP": "SSE", "NIKKEI": "N225", "N225": "N225", "SSE": "SSE"}
GOOD_PIT = {"VERIFIED", "VERIFIED_DATE_ONLY", "VERIFIED_CONSERVATIVE_SESSION_LAG", "VERIFIED_DATE_CONSERVATIVE", "VERIFIED_CONSERVATIVE_END_OF_DAY"}


class ReadableHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def source_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"%PDF"):
        result = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, check=True)
        return result.stdout.decode("utf-8", errors="replace")
    text = raw.decode("utf-8", errors="replace")
    if "<html" in text.lower() or "<!doctype" in text.lower():
        parser = ReadableHTML()
        parser.feed(text)
        return html.unescape(" ".join(parser.parts))
    return text


def normalized(text):
    return " ".join(str(text).split()).casefold()


def digest(path: Path, limit: int | None = None) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while limit is None or limit > 0:
            chunk = f.read(1 << 20 if limit is None else min(1 << 20, limit))
            if not chunk:
                break
            h.update(chunk)
            if limit is not None:
                limit -= len(chunk)
    return h.hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def iso(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timezone missing: {value}")
    return parsed


def local_month_add(date: dt.date, months: int) -> dt.date:
    y, m = divmod(date.year * 12 + date.month - 1 + months, 12)
    m += 1
    return dt.date(y, m, min(date.day, calendar.monthrange(y, m)[1]))


class Audit:
    def __init__(self, stage: str):
        self.check_count = 0
        self.failures = []
        self.notes = []
        self.coverage = {}
        self.stage = stage

    def check(self, ok, check_id, detail=None):
        self.check_count += 1
        if not ok:
            self.failures.append({"check": check_id, "detail": detail})

    def note(self, code, detail):
        self.notes.append({"code": code, "detail": detail})

    def identity(self):
        baseline = load(BASELINE)
        counts = collections.Counter()
        for old in baseline["files"]:
            rel = old["path"]
            path = ROOT / rel
            self.check(path.is_file(), "baseline.file_exists", rel)
            if not path.is_file():
                continue
            if rel in APPEND_ONLY:
                size = path.stat().st_size
                unchanged_prefix = size >= old["size_bytes"] and digest(path, old["size_bytes"]) == old["sha256"]
                self.check(unchanged_prefix, "baseline.authorized_append_prefix", rel)
                counts["append_only_checked"] += 1
                counts["appended"] += size > old["size_bytes"]
            elif rel == "CURRENT_FRAMEWORK.json":
                now = load(path)
                for field in OPERATIVE:
                    self.check(now.get(field) == baseline["framework"].get(field), "framework.operative_unchanged", field)
                self.check(now.get("validated_principles") == [], "framework.no_validated_principles")
                self.check(now.get("live_signal_generation_enabled") is False, "framework.live_disabled")
                counts["framework_metadata_only"] += 1
            else:
                self.check(path.stat().st_size == old["size_bytes"] and digest(path) == old["sha256"], "baseline.frozen_bytes", rel)
                counts["strict_byte_checked"] += 1
        oldzip = baseline["frozen_archive"]
        oldzip_path = Path(oldzip["path"])
        self.check(oldzip_path.is_file(), "complete_archive.exists", oldzip["path"])
        if oldzip_path.is_file():
            self.check(digest(oldzip_path) == oldzip["sha256"], "complete_archive.original_sha", oldzip["path"])
        self.coverage["immutability"] = dict(counts)
        self.coverage["baseline_raw_files"] = len(baseline["files"])
        self.note("IDENTITY_NOT_PIT", "原字节不变与哈希一致只证明本轮没有改写；不证明历史可得性、盲性或因果。")

    def protocol(self):
        path = ROOT / "research/phase4/protocols/BEHAVIORAL_EVENT_SELECTION_PROTOCOL.v001.lock.json"
        lock = load(path)
        self.check(digest(ROOT / lock["path"]) == lock["sha256"], "protocol.sha_matches")
        self.check(lock.get("future_event_labels_opened") is False, "protocol.no_new_labels_at_lock")
        self.check(lock.get("existing_phase3_labels_already_seen") is True, "protocol.history_seen_disclosed")
        self.check(lock.get("mode") == "EXPLORATORY_SOURCE_FIRST_NOT_BLIND", "protocol.not_claimed_blind")
        iso(lock["locked_at_utc"])
        self.coverage["protocol_lock"] = lock

    def sources_and_events(self):
        path = ROOT / "research/phase4/data/events.all.v001.json"
        lock_path = ROOT / "research/phase4/data/events.all.v001.lock.json"
        self.check(path.exists() and lock_path.exists(), "events.files_exist")
        if not path.exists() or not lock_path.exists():
            return
        body, lock = load(path), load(lock_path)
        self.check(digest(path) == lock["sha256"], "events.lock_sha")
        self.check(iso(lock["locked_at_utc"]) > iso(self.coverage["protocol_lock"]["locked_at_utc"]), "events.protocol_before_event_lock")
        self.check(iso(lock["locked_at_utc"]) > iso(body["created_at_utc"]), "events.generated_before_lock")
        self.check(lock["new_event_labels_read_before_lock"] is False, "events.labels_not_read_before_lock_claim")
        self.check(lock["prior_historical_outcomes_may_be_known"] is True, "events.history_memory_disclosed")
        self.check(body["mode"] == "EXPLORATORY_SOURCE_FIRST_NOT_BLIND", "events.exploratory_mode")
        self.check(body["new_probability_forecasts"] == 0, "events.no_new_forecast_count")
        for group in ("regional_inputs", "source_files", "code_files"):
            for rel, sha in lock[group].items():
                self.check((ROOT/rel).is_file(), "events.lock_input_exists", [group, rel])
                if (ROOT/rel).is_file():
                    self.check(digest(ROOT/rel) == sha, "events.lock_input_sha", [group, rel])
        self.check(body["regional_inputs"] == lock["regional_inputs"], "events.regional_input_lock_identical")
        events = body["events"]
        self.check(len(events) == len({e["event_id"] for e in events}), "events.unique_id")
        parents = {e["parent_episode"] for e in events}
        source_cache = {}
        kinds = collections.Counter()
        admitted = 0
        for event in events:
            eid = event["event_id"]
            required = ("market", "family", "parent_episode", "participant_type", "constraint", "observed_action", "action_status", "known_at_t", "unknown_at_t", "publication_date_evidence", "source_paths", "source_file_hashes", "study_asset")
            self.check(all(k in event for k in required), "events.required_schema", eid)
            self.check(event.get("outcomes") is None, "events.outcomes_not_in_frozen_event", eid)
            self.check(event.get("probability_forecast") is None, "events.no_probability_forecast", eid)
            self.check(event.get("original_quote_vintage_verified") is False and event.get("independent_first_publication_archive_verified") is False, "events.known_vintage_limit", eid)
            self.check(event.get("price_study_scope") == "BROAD_MARKET_CONTEXT_NOT_ISSUER_OR_FLOW_CAUSAL_EFFECT", "events.broad_context_scope", eid)
            self.check(event["market"] in {"US", "China", "Japan"}, "events.preregistered_markets", eid)
            if event.get("published_date"):
                self.check("2008-01-01" <= event["published_date"] <= "2025-12-31", "events.fixed_date_scope", eid)
            kinds[(event["market"], event["action_status"])] += 1
            for rel, sha in event["source_file_hashes"].items():
                self.check(rel in event["source_paths"] and lock["source_files"].get(rel) == sha, "events.source_exact_lock_reference", [eid, rel])
            self.check(set(event["source_file_hashes"]) == set(event["source_paths"]), "events.all_source_hashes", eid)
            flow = event.get("flow_size")
            if flow is not None:
                if not isinstance(flow, dict):
                    self.check(False, "events.flow_structured_not_freeform", eid)
                else:
                    self.check(all(k in flow for k in ("value", "unit", "basis")), "events.flow_units_basis", eid)
                    scope_provided = bool(flow.get("scope")) or (bool(event.get("flow_duration")) and bool(event.get("participant_type")) and "PERIOD_ACTUAL_REPURCHASE_VALUE" in str(flow.get("basis", "")))
                    self.check(scope_provided, "events.flow_scope_explicit_or_period_participant", eid)
                    if "scope" not in flow and scope_provided:
                        self.note("REGIONAL_SCOPE_SCHEMA_ADAPTER", {"event_id": eid, "scope_from": "flow_duration acquisition period + participant_type single issuer + PERIOD_ACTUAL_REPURCHASE_VALUE", "data_changed": False})
                    if flow.get("value") is not None:
                        self.check(isinstance(flow["value"], (int, float)) and math.isfinite(float(flow["value"])), "events.flow_numeric_finite", eid)
                    if event["action_status"] in {"ANNOUNCEMENT_ONLY", "MANDATE_CHANGE"}:
                        basis = str(flow.get("basis", "")).upper()
                        self.check(any(word in basis for word in ("NOT_ACTUAL", "NOT_EXECUTED", "CAPACITY", "CEILING", "AUTHORIZ", "LIMIT", "TARGET", "MANDATE", "ANNOUNCEMENT", "PLEDGE")), "events.announcement_not_actual_flow", eid)
            if event.get("source_proof_admitted"):
                admitted += 1
                self.check(event.get("pit_status") in GOOD_PIT and bool(event.get("available_at")), "events.admitted_has_qualified_T", eid)
                evidence = event["publication_date_evidence"]
                self.check(bool(evidence), "events.publication_evidence_not_empty", eid)
                proof_path = evidence.get("source_path") if isinstance(evidence, dict) else None
                excerpt = evidence.get("excerpt") if isinstance(evidence, dict) else str(evidence)
                if proof_path:
                    source = ROOT/proof_path
                    self.check(source.is_file(), "events.date_evidence_source_exists", [eid, proof_path])
                    if source.is_file():
                        if proof_path not in source_cache:
                            source_cache[proof_path] = normalized(source_text(source))
                        text = source_cache[proof_path]
                        # Some original datelines split the date and release
                        # clock.  Semicolon-separated quoted parts are checked
                        # separately, never interpreted as one fabricated quote.
                        parts = [x.strip() for x in str(excerpt).split(";") if x.strip()]
                        quoted_parts = [x for x in parts if len(x) > 6]
                        self.check(bool(quoted_parts) and all(normalized(x) in text for x in quoted_parts), "events.publication_quote_in_original_bytes", {"event_id": eid, "quote": excerpt, "path": proof_path})
                else:
                    self.note("PUBLICATION_EVIDENCE_MANUAL_REVIEW", {"event_id": eid, "reason": "发布日期证据没有唯一source_path，不能以哈希自动替代原发布日期核验。"})
                timestamp = iso(event["available_at"])
                published = dt.date.fromisoformat(event["published_date"])
                zone = ZoneInfo(event.get("timezone") or {"US": "America/New_York", "China": "Asia/Shanghai", "Japan": "Asia/Tokyo"}[event["market"]])
                local_available = timestamp.astimezone(zone)
                self.check(local_available.date() >= published, "events.available_not_before_publication_date", eid)
                precision = str(event.get("publication_date_precision") or (evidence.get("precision") if isinstance(evidence, dict) else "") or "").upper()
                if ("DATE" in precision or precision == "DAY") and "MINUTE" not in precision:
                    end_of_day = dt.datetime.combine(published, dt.time(23,59,59), zone)
                    self.check(timestamp >= end_of_day, "events.date_only_conservative_upper_bound", [eid, event["available_at"]])
            else:
                self.check(not event.get("available_at") or event.get("pit_status") not in GOOD_PIT or not event.get("source_paths") or not event.get("publication_date_evidence"), "events.admission_exclusion_consistent", eid)
            card_path = ROOT/f"research/evidence_cards/EC-{eid}.v001.json"
            event_path = ROOT/f"research/behavioral_events/{eid}.v001.json"
            self.check(card_path.exists() and event_path.exists(), "events.card_and_library_exists", eid)
            if event_path.exists():
                self.check(load(event_path) == event, "events.library_identical_frozen_event", eid)
            if card_path.exists():
                card = load(card_path)
                self.check(card.get("event_id") == eid and card.get("source_file_hashes") == event["source_file_hashes"], "events.evidence_card_source_identity", eid)
                self.check(bool(card.get("alternative_explanation")) and bool(card.get("falsifier")), "events.card_alternative_and_falsifier", eid)
        self.coverage["events"] = {"raw_records": len(events), "unique_parent_episodes": len(parents), "qualified_original_disclosures": admitted, "source_bytes_files": len(lock["source_files"]), "market_action_counts": {":".join(key): value for key, value in kinds.items()}, "independent_n": None}
        self.note("PARENT_DATE_YEAR_NOT_INDEPENDENT_N", "同一制度/公司/全球regime重复发布只计父项目、日期与年份覆盖，不计独立实验。")
        self.note("V002_AUDIT_SCHEMA_CORRECTION", "v002的8条JP scope-key FAIL是QA adapter键名假定过严格；原记录已明确single-issuer期间、JPY单位、PERIOD_ACTUAL_REPURCHASE_VALUE。v002保留，新QA读取这些原字段而不改events/labels。")

    def labels(self):
        path = ROOT / "research/phase4/labels/event_reactions.v001.json"
        if not path.is_file():
            self.check(False, "labels.exists", str(path))
            return
        body = load(path)
        lock_path = ROOT / "research/phase4/data/events.all.v001.lock.json"
        lock = load(lock_path)
        self.check(body["event_lock_sha256"] == digest(lock_path), "labels.event_lock_sha")
        self.check(iso(lock["locked_at_utc"]) < iso(body["created_at_utc"]), "labels.lock_before_reveal")
        self.check(body["mode"] == "EXPLORATORY_NOT_BLIND_NOT_CAUSAL_NOT_NET_ALPHA", "labels.exploratory_mode")
        events = load(ROOT / "research/phase4/data/events.all.v001.json")["events"]
        event_by_id = {e["event_id"]: e for e in events}
        records = body["records"]
        self.check(len(records) == len(events), "labels.all_events_retained")
        self.check(len({r["event_id"] for r in records}) == len(records), "labels.unique_id")
        self.check({r["event_id"] for r in records} == set(event_by_id), "labels.exact_event_coverage")
        cached = {}
        pool_cache = {}
        reactions = 0
        qualified = 0
        mature = collections.Counter()
        for record in records:
            eid = record["event_id"]
            self.check(record.get("probability_forecast") is None, "labels.no_new_forecast", eid)
            self.check(record.get("mechanism_identified") is False, "labels.no_causal_claim", eid)
            self.check(record.get("fundamental_solvency_identified") is False, "labels.solvency_not_imputed", eid)
            if record["status"] != "DESCRIPTIVE_EVENT_STUDY":
                self.check(not record.get("horizons"), "labels.uncertain_no_numeric_outcomes", eid)
                continue
            qualified += 1
            source = record["source"]
            source_path = ROOT / source["path"]
            self.check(digest(source_path) == source["sha256"], "labels.quote_sha", eid)
            self.check(source.get("original_quote_vintage_verified") is False, "labels.quote_vintage_unverified", eid)
            if record["asset"] not in cached:
                cached[record["asset"]] = sorted(load(source_path)["prices"], key=lambda row: row["date"])
            rows = cached[record["asset"]]
            cutoff = iso(record["available_at"])
            self.check(record["features"] == self.independent_features(rows, cutoff), "labels.preT_features", eid)
            self.check(set(record["horizons"]) == {"1w", "1m", "3m", "6m", "12m", "24m"}, "labels.fixed_horizons", eid)
            controls = record["matched_controls"]
            self.check(len(controls) in (0, 3), "labels.three_or_zero_controls", eid)
            self.check(len({c["date"] for c in controls}) == len(controls), "labels.unique_control_dates", eid)
            if record["asset"] not in pool_cache:
                pool_cache[record["asset"]] = self.independent_control_pool(rows)
            family_dates = [iso(e["available_at"]).date() for e in events if e["market"] == record["market"] and e["family"] == record["family"] and e.get("available_at")]
            expected_controls = self.independent_nearest_controls(record["features"], cutoff.date(), pool_cache[record["asset"]], family_dates)
            self.check([c["date"] for c in controls] == expected_controls, "labels.independent_nearest_control_selection", eid)
            for c in controls:
                self.check(c["features"] == self.independent_features(rows, iso(c["cutoff"])), "labels.control_preT_features", [eid, c["date"]])
                quarter = (dt.date.fromisoformat(c["date"]).month - 1) // 3
                year = int(c["date"][:4])
                earlier_same_quarter = [r for r in rows if int(r["date"][:4]) == year and (int(r["date"][5:7])-1)//3 == quarter]
                self.check(c["date"] == earlier_same_quarter[0]["date"], "labels.control_quarter_first", [eid, c["date"]])
                self.check(abs((dt.date.fromisoformat(c["date"]) - cutoff.date()).days) <= 366, "labels.control_window", [eid, c["date"]])
                family_dates = [iso(e["available_at"]).date() for e in events if e["market"] == record["market"] and e["family"] == record["family"] and e.get("available_at")]
                self.check(all(abs((dt.date.fromisoformat(c["date"]) - d).days) > 30 for d in family_dates), "labels.control_family_exclusion", [eid, c["date"]])
            for horizon, observed in record["horizons"].items():
                self.independent_reaction(rows, cutoff, horizon, observed["event"], eid)
                reactions += 1
                if observed["event"]["status"] == "REVEALED_PRICE_ONLY":
                    mature[horizon] += 1
                self.check(len(observed["controls"]) == len(controls), "labels.control_outcome_count", [eid, horizon])
                returns = []
                for c, cr in zip(controls, observed["controls"]):
                    self.check(cr["control_date"] == c["date"], "labels.control_outcome_identity", [eid, horizon])
                    self.independent_reaction(rows, iso(c["cutoff"]), horizon, cr, [eid, c["date"]])
                    reactions += 1
                    if cr["status"] == "REVEALED_PRICE_ONLY":
                        returns.append(cr["gross_price_return"])
                mean_control = math.fsum(returns)/3 if len(returns) == 3 else None
                delta = observed["event"].get("gross_price_return") - mean_control if mean_control is not None and observed["event"]["status"] == "REVEALED_PRICE_ONLY" else None
                self.near(observed["control_mean_price_return"], mean_control, "labels.control_mean", [eid, horizon])
                self.near(observed["matched_time_difference"], delta, "labels.matched_difference", [eid, horizon])
                expected_class = "UNIDENTIFIED" if delta is None else "NEUTRAL" if abs(delta) < .02 else "POSITIVE" if delta > 0 else "NEGATIVE"
                self.check(observed["result_class"] == expected_class, "labels.fixed_descriptive_class", [eid, horizon])
                self.check(observed["same_asset_benchmark_difference"] == (0.0 if observed["event"]["status"] == "REVEALED_PRICE_ONLY" else None), "labels.no_fictitious_benchmark_alpha", [eid, horizon])
        self.coverage["labels"] = {"raw_event_records": len(records), "qualified_events": qualified, "event_and_control_reactions_checked": reactions, "mature_by_horizon": dict(mature), "probability_forecasts": 0}
        self.note("MATCHED_CONTROLS_NOT_CAUSAL", "同一资产不同日期的价格状态匹配不控制估值、信用与预期；后续控制日期不能用作T时已知数据，这里只能作探索性结果比较。")
        self.statistics(records, path)

    def near(self, actual, expected, check_id, detail):
        ok = actual is None and expected is None
        if actual is not None and expected is not None:
            ok = math.isfinite(float(actual)) and math.isclose(float(actual), float(expected), rel_tol=1e-10, abs_tol=1e-12)
        self.check(ok, check_id, {"record": detail, "actual": actual, "expected": expected})

    @staticmethod
    def independent_features(rows, cutoff):
        observations = [r for r in rows if iso(r["available_at"]) <= cutoff]
        if len(observations) < 64:
            return None
        observations = observations[-64:]
        closes = [float(r["close"]) for r in observations]
        if not all(math.isfinite(x) and x > 0 for x in closes):
            return None
        daily = [b/a - 1 for a, b in zip(closes, closes[1:])]
        return {"r63": closes[-1]/closes[0]-1, "vol63": statistics.stdev(daily)*math.sqrt(252), "last_known_date": observations[-1]["date"]}

    def independent_control_pool(self, rows):
        seen_quarters = set()
        result = []
        for r in rows:
            day = dt.date.fromisoformat(r["date"])
            quarter = (day.year, (day.month-1)//3)
            if quarter in seen_quarters:
                continue
            seen_quarters.add(quarter)
            cutoff = iso(r["session_open_at"]) - dt.timedelta(microseconds=1)
            past_features = self.independent_features(rows, cutoff)
            if past_features is not None:
                result.append({"date": r["date"], "features": past_features})
        return result

    @staticmethod
    def independent_nearest_controls(features, day, pool, family_dates):
        if features is None:
            return []
        candidate = []
        for row in pool:
            control_day = dt.date.fromisoformat(row["date"])
            if abs((control_day-day).days) <= 366 and all(abs((control_day-event_day).days) > 30 for event_day in family_dates):
                candidate.append(row)
        if len(candidate) < 3:
            return []
        scales = {}
        for variable in ("r63", "vol63"):
            values = [r["features"][variable] for r in candidate]
            mean = math.fsum(values)/len(values)
            scales[variable] = math.sqrt(math.fsum((v-mean)**2 for v in values)/len(values)) or 1.0
        distances = []
        for row in candidate:
            d = math.fsum(((row["features"][variable]-features[variable])/scales[variable])**2 for variable in ("r63", "vol63"))
            distances.append((d, row["date"]))
        return [date for _, date in sorted(distances)[:3]]

    def independent_reaction(self, rows, cutoff, horizon, observed, record_id):
        # Select endpoints independently from complete canonical records.  In
        # particular, no claimed endpoint from the label can select its own input.
        after = [r for r in rows if iso(r["session_open_at"]) > cutoff]
        if not after:
            self.check(observed["status"] == "NO_POST_PUBLICATION_OPEN", "reaction.no_post_open", record_id)
            return
        entry = min(after, key=lambda r: iso(r["session_open_at"]))
        if not entry.get("open") or float(entry["open"]) <= 0:
            self.check(observed["status"] == "NOT_EXECUTION_IDENTIFIED", "reaction.open_missing", record_id)
            return
        entry_date = dt.date.fromisoformat(entry["date"])
        target = entry_date + dt.timedelta(days=7) if horizon == "1w" else local_month_add(entry_date, int(horizon[:-1]))
        eligible_exits = [r for r in rows if dt.date.fromisoformat(r["date"]) >= target]
        self.check(observed.get("entry_date") == entry["date"], "reaction.first_postT_open", [record_id, horizon])
        self.check(observed.get("target_date") == target.isoformat(), "reaction.fixed_calendar_horizon", [record_id, horizon])
        if not eligible_exits:
            self.check(observed["status"] == "PENDING_HORIZON", "reaction.pending_not_zero", [record_id, horizon])
            self.check("gross_price_return" not in observed, "reaction.pending_no_return", [record_id, horizon])
            return
        exit_row = min(eligible_exits, key=lambda r: r["date"])
        self.check(observed["status"] == "REVEALED_PRICE_ONLY", "reaction.mature_status", [record_id, horizon])
        self.check(observed["exit_date"] == exit_row["date"], "reaction.first_exit_session", [record_id, horizon])
        self.check(iso(observed["entry_open_at"]) == iso(entry["session_open_at"]) > cutoff, "reaction.execution_strictly_after_publication", [record_id, horizon])
        entry_price = float(entry["open"])
        self.near(observed["entry_open"], entry_price, "reaction.original_open", [record_id, horizon])
        self.near(observed["exit_close"], exit_row["close"], "reaction.original_close", [record_id, horizon])
        price_return = float(exit_row["close"])/entry_price - 1
        self.near(observed["gross_price_return"], price_return, "reaction.price_return", [record_id, horizon])
        self.near(observed["illustrative_20bp_roundtrip_return"], price_return-.002, "reaction.fixed_cost_sensitivity", [record_id, horizon])
        holding = [r for r in rows if entry["date"] <= r["date"] <= exit_row["date"]]
        closes = [float(r["close"]) for r in holding]
        running_max = entry_price
        worst_drawdown = 0.0
        for close in closes:
            running_max = max(running_max, close)
            worst_drawdown = min(worst_drawdown, close/running_max-1)
        self.near(observed["maximum_close_to_close_drawdown"], worst_drawdown, "reaction.maximum_close_drawdown", [record_id, horizon])
        self.near(observed["maximum_adverse_close_excursion"], min(closes)/entry_price-1, "reaction.close_MAE", [record_id, horizon])
        self.near(observed["maximum_favorable_close_excursion"], max(closes)/entry_price-1, "reaction.close_MFE", [record_id, horizon])
        self.check(observed["sessions"] == len(holding), "reaction.held_sessions", [record_id, horizon])
        self.check(observed["session_dates_sha256"] == hashlib.sha256(json.dumps([r["date"] for r in holding]).encode()).hexdigest(), "reaction.session_hash", [record_id, horizon])
        self.check(observed["dividends_included"] is False, "reaction.not_claimed_total_return", [record_id, horizon])

    def statistics(self, records, label_path):
        import numpy as np
        path = ROOT / "research/phase4/analysis/event_study.results.v001.json"
        if not path.exists():
            self.check(False, "statistics.exists", str(path))
            return
        results = load(path)
        self.check(results["label_sha256"] == digest(label_path), "statistics.label_sha")
        self.check(iso(results["created_at_utc"]) > iso(load(label_path)["created_at_utc"]), "statistics.after_labels")
        self.check(results["raw_event_records"] == len(records), "statistics.raw_count")
        self.check(results["independent_n"] is None, "statistics.independent_n_not_invented")
        self.check(results["probability_forecasts"] == 0, "statistics.no_new_forecasts")
        self.check(results["mechanisms_identified"] == 0 and results["alpha_established"] is False, "statistics.no_causal_or_alpha_claim")
        expected_groups = {(r["market"], r["family"], r["action_status"]) for r in records}
        actual_slots = {(r["market"], r["family"], r["action_status"], r["horizon"]) for r in results["slots"]}
        expected_slots = {g + (h,) for g in expected_groups for h in ("1w", "1m", "3m", "6m", "12m", "24m")}
        self.check(actual_slots == expected_slots, "statistics.all_slots_including_failure_retained")
        self.check(len(actual_slots) == len(results["slots"]) == results["comparison_slots"], "statistics.no_duplicate_slots")
        for slot in results["slots"]:
            group = (slot["market"], slot["family"], slot["action_status"])
            selected = [r for r in records if (r["market"], r["family"], r["action_status"]) == group]
            h = slot["horizon"]
            mature = [r for r in selected if r.get("horizons", {}).get(h, {}).get("event", {}).get("status") == "REVEALED_PRICE_ONLY"]
            matched = [r for r in mature if r["horizons"][h]["matched_time_difference"] is not None]
            key = list(group) + [h]
            self.check(slot["selected_raw"] == len(selected), "statistics.selected_raw", key)
            self.check(slot["mature_raw"] == len(mature), "statistics.mature_raw", key)
            self.check(slot["matched_raw"] == len(matched), "statistics.matched_raw", key)
            self.check(slot["unique_parent"] == len({r["parent_episode"] for r in mature}), "statistics.unique_parent", key)
            self.check(slot["calendar_years"] == len({r["year"] for r in mature}), "statistics.years", key)
            self.check(slot["unique_publication_dates"] == len({r["available_at"][:10] for r in mature}), "statistics.publication_dates", key)
            self.check(slot["effective_n"] is None, "statistics.not_raw_equals_independent", key)
            last_exit = None
            nonoverlap = []
            for r in sorted(mature, key=lambda r: (r["horizons"][h]["event"]["entry_date"], r["event_id"])):
                obs = r["horizons"][h]["event"]
                if last_exit is None or obs["entry_date"] > last_exit:
                    nonoverlap.append(r)
                    last_exit = obs["exit_date"]
            self.check(slot["actual_nonoverlap_raw"] == len(nonoverlap), "statistics.actual_wholeperiod_nonoverlap", key)
            for field, values in (
                ("gross_price_return", [r["horizons"][h]["event"]["gross_price_return"] for r in mature]),
                ("matched_time_difference", [r["horizons"][h]["matched_time_difference"] for r in matched]),
                ("maximum_drawdown", [r["horizons"][h]["event"]["maximum_close_to_close_drawdown"] for r in mature]),
            ):
                summary = slot[field]
                self.check(summary["n_raw"] == len(values), "statistics.distribution_N", [key, field])
                if values:
                    sorted_values = sorted(values)
                    expected = {"mean": math.fsum(values)/len(values), "median": statistics.median(values), "win_rate": sum(v>0 for v in values)/len(values), "min": min(values), "max": max(values)}
                    for name, q in (("p25", .25), ("p75", .75), ("worst_decile", .1), ("best_decile", .9)):
                        position = (len(sorted_values)-1)*q
                        lo = math.floor(position)
                        hi = math.ceil(position)
                        expected[name] = sorted_values[lo] + (sorted_values[hi]-sorted_values[lo])*(position-lo)
                    for name, value in expected.items():
                        self.near(summary[name], value, "statistics.distribution_scalar", [key, field, name])
            interval = slot["matched_difference_interval"]
            unique_parents = {r["parent_episode"] for r in matched}
            unique_years = {r["year"] for r in matched}
            if len(unique_parents) < 8 or len(unique_years) < 8:
                self.check(interval["status"] == "INSUFFICIENT_CLUSTER_CI" and "lower" not in interval and "upper" not in interval, "statistics.CI_gate_true_parents_and_years", key)
            else:
                self.check(interval["status"] == "DESCRIPTIVE_YEAR_CLUSTER_BOOTSTRAP", "statistics.CI_expected", key)
                self.check(interval["replicates"] == 2000 and interval["seed"] == 4102026, "statistics.fixed_bootstrap_settings", key)
                values_by_parent_year = collections.defaultdict(list)
                for r in matched:
                    values_by_parent_year[(r["parent_episode"], r["year"])].append(r["horizons"][h]["matched_time_difference"])
                values_by_year = collections.defaultdict(list)
                for (_, year), values in values_by_parent_year.items():
                    values_by_year[year].append(math.fsum(values)/len(values))
                years = sorted(values_by_year)
                rng = np.random.default_rng(4102026)
                bootstrap = []
                for _ in range(2000):
                    drawn = rng.choice(years, size=len(years), replace=True)
                    values = [v for year in drawn for v in values_by_year[int(year)]]
                    bootstrap.append(math.fsum(values)/len(values))
                self.near(interval["estimate_parent_collapsed"], math.fsum(v for vv in values_by_year.values() for v in vv)/len(values_by_parent_year), "statistics.parent_collapsed_mean", key)
                self.near(interval["lower"], np.quantile(bootstrap, .025), "statistics.independent_bootstrap_lower", key)
                self.near(interval["upper"], np.quantile(bootstrap, .975), "statistics.independent_bootstrap_upper", key)
        negatives = {(r["event_id"], h) for r in records for h, outcome in r.get("horizons", {}).items() if outcome["matched_time_difference"] is not None and outcome["matched_time_difference"] <= 0}
        actual_negatives = {(r["event_id"], r["horizon"]) for r in results["nonpositive_matched_cases"]}
        self.check(negatives == actual_negatives, "statistics.all_nonpositive_matched_cases_saved")
        self.coverage["statistics"] = {"all_comparison_slots": len(results["slots"]), "nonpositive_matched_case_horizons": len(actual_negatives)}

    def final_package(self, package: Path):
        self.check(package.is_file(), "package.exists", str(package))
        if not package.is_file():
            return
        self.check(package.stat().st_size < 10_000_000, "package.under_10MB", package.stat().st_size)
        with zipfile.ZipFile(package) as archive:
            members = archive.namelist()
            self.check(len(members) == len(set(members)), "package.no_duplicate_members")
            self.check(all(not x.startswith("/") and ".." not in Path(x).parts for x in members), "package.safe_member_names")
            self.check(archive.testzip() is None, "package.crc_pass")
            for name in REQUIRED_DOCS:
                found = [x for x in members if Path(x).name == name]
                self.check(len(found) == 1, "package.required_document", name)
            candidates = [x for x in members if Path(x).name in {"EXPORT_MANIFEST.json", "CORE_EXPORT_MANIFEST.json"}]
            self.check(len(candidates) == 1, "package.one_manifest", candidates)
            if len(candidates) == 1:
                manifest_name = candidates[0]
                manifest = json.loads(archive.read(manifest_name))
                records = manifest.get("files", [])
                prefix = str(Path(manifest_name).parent)
                prefix = "" if prefix == "." else prefix + "/"
                declared = []
                for record in records:
                    key = prefix + record["path"]
                    declared.append(key)
                    self.check(key in members, "package.manifest_member_exists", key)
                    if key in members:
                        data = archive.read(key)
                        self.check(len(data) == record.get("size_bytes", record.get("bytes")), "package.member_size", key)
                        self.check(hashlib.sha256(data).hexdigest() == record["sha256"], "package.member_sha", key)
                actual = {x for x in members if not x.endswith("/") and x != manifest_name}
                self.check(set(declared) == actual, "package.manifest_full_coverage", {"unlisted": sorted(actual-set(declared)), "missing": sorted(set(declared)-actual)})
        self.coverage["core_package"] = {"path": str(package), "bytes": package.stat().st_size, "sha256": digest(package)}
        self.note("V004_MANIFEST_FILENAME_ADAPTER_CORRECTION", "v004仅因QA硬编码EXPORT_MANIFEST.json而未识别本包实际CORE_EXPORT_MANIFEST.json失败；v004保留。新版读取明确两种manifest名并核对每份字节，不修改原CORE、事件或统计。")

    def supplementary_source_ledgers(self):
        checked = 0
        directory = ROOT / "research/phase4/sources/frameworks"
        for ledger_path in sorted(directory.glob("FRAMEWORK_SOURCE_LEDGER.*.json")):
            ledger = load(ledger_path)
            if ledger.get("previous_ledger_sha256"):
                previous = directory / "FRAMEWORK_SOURCE_LEDGER.v001.json"
                self.check(digest(previous) == ledger["previous_ledger_sha256"], "supplementary.previous_ledger_sha", str(ledger_path.relative_to(ROOT)))
            for source in ledger["sources"]:
                self.check(source["historical_event_admissible"] is False and source["available_at_for_historical_replay"] is None, "supplementary.current_reference_not_historical_signal", source["source_id"])
                if source.get("sha256") and source.get("path"):
                    path = directory / source["path"]
                    self.check(path.is_file(), "supplementary.framework_bytes_exists", source["source_id"])
                    if path.is_file():
                        self.check(digest(path) == source["sha256"] and path.stat().st_size == source["bytes"], "supplementary.framework_source_sha_size", source["source_id"])
                        checked += 1
        path = ROOT / "research/phase4/audit/counterexamples/source_fetch_manifest.v001.json"
        if path.exists():
            ledger = load(path)
            for source in ledger:
                if source.get("sha256") and source.get("path"):
                    source_path = ROOT/source["path"]
                    self.check(source_path.is_file(), "supplementary.counterexample_bytes_exists", source["id"])
                    if source_path.is_file():
                        self.check(digest(source_path) == source["sha256"] and source_path.stat().st_size == source["bytes"], "supplementary.counterexample_source_sha_size", source["id"])
                        checked += 1
                self.check(source.get("scope") == "RETROSPECTIVE_MECHANISM_AUDIT_NOT_BLIND_SIGNAL", "supplementary.counterexample_not_blind_signal", source["id"])
        self.coverage["supplementary_source_records_checked"] = checked

    def append_only_scope_errata(self):
        directory = ROOT / "research/phase4/regional/us"
        new_path = directory / "events.v002.json"
        if not new_path.exists():
            self.check(False, "scope_errata.new_version_exists")
            return
        old_path = directory / "events.json"
        lock = load(directory / "events.lock.v002.json")
        self.check(digest(old_path) == lock["previous_sha256"], "scope_errata.old_sha_unchanged")
        self.check(digest(new_path) == lock["sha256"], "scope_errata.new_sha_matches")
        old, new = load(old_path), load(new_path)
        self.check(len(old) == len(new) == 42, "scope_errata.no_selected_events_added_or_removed")
        self.check([r["event_id"] for r in old] == [r["event_id"] for r in new], "scope_errata.same_order_ids")
        changed = []
        for previous, revised in zip(old, new):
            eid = previous["event_id"]
            if previous == revised:
                continue
            changed.append(eid)
            self.check(previous["family"] == "corporate_capital_allocation", "scope_errata.corporate_only", eid)
            keys_changed = {k for k in set(previous)|set(revised) if previous.get(k) != revised.get(k)}
            allowed = {"observed_action"} | ({"flow_size", "unknown_at_t"} if eid == "US-P4-010" else set())
            self.check(keys_changed <= allowed, "scope_errata.explanation_only_fields", [eid, sorted(keys_changed)])
            if "flow_size" in keys_changed:
                old_flow, new_flow = previous["flow_size"], revised["flow_size"]
                self.check({k: v for k,v in old_flow.items() if k != "basis"} == {k: v for k,v in new_flow.items() if k != "basis"}, "scope_errata.no_flow_amount_or_units_changed", eid)
                self.check(new_flow["basis"].startswith(old_flow["basis"]), "scope_errata.basis_only_appended", eid)
            if "unknown_at_t" in keys_changed:
                self.check(revised["unknown_at_t"][:len(previous["unknown_at_t"])] == previous["unknown_at_t"], "scope_errata.unknowns_only_appended", eid)
        self.check(len(changed) == 9, "scope_errata.exact_nine_scope_annotations", changed)
        frozen = load(ROOT / "research/phase4/data/events.all.v001.lock.json")
        self.check(frozen["regional_inputs"][str(old_path.relative_to(ROOT))] == digest(old_path), "scope_errata.global_v001_still_points_original")
        self.coverage["scope_errata"] = {"corrected_explanation_records": len(changed), "original_selection_dates_numeric_amounts_and_labels_unchanged": True}
        self.note("CORPORATE_CASH_ROW_NOT_OPEN_MARKET_BUYING", "US-P4-010原2009来源同时报现金行$22m与无常规季度回购，交易类别桥接未识别。其余8年误复用2009语义的注释按v002收窄；不改原v001或全部价格标签，现金金额不能当公开市场买盘。")

    def save(self, version):
        directory = ROOT / "research/phase4/audit"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"INDEPENDENT_PHASE4_QA.{version}.json"
        result = {
            "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "stage": self.stage,
            "status": "FAIL" if self.failures else "PASS" if self.stage == "final" else "PASS_PRELIMINARY_STAGE_ONLY",
            "independent_check_count": self.check_count,
            "failures": self.failures,
            "coverage": self.coverage,
            "notes": self.notes,
            "qa_script_sha256": digest(Path(__file__)),
            "limitations": [
                "工程QA不证明事件目录完整、不证明条件可投资或经济机制因果。",
                "研究者已知历史，必须保持EXPLORATORY；新预测与live决策为0。",
            ],
        }
        with path.open("x", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(json.dumps({"path": str(path.relative_to(ROOT)), "status": result["status"], "checks": self.check_count, "failures": self.failures[:25]}, ensure_ascii=False))
        return 1 if self.failures else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("preflight", "events", "labels", "final"), default="preflight")
    parser.add_argument("--version", required=True)
    parser.add_argument("--package", type=Path, default=Path("/workspace/outputs/Investment_Research_Phase4_CORE.zip"))
    args = parser.parse_args()
    audit = Audit(args.stage)
    audit.identity()
    audit.protocol()
    if args.stage in ("events", "labels", "final"):
        audit.sources_and_events()
    if args.stage in ("labels", "final"):
        audit.labels()
    if args.stage == "final":
        audit.supplementary_source_ledgers()
        audit.append_only_scope_errata()
        audit.final_package(args.package)
    raise SystemExit(audit.save(args.version))


if __name__ == "__main__":
    main()
