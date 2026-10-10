"""Neutral calendar sampling: never inspect prices or future returns."""
from datetime import date


def select_episodes(universe, cutoff_dates, round_id="ROUND_002"):
    episodes = []
    for cutoff in sorted(set(cutoff_dates)):
        date.fromisoformat(cutoff)
        for asset in sorted(universe, key=lambda a: a["asset_id"]):
            if asset.get("inception_date", "0001-01-01") > cutoff:
                raise ValueError("universe instrument not yet in existence: " + asset["asset_id"])
            episodes.append({"episode_id": f"{round_id}-{len(episodes)+1:03d}", "asset_id": asset["asset_id"], "market": asset["market"], "cutoff_at": cutoff + "T23:59:59+00:00", "cutoff_timezone": "UTC", "sampling_weight": 1.0, "sample_role": "EXPLORATORY_FIXED_CALENDAR", "selection_basis": "calendar_grid_x_frozen_universe"})
    return {"round_id": round_id, "selection_method": "FIXED_CALENDAR_FULL_GRID", "selection_inspects_outcomes": False, "universe": universe, "cutoff_dates": sorted(set(cutoff_dates)), "episodes": episodes, "missing_policy": "KEEP_ROW_AND_REPORT_UNRESOLVED_DATA_NO_REPLACEMENT"}
