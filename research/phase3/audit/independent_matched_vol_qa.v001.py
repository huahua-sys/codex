"""Independent post-panel comparator QA; all original experiments retained."""
from pathlib import Path
from datetime import datetime, timezone
import collections
import hashlib
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "research/phase3"
AD = BASE / "audit"
EQUITIES = {"Broad", "Growth", "Technology", "Semiconductor", "Financials_Banks",
            "Industrials", "Consumer", "Healthcare", "Energy_Resources", "Utilities"}
VARS = {"H-P3-TREND": ("features", "trend_group", "POSITIVE", "NONPOSITIVE"),
        "H-P3-DRAWDOWN": ("features", "drawdown_group", "LARGE_DRAWDOWN", "OTHER"),
        "H-P3-VOL": ("features", "vol_group", "HIGH", "NOT_HIGH"),
        "H-P3-CREDIT": ("credit", "group", "TIGHTENING", "NOT_TIGHTENING")}


def read(p):
    return json.loads(Path(p).read_text())


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def klass(p):
    return "EQUITY" if p["industry"] in EQUITIES else "TREASURY_DURATION" if p["industry"].startswith("Treasury_") else p["industry"]


def interval(cells, key):
    if not cells:
        return {"mean": None, "ci95": None, "blocks": 0}
    block = collections.defaultdict(list)
    for row in cells:
        block[(row["year"] - 2000) // 2].append(row[key])
    keys = sorted(block)
    sums, n = np.asarray([sum(block[k]) for k in keys]), np.asarray([len(block[k]) for k in keys])
    draws = np.random.default_rng(20261009).integers(0, len(keys), size=(500, len(keys)))
    estimates = sums[draws].sum(axis=1) / n[draws].sum(axis=1)
    return {"mean": float(np.mean([c[key] for c in cells])),
            "ci95": np.quantile(estimates, [.025, .975]).tolist(), "blocks": len(keys)}


def main():
    feature = {p["point_id"]: p for p in read(BASE / "features/decision_points.v001.json")["points"]}
    rows = []
    for partition in ["development", "holdout"]:
        for point in read(BASE / f"labels/{partition}.v001.json")["points"]:
            p = feature[point["point_id"]]
            for h, label in point["horizons"].items():
                if not p["feature_eligible"] or label["status"] != "REVEALED" or h not in ["12m", "24m"]:
                    continue
                groups = {}
                for name, (section, key, positive, negative) in VARS.items():
                    value = p[section].get(key)
                    if name == "H-P3-CREDIT" and (p["market"] != "US" or p["credit"]["status"] != "KNOWN_AT_T"):
                        value = None
                    groups[name] = 1 if value == positive else 0 if value == negative else None
                b = label["benchmark"]
                rows.append({"point_id": point["point_id"], "asset_id": p["asset_id"],
                             "year": p["year"], "quarter": p["calendar_quarter"], "horizon": h,
                             "stratum": (p["market"], p["currency"], klass(p), label["return_basis"]),
                             "groups": groups, "net": label["net_return"], "mdd": label["max_drawdown"],
                             "entry": label["entry_date"], "exit": label["exit_date"],
                             "spy_residual": b["difference_net_return"] if b["status"] == "SAME_EXECUTION" else None})
    counts, errors = collections.Counter(), []

    def cmp(observed, expected, what):
        counts["scalar_fields"] += 1
        if observed is None or expected is None:
            if observed != expected:
                errors.append({"what": what, "observed": observed, "expected": expected})
        elif not math.isclose(float(observed), float(expected), rel_tol=2e-9, abs_tol=3e-11):
            errors.append({"what": what, "observed": observed, "expected": expected})

    def compare_interval(recorded, cells, key, context):
        calculated = interval(cells, key)
        cmp(recorded["mean"], calculated["mean"], context + ":mean")
        assert recorded["blocks"] == calculated["blocks"]
        if calculated["ci95"] is None:
            assert recorded["ci95"] is None
        else:
            for i in range(2):
                cmp(recorded["ci95"][i], calculated["ci95"][i], context + ":interval")

    def make_cells(candidates, variable):
        grouped = collections.defaultdict(lambda: {0: [], 1: []})
        for row in candidates:
            if row["groups"][variable] is not None:
                grouped[row["quarter"]][row["groups"][variable]].append(row)
        cells = []
        for q, g in sorted(grouped.items()):
            if not g[0] or not g[1]:
                continue
            cells.append({"quarter": q, "year": int(q[:4]),
                          "n_group1": len(g[1]), "n_group0": len(g[0]),
                          "ids1": [r["point_id"] for r in g[1]], "ids0": [r["point_id"] for r in g[0]],
                          "return_difference": float(np.mean([r["net"] for r in g[1]]) - np.mean([r["net"] for r in g[0]])),
                          "mdd_difference": float(np.mean([r["mdd"] for r in g[1]]) - np.mean([r["mdd"] for r in g[0]])),
                          "entry": min(r["entry"] for r in g[0] + g[1]),
                          "exit": max(r["exit"] for r in g[0] + g[1]),
                          "point_ids": [r["point_id"] for r in g[0] + g[1]],
                          "spy1": [r["spy_residual"] for r in g[1] if r["spy_residual"] is not None],
                          "spy0": [r["spy_residual"] for r in g[0] if r["spy_residual"] is not None]})
        return grouped, cells

    matched = read(BASE / "matched/RESULTS.v001.json")
    prereg = read(BASE / "matched/PREREGISTRATION.v001.json")
    mlock = read(BASE / "matched/RESULTS.lock.v001.json")
    assert mlock["result_sha256"] == sha(BASE / "matched/RESULTS.v001.json")
    assert mlock["registered_sha256"] == sha(BASE / "matched/PREREGISTRATION.v001.json")
    assert all(sha(ROOT / name) == digest for name, digest in prereg["sources"].items())
    assert datetime.fromisoformat(prereg["registered_at"]) <= datetime.fromisoformat(mlock["completed_at"])
    matching = {}
    for result in matched["results"]:
        st, variable, h = tuple(result["stratum"]), result["variable"], result["horizon"]
        grouped, cells = make_cells([r for r in rows if r["stratum"] == st and r["horizon"] == h], variable)
        matching[st, variable, h] = cells
        assert result["both_group_quarters"] == len(cells)
        assert result["matched_raw_observations"] == sum(c["n_group1"] + c["n_group0"] for c in cells)
        assert result["RAW_OBSERVATIONS"] == sum(len(g[0]) + len(g[1]) for g in grouped.values())
        assert result["missing_opposite_group_quarters"] == sum(not g[0] or not g[1] for g in grouped.values())
        compare_interval(result["return_contrast"], cells, "return_difference", "matched_return")
        compare_interval(result["gross_MDD_contrast"], cells, "mdd_difference", "matched_mdd")
        residual = []
        if st[0] == "US" and st[2] == "EQUITY":
            for cell in cells:
                if cell["spy1"] and cell["spy0"]:
                    residual.append({**cell, "return_difference": float(np.mean(cell["spy1"]) - np.mean(cell["spy0"]))})
        compare_interval(result["SPY_residual_contrast"], residual, "return_difference", "matched_spy_residual")
        recorded_cells = [c for c in matched["matched_cells"] if tuple(c["stratum"]) == st and c["variable"] == variable and c["horizon"] == h]
        assert len(recorded_cells) == len(cells)
        for c, rec in zip(cells, recorded_cells):
            assert c["quarter"] == rec["quarter"] and c["ids1"] == rec["point_ids_group1"] and c["ids0"] == rec["point_ids_group0"]
            cmp(rec["return_difference"], c["return_difference"], "matched_quarter_return")
            cmp(rec["mdd_difference"], c["mdd_difference"], "matched_quarter_mdd")
        counts["matched_comparison_slots"] += 1
    vreg = read(BASE / "vol_falsification/PREREGISTRATION.v001.json")
    vol = read(BASE / "vol_falsification/RESULTS.v001.json")
    vlock = read(BASE / "vol_falsification/RESULTS.lock.v001.json")
    assert vlock["results_sha256"] == sha(BASE / "vol_falsification/RESULTS.v001.json")
    assert vlock["preregistration_sha256"] == sha(BASE / "vol_falsification/PREREGISTRATION.v001.json")
    assert all(sha(ROOT / name) == digest for name, digest in vreg["sources"].items())
    assert len(vol["comparisons"]) == 88 and len(vol["nonoverlap"]) == 2
    assert len(vreg["assets"]) == 10 and len(vreg["variants"]) == 11
    all_cells = {}
    for result in vol["comparisons"]:
        h, variant, era = result["horizon"], result["variant"], result["era"]
        omitted = variant[5:] if variant.startswith("OMIT_") else None
        candidates = [r for r in rows if r["asset_id"] in vreg["assets"] and r["asset_id"] != omitted and r["horizon"] == h and
                      (era == "ALL" or int(era[:4]) <= r["year"] <= int(era[5:]))]
        _, cells = make_cells(candidates, "H-P3-VOL")
        assert result["both_group_quarters"] == len(cells) and result["n_raw"] == sum(c["n_group0"] + c["n_group1"] for c in cells)
        assert len(cells) == len(result["cells"])
        for c, rec in zip(cells, result["cells"]):
            assert c["quarter"] == rec["quarter"] and c["point_ids"] == rec["point_ids"]
            assert c["entry"] == rec["entry"] and c["exit"] == rec["exit"]
            cmp(rec["return_difference"], c["return_difference"], "vol_quarter_return")
            cmp(rec["mdd_difference"], c["mdd_difference"], "vol_quarter_mdd")
        compare_interval(result["return_contrast"], cells, "return_difference", "vol_contrast")
        compare_interval(result["gross_MDD_contrast"], cells, "mdd_difference", "vol_mdd_contrast")
        if variant == "ALL" and era == "ALL":
            same = matching[("US", "USD", "EQUITY", "TOTAL_RETURN"), "H-P3-VOL", h]
            assert [c["quarter"] for c in same] == [c["quarter"] for c in cells]
            for a, b in zip(same, cells):
                cmp(a["return_difference"], b["return_difference"], "ALL_equals_matched_return")
                cmp(a["mdd_difference"], b["mdd_difference"], "ALL_equals_matched_mdd")
            all_cells[h] = cells
        counts["leave_one_or_era_slots"] += 1
    nonoverlap = []
    for result in vol["nonoverlap"]:
        chosen, last = [], None
        for cell in all_cells[result["horizon"]]:
            if last is None or cell["entry"] > last:
                chosen.append(cell)
                last = cell["exit"]
        assert [c["quarter"] for c in chosen] == [c["quarter"] for c in result["cells"]]
        assert len(chosen) == result["both_group_quarters"]
        assert all(b["entry"] > a["exit"] for a, b in zip(chosen, chosen[1:]))
        compare_interval(result["return_contrast"], chosen, "return_difference", "actual_global_nonoverlap_return")
        compare_interval(result["gross_MDD_contrast"], chosen, "mdd_difference", "actual_global_nonoverlap_mdd")
        nonoverlap.append({"horizon": result["horizon"], "quarter_count": len(chosen),
                           "raw_asset_rows": sum(c["n_group0"] + c["n_group1"] for c in chosen),
                           "independent_n": None, "strict_entry_after_previous_max_exit": True})
    prior = read(AD / "PRIOR_STATE.v001.json")
    changed = [p for p, obj in prior["immutable_file_hashes"].items() if not (ROOT / p).is_file() or sha(ROOT / p) != obj["sha256"]]
    operative = read(AD / "PRIOR_OPERATIVE_FRAMEWORK.v001.json")["operative_framework"]
    current = read(ROOT / "CURRENT_FRAMEWORK.json")
    operative_equal = {k: current[k] == v for k, v in operative.items()}
    assert not changed and all(operative_equal.values()) and not errors
    output = {"audit_id": "PHASE3_MATCHED_VOL_INDEPENDENT_QA_V007", "reviewed_at": datetime.now(timezone.utc).isoformat(),
              "status": "PASS", "RAW OBSERVATIONS": dict(counts),
              "EFFECTIVE SAMPLE ASSESSMENT": {"n_effective": None,
                  "notes": ["These controls reuse locked panel rows; no new independent samples or forecasts.",
                            "Same-quarter comparisons reduce common-date composition but do not match beta/sector risk or identify alpha.",
                            "Global nonoverlap rows remain correlated sectors and repeated economic regimes.",
                            "All10 leave-one variants and eras were retained; no preferred universe, threshold or strategy chosen."]},
              "strict_nonoverlap": nonoverlap, "all_equals_prior_matched": True,
              "paired_benchmark_definition": "Only US EQUITY same-execution SPY residuals; fixed component net MDD is not mixed with primary gross MDD. Residual is not risk-matched alpha.",
              "old_immutable_hash_count": len(prior["immutable_file_hashes"]), "old_immutable_changed": changed,
              "operative_fields_equal": operative_equal, "numeric_errors": errors,
              "audit_code_sha256": sha(__file__)}
    with (AD / "MATCHED_VOL_QA.v007.json").open("x") as handle:
        json.dump(output, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
    print(json.dumps({"status": "PASS", "counts": dict(counts), "nonoverlap": nonoverlap,
                      "immutable_changes": changed, "operative_equal": all(operative_equal.values())}))


if __name__ == "__main__":
    main()
