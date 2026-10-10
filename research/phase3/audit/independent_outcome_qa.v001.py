"""Independent Phase3 outcome/integrity audit. Writes only its own audit folder.

Runs after root authorization to read both future-label partitions. No forecasts,
strategies, optimizers, or locked research artifacts are changed.
"""
from pathlib import Path
from datetime import datetime, timezone
import bisect
import collections
import hashlib
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
AD = ROOT / "research/phase3/audit"
BASE = ROOT / "research/phase3"


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def od(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def ts(value):
    return datetime.fromisoformat(value)


def write_once(name, data):
    with (AD / name).open("x") as handle:
        json.dump(data, handle, ensure_ascii=False, sort_keys=True, indent=2,
                  allow_nan=False)
        handle.write("\n")


def mdd(path):
    w = np.asarray(path, dtype=float)
    return float(np.min(w / np.maximum.accumulate(w) - 1))


def independently_value(rows, actions, total_return=True):
    """Explicit units and entitlement ledger, not the existing evaluator."""
    byday = collections.defaultdict(list)
    for action in actions:
        byday[action["date"]].append(action)
    initial = rows[0]["open"]
    units = 1.0
    lows, highs, closes, comparable = [0.0], [0.0], [1.0], [1.0]
    for i, row in enumerate(rows):
        dividend = 0.0
        if i > 0:
            units *= math.prod(float(a["ratio"]) for a in byday[row["date"]]
                               if a["action_type"] == "split")
            if total_return:
                dividend = units * sum(float(a["amount"]) for a in byday[row["date"]]
                                       if a["action_type"] == "dividend")
        if i == len(rows) - 1:
            stock = units * row["open"]
            terminal = (stock + dividend) / initial
            lows.append(terminal - 1)
            highs.append(terminal - 1)
            closes.append(terminal)
            # Terminal dividend receivable is not subject to stock liquidation fee.
            comparable.append((stock * .9975 + dividend) / (initial * 1.0025))
        else:
            lows.append((units * row["low"] + dividend) / initial - 1)
            highs.append((units * row["high"] + dividend) / initial - 1)
            closes.append((units * row["close"] + dividend) / initial)
            comparable.append((units * row["close"] + dividend) / (initial * 1.0025))
            units += dividend / row["close"]
    return {"gross_return": terminal - 1,
            "net_return": terminal * .9975 / 1.0025 - 1,
            "max_adverse_excursion": min(lows),
            "max_favorable_excursion": max(highs),
            "max_drawdown": mdd(closes),
            "comparable_net_return": comparable[-1] - 1,
            "comparable_mdd": mdd(comparable),
            "comparable_path": comparable}


def main():
    design = read(BASE / "design.v001.json")
    feature_path = BASE / "features/decision_points.v001.json"
    features = read(feature_path)
    feature_lock = read(BASE / "features/decision_points.v001.SHA.lock.json")
    registry = read(BASE / "panel.registration.v001.json")
    assert feature_lock["feature_sha256"] == sha(feature_path)
    assert all(sha(ROOT / name) == expected for name, expected in
               registry["source_and_code_sha256"].items())
    feature_map = {p["point_id"]: p for p in features["points"]}
    assets = {a["asset_id"]: a for a in design["assets"]}
    sources, prepared, bydates, actionsbyasset = {}, {}, {}, {}
    for aid in assets:
        path = BASE / "data/market" / (aid + ".canonical.json")
        if path.exists() and aid != "XLF":
            bundle = read(path)
            rows = sorted(bundle["prices"], key=lambda r: ts(r["session_open_at"]))
            prepared[aid] = (rows, [ts(r["session_open_at"]) for r in rows])
            bydates[aid] = {r["date"]: r for r in rows}
            actionsbyasset[aid] = bundle.get("actions", [])
            sources[aid] = bundle
    expected_cache = {}

    def expected(aid, cutoff, n):
        key = aid, cutoff, n
        if key not in expected_cache:
            if aid not in prepared:
                expected_cache[key] = None
            else:
                rows, opens = prepared[aid]
                start = bisect.bisect_right(opens, ts(cutoff))
                held = rows[start:start + n + 1]
                if len(held) < n + 1:
                    expected_cache[key] = None
                else:
                    acts = [a for a in actionsbyasset[aid]
                            if held[0]["date"] < a["date"] <= held[-1]["date"]]
                    value = independently_value(held, acts, assets[aid]["instrument_type"] == "ETF")
                    value.update(rows=held, actions=acts,
                                 session_sha256=od([r["date"] for r in held]))
                    expected_cache[key] = value
        return expected_cache[key]

    fixed_dates = sorted(set(bydates["SPY"]) & set(bydates["IEF"]) & set(bydates["BIL"]))
    fixed_opens = [ts(bydates["SPY"][d]["session_open_at"]) for d in fixed_dates]
    fixed_cache = {}
    weights = {"FIXED_50_50_SPY_BIL": {"SPY": .5, "BIL": .5},
               "FIXED_60_40_SPY_IEF": {"SPY": .6, "IEF": .4},
               "FIXED_70_30_SPY_IEF": {"SPY": .7, "IEF": .3}}

    def fixed(cutoff, n):
        key = cutoff, n
        if key not in fixed_cache:
            start = bisect.bisect_right(fixed_opens, ts(cutoff))
            dates = fixed_dates[start:start + n + 1]
            if len(dates) < n + 1:
                fixed_cache[key] = None
            else:
                components = {}
                for aid in ["SPY", "IEF", "BIL"]:
                    component_rows = [bydates[aid][d] for d in dates]
                    components[aid] = independently_value(component_rows, actionsbyasset[aid])
                values = {}
                for name, w in weights.items():
                    nav = sum(weight * np.asarray(components[aid]["comparable_path"])
                              for aid, weight in w.items())
                    values[name] = {"net_return": float(nav[-1] - 1),
                                    "net_max_drawdown": mdd(nav)}
                fixed_cache[key] = {"session_sha256": od(dates), "values": values}
        return fixed_cache[key]

    errors, check_counts = [], collections.Counter()

    def eq(observed, calculated, description):
        check_counts[description.split(":", 1)[0]] += 1
        if not math.isclose(float(observed), float(calculated), rel_tol=2e-9, abs_tol=3e-11):
            errors.append({"check": description, "observed": observed,
                           "independent": calculated})

    partition_labels, merged = {}, []
    label_locks, analysis_locks = {}, {}
    for partition in ["development", "holdout"]:
        path = BASE / f"labels/{partition}.v001.json"
        labels = read(path)
        lock = read(BASE / f"labels/{partition}.v001.SHA.lock.json")
        alock = read(BASE / f"analysis/{partition}.lock.v001.json")
        assert lock["label_sha256"] == sha(path)
        assert labels["feature_sha256"] == lock["feature_sha256"] == sha(feature_path)
        assert all(sha(ROOT / name) == expected for name, expected in alock["files"].items())
        label_locks[partition], analysis_locks[partition] = lock, alock
        assert len(labels["points"]) == (2496 if partition == "development" else 208)
        partition_labels[partition] = labels
        for point in labels["points"]:
            p = feature_map[point["point_id"]]
            assert p["year"] <= 2023 if partition == "development" else p["year"] >= 2024
            assert point["cutoff_at"] == p["cutoff_at"]
            assert set(point["horizons"]) == set(design["horizons"])
            for horizon, n in design["horizons"].items():
                label = point["horizons"][horizon]
                if p["status"] in {"NO_SOURCE", "EXCLUDED_INSTRUMENT"}:
                    assert label["status"] == p["status"] and label.get("net_return") is None
                    continue
                value = expected(p["asset_id"], p["cutoff_at"], n)
                if value is None:
                    assert label["status"] == "PENDING_HORIZON" and label.get("net_return") is None
                    continue
                assert label["status"] == "REVEALED"
                rows = value["rows"]
                assert ts(rows[0]["session_open_at"]) > ts(p["cutoff_at"])
                assert label["entry_date"] == rows[0]["date"] and label["exit_date"] == rows[-1]["date"]
                assert label["sessions_held"] == n and label["price_evidence_record_count"] == n + 1
                assert label["execution_session_dates_sha256"] == value["session_sha256"]
                assert label["price_evidence_record_ids_sha256"] == od([r["record_id"] for r in rows])
                assert label["action_evidence_record_ids"] == [a["record_id"] for a in value["actions"]]
                for metric in ["gross_return", "net_return", "max_drawdown",
                               "max_adverse_excursion", "max_favorable_excursion"]:
                    eq(label[metric], value[metric], f"primary_{metric}:{point['point_id']}:{horizon}")
                check_counts["revealed_horizon_labels"] += 1
                b = label["benchmark"]
                if b["status"] == "SAME_EXECUTION":
                    bv = expected(b["benchmark_id"], p["cutoff_at"], n)
                    assert bv and bv["session_sha256"] == value["session_sha256"]
                    assert assets[b["benchmark_id"]]["currency"] == p["currency"]
                    eq(b["net_return"], bv["net_return"], f"paired_benchmark_return:{point['point_id']}:{horizon}")
                    eq(b["difference_net_return"], value["net_return"] - bv["net_return"],
                       f"paired_benchmark_difference:{point['point_id']}:{horizon}")
                for name, result in label["fixed_allocation_benchmarks"].items():
                    if result["status"] == "SAME_EXECUTION":
                        f = fixed(p["cutoff_at"], n)
                        assert f and f["session_sha256"] == value["session_sha256"]
                        eq(result["net_return"], f["values"][name]["net_return"], f"fixed_return:{point['point_id']}:{horizon}:{name}")
                        eq(result["net_max_drawdown"], f["values"][name]["net_max_drawdown"], f"fixed_mdd:{point['point_id']}:{horizon}:{name}")
                        eq(result["asset_comparable_net_return"], value["comparable_net_return"], f"same_helper_asset_return:{point['point_id']}:{horizon}:{name}")
                        eq(result["asset_comparable_mdd"], value["comparable_mdd"], f"same_helper_asset_mdd:{point['point_id']}:{horizon}:{name}")
                        eq(result["difference_net_return"], value["comparable_net_return"] - f["values"][name]["net_return"], f"fixed_residual:{point['point_id']}:{horizon}:{name}")
                if p["feature_eligible"]:
                    merged.append({"point_id": point["point_id"], "asset_id": p["asset_id"],
                                   "partition": partition, "horizon": horizon,
                                   "entry_date": label["entry_date"], "exit_date": label["exit_date"],
                                   "net_return": label["net_return"], "max_drawdown": label["max_drawdown"]})
    assert ts(feature_lock["locked_at"]) <= ts(partition_labels["development"]["revealed_at"])
    assert ts(label_locks["development"]["locked_at"]) <= ts(analysis_locks["development"]["locked_at"])
    assert ts(analysis_locks["development"]["locked_at"]) <= ts(partition_labels["holdout"]["revealed_at"])
    assert ts(label_locks["holdout"]["locked_at"]) <= ts(analysis_locks["holdout"]["locked_at"])
    assert label_locks["holdout"]["development_analysis_lock"]["sha256"] == sha(BASE / "analysis/development.lock.v001.json")
    prior = read(AD / "PRIOR_STATE.v001.json")
    prior_changes = [name for name, row in prior["immutable_file_hashes"].items()
                     if not (ROOT / name).is_file() or sha(ROOT / name) != row["sha256"]]
    assert not prior_changes, prior_changes
    assert not errors, errors[:10]
    # Appendix only: merged non-overlap is never used to change old results.
    recorded_nonoverlap = {}
    for partition in ["development", "holdout"]:
        original = read(BASE / f"analysis/{partition}.results.v001.json")
        recorded_nonoverlap[partition] = {
            (r["asset_id"], r["horizon"]): r["point_ids"]
            for r in original["actual_nonoverlap"]}
        del original
    appendix = []
    for horizon in ["12m", "24m"]:
        for aid in sorted(assets):
            candidates = sorted([r for r in merged if r["asset_id"] == aid and r["horizon"] == horizon],
                                key=lambda r: (r["entry_date"], r["point_id"]))
            chosen, end = [], None
            for row in candidates:
                if end is None or row["entry_date"] >= end:
                    chosen.append(row)
                    end = row["exit_date"]
            separate = []
            for partition in ["development", "holdout"]:
                own, end = [], None
                for row in [r for r in candidates if r["partition"] == partition]:
                    if end is None or row["entry_date"] >= end:
                        own.append(row)
                        end = row["exit_date"]
                separate.extend(own)
                assert recorded_nonoverlap[partition][aid, horizon] == [r["point_id"] for r in own]
            separate = sorted(separate, key=lambda r: r["entry_date"])
            adjacent_overlap = [{"earlier": a["point_id"], "later": b["point_id"],
                                 "earlier_exit": a["exit_date"], "later_entry": b["entry_date"]}
                                for a, b in zip(separate, separate[1:]) if b["entry_date"] < a["exit_date"]]
            appendix.append({"asset_id": aid, "horizon": horizon,
                             "raw_mature_feature_eligible": len(candidates),
                             "partition_internal_sum": len(separate),
                             "merged_greedy_nonoverlap": len(chosen),
                             "merged_point_ids": [r["point_id"] for r in chosen],
                             "cross_partition_overlap_pairs": adjacent_overlap,
                             "effective_independent_n": None})
    result = {"audit_id": "PHASE3_OUTCOME_PATH_INTEGRITY_QA_V005",
              "reviewed_at": datetime.now(timezone.utc).isoformat(), "status": "PASS",
              "scope": "Root-authorized independent future-label QA after both partitions locked; no research artifact modified, no rule or forecast changed.",
              "RAW OBSERVATIONS": {"selected_decision_points": 2704,
                                   "feature_eligible_mature_12m": sum(r["horizon"] == "12m" for r in merged),
                                   "revealed_horizon_labels": check_counts["revealed_horizon_labels"],
                                   "scalar_checks": sum(v for k, v in check_counts.items() if k != "revealed_horizon_labels"),
                                   "prior_immutable_file_hashes": len(prior["immutable_file_hashes"]),
                                   "new_predictions_or_investment_tests": 0},
              "EFFECTIVE SAMPLE ASSESSMENT": {"n_effective": None,
                  "notes": ["The same start contributes six related labels.",
                            "Market/sector/global dependence and overlapping returns remain.",
                            "Merged greedy nonoverlap is an appendix, not an effective-N estimator.",
                            "Conditional provider TR and original-vintage/survivor limitations remain."]},
              "check_counts": dict(check_counts), "numeric_errors": errors,
              "hash_and_local_order_checks": "PASS; local hashes/times are not trusted external timestamps or true future-OOS proof.",
              "prior_immutable_changed": prior_changes,
              "fixed_return_method": "Independent shares/cash entitlement ledger; initial buy cost and terminal stock-only sell cost; primary label and comparable net NAV kept separate.",
              "merged_nonoverlap_appendix": appendix,
              "source_hashes": {"allA": sha(feature_path), "development_labels": sha(BASE / "labels/development.v001.json"),
                                "holdout_labels": sha(BASE / "labels/holdout.v001.json"), "audit_code": sha(__file__)}}
    write_once("OUTCOME_PATH_INTEGRITY_QA.v005.json", result)
    print(json.dumps({"status": "PASS", "check_counts": dict(check_counts),
                      "merged_nonoverlap_totals": {h: sum(r["merged_greedy_nonoverlap"] for r in appendix if r["horizon"] == h) for h in ["12m", "24m"]},
                      "partition_internal_totals": {h: sum(r["partition_internal_sum"] for r in appendix if r["horizon"] == h) for h in ["12m", "24m"]}}))


if __name__ == "__main__":
    main()
