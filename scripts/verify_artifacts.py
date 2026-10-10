#!/usr/bin/env python3
"""Verify ROUND_001 initialization only; this does not validate investment hypotheses.

The fixed 15 designs and zero empirical counts apply to this first-round snapshot.
Revise the acceptance rules before using this script for later research rounds.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
errors = []
checks = []


def check(name, ok, detail):
    checks.append({"check": name, "passed": bool(ok), "detail": detail})
    if not ok:
        errors.append(name + ": " + str(detail))


required = [
    "README.md", "AGENTS.md", "DATA_INVENTORY.md", "PROJECT_AUDIT.md",
    "RESEARCH_CONSTITUTION.md", "HYPOTHESIS_REGISTRY.md", "RESEARCH_LEDGER.md",
    "INVESTMENT_PHILOSOPHY.md", "CANDIDATE_PRINCIPLES.md", "FAILED_HYPOTHESES.md",
    "OPEN_QUESTIONS.md", "CURRENT_FRAMEWORK.json", "CHANGELOG.md", "EPISODE_INDEX.md",
    "PREDICTION_LEDGER.md", "RESEARCH_ROADMAP.md", "research/status/LATEST.md",
    "research/replays/ROUND_001_BLOCKED.md", "research/episode_library/ROUND_001_PLAN.md",
    "research/protocols/HISTORICAL_REPLAY.md", "research/protocols/DATA_CONTRACT.md",
    "research/protocols/INDUSTRY_FRAMEWORKS.md", "research/protocols/DECISION_FRAMEWORK.md",
    "research/protocols/STATISTICAL_VALIDATION.md", "research/audit/INITIAL_SCAN.json",
    "data/manifests/SOURCE_MANIFEST.json", "research/audit/INDEPENDENT_REVIEW.md",
    "research/templates/EPISODE_TEMPLATE.md", "research/templates/PREDICTION_TEMPLATE.md",
    "research/templates/PREREGISTRATION_TEMPLATE.md", "research/templates/FAILED_HYPOTHESIS_TEMPLATE.md",
]
missing = [x for x in required if not (ROOT / x).is_file()]
check("required_artifacts", not missing, missing)

parsed = {}
for path in sorted(ROOT.rglob("*.json")):
    if path.name == "ARTIFACT_VERIFICATION.json":
        continue
    try:
        parsed[str(path.relative_to(ROOT))] = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        errors.append(str(path.relative_to(ROOT)) + ": " + str(exc))
check("json_parse", len(parsed) == len(list(ROOT.rglob("*.json"))) - int((ROOT / "research/audit/ARTIFACT_VERIFICATION.json").exists()), sorted(parsed))

framework = parsed.get("CURRENT_FRAMEWORK.json", {})
fields = ["framework_version", "last_updated", "validated_principles", "candidate_principles",
          "active_hypotheses", "known_failure_modes", "regime_rules", "industry_specific_rules",
          "signals_to_monitor", "sell_signals", "risk_signals", "price_in_checks", "open_questions",
          "data_limitations", "recent_changes"]
check("framework_required_fields", all(x in framework for x in fields), [x for x in fields if x not in framework])
check("no_unearned_validated_principles", framework.get("validated_principles") == [], framework.get("validated_principles"))
check("no_unregistered_active_hypotheses", framework.get("active_hypotheses") == [], framework.get("active_hypotheses"))
check("live_signals_disabled", framework.get("live_signal_generation_enabled") is False,
      framework.get("live_signal_generation_enabled"))
operational_arrays = ["regime_rules", "industry_specific_rules", "signals_to_monitor", "sell_signals", "risk_signals", "price_in_checks"]
check("no_untested_operational_signals", all(framework.get(k) == [] for k in operational_arrays), operational_arrays)

candidate_files = sorted((ROOT / "research/candidate_principles").glob("CP-*.md"))
experiment_files = sorted((ROOT / "research/experiments").glob("EXP-*.md"))
candidate_ids = {re.search(r"CP-\d{3}", p.name).group() for p in candidate_files}
experiment_ids = {re.search(r"EXP-\d{3}", p.name).group() for p in experiment_files}
expected_cp = {f"CP-{i:03}" for i in range(1, 16)}
expected_exp = {f"EXP-{i:03}" for i in range(1, 16)}
check("candidate_records", candidate_ids == expected_cp and len(candidate_files) == 15, sorted(candidate_ids))
check("experiment_records", experiment_ids == expected_exp and len(experiment_files) == 15, sorted(experiment_ids))
entries = framework.get("candidate_principles", [])
check("framework_candidate_count", len(entries) == 15, len(entries))
check("framework_candidate_ids", {x.get("id") for x in entries} == expected_cp, [x.get("id") for x in entries])
check("all_candidates_untested", all(x.get("empirical_evidence_count") == 0 and x.get("discovery_origin") == "MASTER_PROMPT_DERIVED_UNTESTED" for x in entries), "Zero evidence and explicit origin required")
check("candidate_ranking_unique", sorted(x.get("research_priority_rank", 0) for x in entries) == list(range(1, 16)), [x.get("research_priority_rank") for x in entries])
score_errors = []
for entry in entries:
    g = entry.get("heuristic_priority_components", {})
    try:
        values = [g[k] for k in ["research_value", "falsifiability", "data_burden", "compute_cost", "overfit_risk"]]
        expected_score = 3 * values[0] + 3 * values[1] - 2 * values[2] - values[3] - 2 * values[4]
        if any(not isinstance(v, int) or not 1 <= v <= 5 for v in values) or expected_score != entry.get("heuristic_priority_score"):
            score_errors.append(entry.get("id"))
    except KeyError:
        score_errors.append(entry.get("id"))
check("heuristic_scores_recompute", not score_errors, score_errors)
if not score_errors:
    sorted_entries = sorted(entries, key=lambda x: (-x["heuristic_priority_score"], -x["heuristic_priority_components"]["falsifiability"], x["heuristic_priority_components"]["data_burden"], x["heuristic_priority_components"]["compute_cost"], x["heuristic_priority_components"]["overfit_risk"], x["id"]))
    check("heuristic_tie_break_order", [x["research_priority_rank"] for x in sorted_entries] == list(range(1, 16)), [x["id"] for x in sorted_entries])
registry = (ROOT / "HYPOTHESIS_REGISTRY.md").read_text(encoding="utf-8") if (ROOT / "HYPOTHESIS_REGISTRY.md").exists() else ""
registered_ids = re.findall(r"^\|\s*(H-\d{3})\s*\|", registry, flags=re.MULTILINE)
check("registry_hypotheses_15", len(registered_ids) == 15 and set(registered_ids) == {f"H-{i:03}" for i in range(1, 16)}, registered_ids)
bad_refs = []
for entry in entries:
    for field in ["record_path", "experiment_path"]:
        if not (ROOT / entry.get(field, "__MISSING__")).is_file():
            bad_refs.append({"id": entry.get("id"), "field": field, "path": entry.get(field)})
check("candidate_framework_paths", not bad_refs, bad_refs)

metrics = framework.get("research_counts", {})
zero_keys = ["empirical_sources", "completed_replays", "locked_predictions", "revealed_outcomes",
             "completed_statistical_experiments", "replay_discovered_candidates", "validated_principles"]
check("empirical_counts_zero", all(metrics.get(k) == 0 for k in zero_keys), metrics)
check("round_is_blocked", framework.get("current_round", {}).get("status") == "BLOCKED_DATA_REQUIRED", framework.get("current_round"))

source_path = ROOT / "sources/Codex_Investment_Research_Lab_Master_Prompt_v3.md"
expected_hash = "4d165d66b77d021325b9c96909433d044f10b818b8cf74796bfb205c2e0c13bb"
actual_hash = hashlib.sha256(source_path.read_bytes()).hexdigest() if source_path.exists() else None
check("instruction_source_hash", actual_hash == expected_hash, actual_hash)
scan = parsed.get("research/audit/INITIAL_SCAN.json", {})
check("initial_workspace_empty", scan.get("workspace", {}).get("files") == [] and scan.get("workspace", {}).get("errors") == [], "Pre-existing workspace contains no observed files or scan errors")
check("prompt_not_empirical_source", parsed.get("data/manifests/SOURCE_MANIFEST.json", {}).get("empirical_source_count") == 0, "Generated artifacts are not historical observations")

broken = []
link_count = 0
for path in sorted(ROOT.rglob("*.md")):
    if "sources" in path.relative_to(ROOT).parts:
        continue
    content = path.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", content):
        target = target.strip().strip("<>")
        if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        target = unquote(target.split("#", 1)[0])
        if not target:
            continue
        link_count += 1
        if not (path.parent / target).exists():
            broken.append({"from": str(path.relative_to(ROOT)), "target": target})
check("local_markdown_links", not broken, {"checked": link_count, "broken": broken})

json_blocks = 0
invalid_blocks = []
for path in sorted(ROOT.rglob("*.md")):
    if "sources" in path.relative_to(ROOT).parts:
        continue
    for index, block in enumerate(re.findall(r"```json\s*\n(.*?)\n```", path.read_text(encoding="utf-8"), flags=re.DOTALL), start=1):
        json_blocks += 1
        try:
            json.loads(block)
        except ValueError as exc:
            invalid_blocks.append({"file": str(path.relative_to(ROOT)), "block": index, "error": str(exc)})
check("fenced_json_valid", not invalid_blocks, {"checked": json_blocks, "invalid": invalid_blocks})

report = {"observed_at": datetime.now(timezone.utc).isoformat(), "scope": "ROUND_001 initialization: artifact completeness, source provenance and internal consistency only; no empirical investment validation. Fixed zero empirical counts do not apply to later rounds.",
          "status": "PASS" if not errors else "FAIL", "checks": checks, "errors": errors}
report_path = ROOT / "research/audit/ARTIFACT_VERIFICATION.json"
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": report["status"], "checks": len(checks), "markdown_links_checked": link_count,
                  "errors": errors, "report_path": str(report_path)}, ensure_ascii=False))
sys.exit(1 if errors else 0)
