"""Independent distributions and selected block-interval QA; no optimization."""
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
GROUPS = {"H-P3-TREND": ("features", "trend_group", "POSITIVE", "NONPOSITIVE"),
          "H-P3-DRAWDOWN": ("features", "drawdown_group", "LARGE_DRAWDOWN", "OTHER"),
          "H-P3-VOL": ("features", "vol_group", "HIGH", "NOT_HIGH"),
          "H-P3-CREDIT": ("credit", "group", "TIGHTENING", "NOT_TIGHTENING")}


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def kinds(point):
    year = point["year"]
    era = "2000-2009" if year < 2010 else "2010-2019" if year < 2020 else "2020-2025"
    scope = ("PREREGISTERED_CROSS_TIME_RECONSTRUCTION" if year <= 2015 else
             "DEVELOPMENT_CONTEXT_ALREADY_EXPOSED" if year <= 2023 else
             "COMPUTATIONAL_LATER_LABEL_HOLDOUT_WITH_PRIOR_PATH_EXPOSURE")
    names = [("ALL", "ALL"), ("era", era), ("validation_scope", scope),
             ("prior_exposure", point["prior_exposure"])]
    for key in ["asset_id", "market", "industry"]:
        names.extend([(key, point[key]), (key + "_x_era", point[key] + "|" + era)])
    if point["quarter"] == 4:
        names.append(("fixed_Q4", "Q4"))
    return names


def summary(rows, benchmark=None):
    values = [r["net"] if benchmark is None else r["bench"].get(benchmark) for r in rows]
    a = np.asarray([v for v in values if v is not None], dtype=float)
    names = ["mean", "median", "win_rate", "p25", "p75", "worst_decile_p10",
             "best_decile_p90", "mean_max_drawdown", "worst_max_drawdown"]
    out = {"n_raw": int(len(a)), **{n: None for n in names}}
    if len(a):
        out.update(mean=float(np.mean(a)), median=float(np.median(a)),
                   win_rate=float(np.mean(a > 0)), p25=float(np.quantile(a, .25)),
                   p75=float(np.quantile(a, .75)), worst_decile_p10=float(np.quantile(a, .1)),
                   best_decile_p90=float(np.quantile(a, .9)))
        if benchmark is None:
            dd = np.asarray([r["mdd"] for r in rows], dtype=float)
            out.update(mean_max_drawdown=float(dd.mean()), worst_max_drawdown=float(dd.min()))
    return out


def dates(rows, benchmark=None):
    cells = collections.defaultdict(list)
    for r in rows:
        value = r["net"] if benchmark is None else r["bench"].get(benchmark)
        if value is not None:
            cells[r["quarter"]].append(value)
    return {q: float(np.mean(values)) for q, values in cells.items()}


def interval(a, b, design, benchmark=None):
    left, right = dates(a, benchmark), dates(b, benchmark)
    blocks = sorted({(int(q[:4]) - 2000) // 2 for q in set(left) | set(right)})
    if not left or not right:
        return None
    ls, ln, rs, rn = [], [], [], []
    for block in blocks:
        lv = [v for q, v in left.items() if (int(q[:4]) - 2000) // 2 == block]
        rv = [v for q, v in right.items() if (int(q[:4]) - 2000) // 2 == block]
        ls.append(sum(lv)); ln.append(len(lv)); rs.append(sum(rv)); rn.append(len(rv))
    draws = np.random.default_rng(design["bootstrap_seed"]).integers(
        0, len(blocks), size=(design["bootstrap_reps"], len(blocks)))
    with np.errstate(divide="ignore", invalid="ignore"):
        l = np.asarray(ls)[draws].sum(axis=1) / np.asarray(ln)[draws].sum(axis=1)
        r = np.asarray(rs)[draws].sum(axis=1) / np.asarray(rn)[draws].sum(axis=1)
    difference = l - r
    good = difference[np.isfinite(difference)]
    return np.quantile(good, [.025, .975]).tolist() if len(good) else None


def main():
    design = read(BASE / "design.v001.json")
    features = {p["point_id"]: p for p in read(BASE / "features/decision_points.v001.json")["points"]}
    counts, errors, records = collections.Counter(), [], []

    def compare(observed, expected, context):
        counts["scalar_fields"] += 1
        if observed is None or expected is None:
            if observed != expected:
                errors.append({"context": context, "observed": observed, "independent": expected})
        elif not math.isclose(float(observed), float(expected), rel_tol=2e-9, abs_tol=3e-11):
            errors.append({"context": context, "observed": observed, "independent": expected})

    for partition in ["development", "holdout"]:
        label = read(BASE / f"labels/{partition}.v001.json")
        stats = read(BASE / f"analysis/{partition}.results.v001.json")
        bucket, selected = collections.defaultdict(list), collections.Counter()
        eligible_rows = []
        for point in label["points"]:
            p = features[point["point_id"]]
            for horizon, value in point["horizons"].items():
                for kind, name in kinds(p):
                    selected[kind, name, horizon] += 1
                if not p["feature_eligible"] or value["status"] != "REVEALED":
                    continue
                benchmark = {"OWN_PASSIVE": 0.0}
                b = value["benchmark"]
                if b["status"] == "SAME_EXECUTION":
                    benchmark["PAIRED_ASSET_BENCHMARK"] = b["difference_net_return"]
                for name, b in value["fixed_allocation_benchmarks"].items():
                    if b["status"] == "SAME_EXECUTION":
                        benchmark[name] = b["difference_net_return"]
                row = {"net": value["net_return"], "mdd": value["max_drawdown"],
                       "bench": benchmark, "quarter": p["calendar_quarter"], "p": p,
                       "horizon": horizon}
                eligible_rows.append(row)
                for variable, (section, key, yes, no) in GROUPS.items():
                    group = p[section].get(key)
                    if variable == "H-P3-CREDIT" and (p["market"] != "US" or p["credit"]["status"] != "KNOWN_AT_T"):
                        group = None
                    if group not in [yes, no]:
                        continue
                    g = int(group == yes)
                    for kind, name in kinds(p):
                        bucket[kind, name, horizon, variable, g].append(row)
        for item in stats["all_results"]:
            prefix = item["cohort_type"], item["cohort"], item["horizon"], item["variable"]
            groups = [bucket.get((*prefix, g), []) for g in [1, 0]]
            compare(item["selected_point_count"], selected[prefix[:3]], f"selected:{prefix}")
            compare(item["excluded_feature_or_label_or_variable"], selected[prefix[:3]] - sum(map(len, groups)), f"excluded:{prefix}")
            for index, key in enumerate(["group1", "group0"]):
                expected = summary(groups[index])
                for metric, value in expected.items():
                    compare(item[key][metric], value, f"distribution:{partition}:{prefix}:{key}:{metric}")
            ld, rd = dates(groups[0]), dates(groups[1])
            expected = float(np.mean(list(ld.values())) - np.mean(list(rd.values()))) if ld and rd else None
            compare(item["group_difference"]["difference_date_equal"], expected, f"date_equal:{partition}:{prefix}")
            for name, result in item["benchmarks"].items():
                for index, key in enumerate(["group1", "group0"]):
                    for metric, value in summary(groups[index], name).items():
                        compare(result[key][metric], value, f"benchmark_distribution:{partition}:{prefix}:{name}:{key}:{metric}")
                ld, rd = dates(groups[0], name), dates(groups[1], name)
                expected = float(np.mean(list(ld.values())) - np.mean(list(rd.values()))) if ld and rd else None
                compare(result["group_difference"]["difference_date_equal"], expected, f"benchmark_date_equal:{partition}:{prefix}:{name}")
            # Independently recompute principal/market/industry/era/asset 12/24m intervals.
            if item["cohort_type"] in ["ALL", "market", "industry", "era", "asset_id"] and item["horizon"] in ["12m", "24m"]:
                expected = interval(groups[0], groups[1], design)
                observed = item["group_difference"]["ci95"]
                if expected is None:
                    compare(observed, expected, f"bootstrap_absence:{prefix}")
                else:
                    for i, bound in enumerate(expected):
                        compare(observed[i], bound, f"bootstrap:{partition}:{prefix}:{i}")
                    counts["bootstrap_intervals"] += 1
            counts["comparison_slots"] += 1
        assert stats["credit_interaction_gate"]["status"] == "NOT_RUN_GATE_FAILED" and not stats["credit_interaction"]
        if partition == "development":
            for entry, (lo, hi) in zip(stats["credit_interaction_gate"]["evidence"], [[2000, 2009], [2010, 2019]]):
                valid = [r for r in eligible_rows if r["horizon"] == "12m" and r["p"]["market"] == "US" and lo <= r["p"]["year"] <= hi and r["p"]["credit"]["status"] == "KNOWN_AT_T"]
                groups = [[r for r in valid if (r["p"]["credit"]["group"] == "TIGHTENING") == g] for g in [True, False]]
                date_sets = [dates(g) for g in groups]
                difference = float(np.mean(list(date_sets[0].values())) - np.mean(list(date_sets[1].values())))
                compare(entry["difference"], difference, f"credit_gate_difference:{lo}-{hi}")
                compare(entry["date_clusters"], len(set(date_sets[0]) | set(date_sets[1])), f"credit_gate_date_clusters:{lo}-{hi}")
                assert entry["group1_dates"] == len(date_sets[0]) and entry["group0_dates"] == len(date_sets[1])
            assert stats["credit_interaction_gate"]["evidence"][0]["difference"] * stats["credit_interaction_gate"]["evidence"][1]["difference"] < 0
        records.append({"partition": partition, "selected": len(label["points"]),
                        "eligible_mature12m": sum(r["horizon"] == "12m" for r in eligible_rows),
                        "comparison_slots": len(stats["all_results"]),
                        "interaction_gate": stats["credit_interaction_gate"]})
        del label, stats, bucket, eligible_rows
    assert not errors, errors[:10]
    result = {"audit_id": "PHASE3_INDEPENDENT_STATISTICAL_QA_V006",
              "reviewed_at": datetime.now(timezone.utc).isoformat(), "status": "PASS",
              "RAW OBSERVATIONS": {"locked_comparison_slots": counts["comparison_slots"],
                  "independent_scalar_checks": counts["scalar_fields"],
                  "independent_primary_and_group_block_intervals": counts["bootstrap_intervals"],
                  "new_investment_tests": 0},
              "EFFECTIVE SAMPLE ASSESSMENT": {"n_effective": None,
                  "explanation": "QA recalculations are not additional samples/tests of investment hypotheses. All slices reuse correlated dates/assets and overlapping returns; later partition only one two-year calendar block."},
              "partitions": records, "errors": errors, "code_sha256": sha(__file__),
              "method": ["All group sizes, mean/median/winrate/quantiles and gross MDD distributions independently recomputed.",
                         "All same-execution benchmark residual group distributions and marginal date-equal group differences recomputed.",
                         "Principal ALL/asset/market/industry/era 12m/24m intervals recomputed from fixed-seed joint two-year blocks.",
                         "Credit two-decade gate independently verifies sign reversal; interaction remains NOT_RUN_GATE_FAILED.",
                         "No replacement, tuning, filtering or independent-N inference from the QA count."]}
    with (AD / "STATISTICAL_QA.v006.json").open("x") as handle:
        json.dump(result, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
    print(json.dumps({"status": "PASS", "counts": dict(counts), "partitions": records}))


if __name__ == "__main__":
    main()
