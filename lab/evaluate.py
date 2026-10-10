"""Stage B only: future outcomes after ALL Stage A locks are validated."""
import math
from pathlib import Path
from .schema import HORIZONS, read_json, sha256, split_ratio, timestamp, utc_now, validate_actions, validate_records, write_once


def evaluate_path(prices, actions, cutoff_at, n_sessions, action_coverage="UNKNOWN", return_basis="PRICE_ONLY", roundtrip_bps=50.0, tradability="UNVERIFIED"):
    """Enter next-session open; exit open after N complete market sessions.

    Total-return convention: distributions are reinvested at ex-date close;
    this is an economic-return convention, not a dividend payment-date strategy.
    Splits/dividends on entry ex-date occur before purchasing and are excluded.
    """
    if any(not r.get("session_open_at") for r in prices):
        raise ValueError("explicit session_open_at required; midnight cannot substitute executable open")
    rows = sorted([r for r in prices if timestamp(r["session_open_at"]) > timestamp(cutoff_at)], key=lambda r: timestamp(r["session_open_at"]))
    if len(rows) <= n_sessions:
        return {"status": "PENDING_HORIZON", "gross_return": None, "net_return": None, "max_adverse_excursion": None, "max_favorable_excursion": None, "max_drawdown": None}
    if return_basis == "TOTAL_RETURN" and action_coverage != "COMPLETE":
        return {"status": "UNRESOLVED_DATA", "reason": "company_action_coverage_unknown", "gross_return": None, "net_return": None, "max_adverse_excursion": None, "max_favorable_excursion": None, "max_drawdown": None}
    entry, exit_row = rows[0], rows[n_sessions]
    held = rows[:n_sessions + 1]
    by_date = {}
    for a in actions:
        if entry["date"] < a["date"] <= exit_row["date"]:
            by_date.setdefault(a["date"], []).append(a)
    shares = 1.0
    entry_price = entry["open"]
    # A daily-bar approximation; low/high order is unknown, so drawdown uses closes.
    low_paths, high_paths, close_paths = [0.0], [0.0], [1.0]
    for i, row in enumerate(held):
        dividends = 0.0
        if i:
            # All splits effective that session precede its ex-date cash entitlement.
            for a in by_date.get(row["date"], []):
                if a["action_type"] == "split":
                    shares *= split_ratio(a)
            if return_basis == "TOTAL_RETURN":
                dividends = sum(float(a["amount"]) * shares for a in by_date.get(row["date"], []) if a["action_type"] == "dividend")
        if i == n_sessions:
            # Exit at open before this session's close reinvestment; ex-date cash
            # entitlement is included when already held before ex-date.
            final_wealth = shares * row["open"] + dividends
            low_paths.append(final_wealth / entry_price - 1)
            high_paths.append(final_wealth / entry_price - 1)
            close_paths.append(final_wealth / entry_price)
            break
        low_paths.append((shares * row["low"] + dividends) / entry_price - 1)
        high_paths.append((shares * row["high"] + dividends) / entry_price - 1)
        close_paths.append((shares * row["close"] + dividends) / entry_price)
        if dividends:
            shares += dividends / row["close"]
    gross = final_wealth / entry_price - 1
    cost = float(roundtrip_bps) / 10000
    # Equal half-cost legs, not simple subtraction; fixed 50bp is an assumption.
    net = (1 + gross) * (1-cost/2) / (1+cost/2) - 1
    peak, drawdown = 1.0, 0.0
    for w in close_paths:
        peak = max(peak, w)
        drawdown = min(drawdown, w/peak - 1)
    return {"status": "REVEALED", "entry_date": entry["date"], "entry_open": entry_price,
        "exit_date": exit_row["date"], "exit_open": exit_row["open"], "sessions_held": n_sessions,
        "gross_return": gross, "net_return": net, "roundtrip_cost_bps_assumed": roundtrip_bps,
        "net_status": "HYPOTHETICAL_COST_MODEL" if tradability != "EXCHANGE_TRADED_ETF" else "ETF_ECONOMIC_TOTAL_RETURN_COST_ASSUMPTION",
        "return_basis": return_basis, "tradability": tradability,
        "dividend_convention": "ex-date cash entitlement reinvested at ex-date close; not payment-date executable strategy",
        "max_adverse_excursion": min(low_paths), "max_favorable_excursion": max(high_paths),
        "excursion_basis": "gross wealth daily OHLC approximation; cash entitlement included on exdate; exit session only exit open",
        "max_drawdown": drawdown, "max_drawdown_basis": "daily closes plus entry/exit open, not intraday path",
        "price_evidence_record_ids": [r["record_id"] for r in held],
        "action_evidence_record_ids": [a["record_id"] for a in actions if entry["date"] < a["date"] <= exit_row["date"]]}


def score_prediction(prediction, bundle):
    if not prediction.get("horizons"):
        return {"episode_id": prediction["episode_id"], "status": "UNRESOLVED_DATA", "reason": "exante_history_insufficient", "horizons": {}}
    prices, actions = bundle["prices"], bundle.get("actions", [])
    validate_records(prices, require_prices=True)
    validate_actions(actions)
    for row in prices+actions:
        for field in ("asset_id", "market"):
            if field in row and row[field] != prediction[field]:
                raise ValueError("outcome record belongs to different " + field)
    if len({r["date"] for r in prices}) != len(prices):
        raise ValueError("duplicate outcome price date")
    metadata = bundle.get("metadata", {})
    basis = metadata.get("price_basis")
    if basis not in {"UNADJUSTED", "AS_REPORTED_OHLC_NO_ADJCLOSE"}:
        raise ValueError("outcome price basis is missing or future adjusted")
    if basis != prediction.get("input_quality", {}).get("price_basis", "UNADJUSTED"):
        raise ValueError("outcome/frozen input price basis mismatch")
    if basis == "AS_REPORTED_OHLC_NO_ADJCLOSE" and not metadata.get("no_splits_in_analysis_interval_confirmed"):
        raise ValueError("outcome as-reported OHLC needs no-splits interval audit")
    if metadata.get("return_basis", prediction["return_basis"]) != prediction["return_basis"]:
        raise ValueError("outcome/frozen return basis mismatch")
    if any(r.get("pit_status") in {"KNOWN_MARKET_OBSERVATION_RECONSTRUCTED", "KNOWN_CORPORATE_ACTION_RECONSTRUCTED"} for r in prices+actions) and metadata.get("original_vintage_status") != "NOT_ARCHIVED_PROVIDER_CORRECTIONS_POSSIBLE":
        raise ValueError("outcome reconstructed data needs original-vintage limitation")
    result = {"episode_id": prediction["episode_id"], "asset_id": prediction["asset_id"], "cutoff_at": prediction["cutoff_at"], "status": "REVEALED", "revealed_at": utc_now(), "information_set": "KNOWN_ONLY_AFTER_T_OUTCOME_LABELS", "horizons": {}, "attribution": "UNRESOLVED_MECHANISM: price result cannot establish causal mechanism or distinguish correct logic from luck", "label_quality": metadata}
    for horizon, config in prediction["horizons"].items():
        r = evaluate_path(prices, actions, prediction["cutoff_at"], config["session_count"], bundle.get("action_coverage", "UNKNOWN"), prediction["return_basis"], prediction["cost_bps_roundtrip"], prediction["tradability"])
        if r["status"] == "REVEALED":
            net = r["net_return"]
            band = config["scenario_threshold_upper"]
            actual_scenario = "Bull" if net > band else "Bear" if net < -band else "Base"
            actual_up = int(net > 0)
            p = config["p_up_scoring_probability"]
            exposure = prediction["exposure"]
            # WAIT receives assumed zero cash return; record as a model outcome.
            cash = prediction["cash_alternative_return"]
            modeled_decision_return = net if exposure else cash
            r.update(actual_scenario=actual_scenario, actual_up=bool(actual_up),
                     direction_correct=(actual_up == int(p > .5)) if p != .5 else None,
                     direction_scoring_rule="p_up>.5 predicts up;p_up<.5 predicts nonpositive;p_up=.5 abstains",
                     predicted_up_probability=p, predicted_up_range=config["p_up_range"],
                     brier_score=(p-actual_up)**2,
                     scenario_brier_score=sum((s["scoring_probability"]-int(s["scenario"] == actual_scenario))**2 for s in config["scenarios"]),
                     model_expected_value=config["model_expected_value"], realized_return=net,
                     expected_value_status=config["expected_value_status"],
                     hypothetical_decision_return=modeled_decision_return,
                     cash_return_assumption=cash, cash_return_status=prediction["cash_alternative_status"],
                     benchmark_id=prediction["asset_id"], benchmark_return=net,
                     hypothetical_excess_vs_buy_and_hold=modeled_decision_return-net,
                     upside_capture=(modeled_decision_return/net if net > 0 else None),
                     downside_avoidance=(modeled_decision_return-net if net < 0 else None),
                     false_negative_missed_winner=(exposure == 0 and actual_scenario == "Bull"),
                     failed_long_signal=(exposure == 1 and actual_scenario != "Bull"),
                     outcome_role="PRICE_LABEL_AND_HYPOTHETICAL_EXPOSURE" if prediction["tradability"] != "EXCHANGE_TRADED_ETF" else "TOTAL_RETURN_LABEL_WITH_MODEL_COSTS")
        result["horizons"][horizon] = r
    statuses = {r["status"] for r in result["horizons"].values()}
    if "REVEALED" not in statuses:
        result["status"] = "UNRESOLVED_DATA" if "UNRESOLVED_DATA" in statuses else "PENDING_HORIZON"
    elif statuses != {"REVEALED"}:
        result["status"] = "PARTIALLY_REVEALED"
    return result


def summarize(evaluations):
    output = {"status": "DESCRIPTIVE_SMALL_DEPENDENT_SAMPLE_NOT_CONFIRMATORY", "episode_count": len(evaluations), "effective_independent_sample_warning": "Same date market episodes share shocks; long horizons overlap; count date clusters, not 24 independent bets", "horizons": {}}
    for h in HORIZONS:
        rows = [e["horizons"][h] for e in evaluations if h in e.get("horizons", {}) and e["horizons"][h]["status"] == "REVEALED"]
        predicted = [r for r in rows if r["direction_correct"] is not None]
        bins = []
        for low, high in ((0., .45), (.45, .55), (.55, 1.000001)):
            group = [r for r in rows if low <= r["predicted_up_probability"] < high]
            if group:
                n = len(group); phat = sum(r["actual_up"] for r in group)/n
                # Wilson interval is descriptive only, independence assumption fails here.
                z = 1.96; denom=1+z*z/n; center=(phat+z*z/(2*n))/denom; half=z*math.sqrt(phat*(1-phat)/n+z*z/(4*n*n))/denom
                bins.append({"bin": [low, min(high, 1.)], "n": n, "mean_predicted_probability": sum(r["predicted_up_probability"] for r in group)/n, "actual_up_fraction": phat, "naive_wilson_95_interval": [center-half, center+half], "interval_limitation": "dependent overlapping observations; interval understates uncertainty"})
        gains=[r for r in rows if r["net_return"]>0]; losses=[r for r in rows if r["net_return"]<0]
        upside_den = sum(r["net_return"] for r in gains)
        loss_den = -sum(r["net_return"] for r in losses)
        output["horizons"][h] = {"n_mature": len(rows), "n_direction_scored": len(predicted), "n_unresolved_or_pending": len(evaluations)-len(rows),
            "direction_accuracy": sum(r["direction_correct"] for r in predicted)/len(predicted) if predicted else None,
            "mean_brier_score": sum(r["brier_score"] for r in rows)/len(rows) if rows else None,
            "mean_scenario_brier_score": sum(r["scenario_brier_score"] for r in rows)/len(rows) if rows else None,
            "constant_05_brier": sum((.5-int(r["actual_up"]))**2 for r in rows)/len(rows) if rows else None,
            "constant_06_brier": sum((.6-int(r["actual_up"]))**2 for r in rows)/len(rows) if rows else None,
            "always_up_direction_accuracy": sum(r["actual_up"] for r in rows)/len(rows) if rows else None,
            "mean_realized_net_label": sum(r["net_return"] for r in rows)/len(rows) if rows else None,
            "mean_hypothetical_decision_return": sum(r["hypothetical_decision_return"] for r in rows)/len(rows) if rows else None,
            "mean_model_expected_value": sum(r["model_expected_value"] for r in rows)/len(rows) if rows else None,
            "upside_capture_ratio": sum(r["hypothetical_decision_return"] for r in gains)/upside_den if upside_den else None,
            "downside_avoidance_fraction": sum(r["downside_avoidance"] for r in losses)/loss_den if loss_den else None,
            "calibration_bins": bins, "calibration_conclusion": "INSUFFICIENT_INDEPENDENT_SAMPLE"}
    output["date_cluster_count"] = len({e["cutoff_at"] for e in evaluations if "cutoff_at" in e})
    return output


def verify_all_locks(output_dir, exante_dir, selection_path, preregistration_path):
    from .replay import implementation_hashes
    output_dir, exante_dir = Path(output_dir), Path(exante_dir)
    selected = read_json(selection_path)
    sentinel = read_json(output_dir / "all_locks.v001.json")
    hashes = {"selection_sha256": sha256(selection_path), "preregistration_sha256": sha256(preregistration_path), "input_manifest_sha256": sha256(exante_dir / "manifest.json"), "implementation_sha256": implementation_hashes()}
    expected = sorted(e["episode_id"] for e in selected["episodes"])
    if sentinel["episode_ids"] != expected or any(sentinel[k] != v for k,v in hashes.items()):
        raise ValueError("all-lock selection/input/preregistration mismatch")
    predictions = []
    manifest = read_json(exante_dir / "manifest.json")
    for eid in expected:
        lp=output_dir/"locks"/(eid+".v001.lock.json"); pp=output_dir/"predictions"/(eid+".v001.json"); mp=output_dir/"predictions"/(eid+".v001.md")
        lock=read_json(lp)
        inp=(exante_dir / lock["input_path"]).resolve()
        if exante_dir.resolve() not in inp.parents:
            raise ValueError("lock input path escapes")
        if sentinel["lock_sha256"][eid] != sha256(lp) or lock["prediction_sha256"] != sha256(pp) or lock["prediction_markdown_sha256"] != sha256(mp) or lock["input_sha256"] != sha256(inp) or manifest["inputs"][eid]["sha256"] != sha256(inp) or any(lock[k] != v for k,v in hashes.items()):
            raise ValueError("lock integrity failure " + eid)
        predictions.append((read_json(pp), sha256(lp), sha256(pp)))
    return predictions


def run_stage_b(output_dir, exante_dir, selection_path, preregistration_path, label_bundle_path):
    # Verify ALL locks before even opening future bundle.
    predictions=verify_all_locks(output_dir, exante_dir, selection_path, preregistration_path)
    labels=read_json(label_bundle_path)
    source_hash=sha256(label_bundle_path)
    evaluations=[]
    for p, lh, ph in predictions:
        path=Path(output_dir)/"labels"/(p["episode_id"]+".v001.json")
        if path.exists():
            old=read_json(path)
            if old.get("prediction_sha256") != ph or old.get("lock_sha256") != lh or old.get("source_bundle_sha256") != source_hash:
                raise ValueError("existing label mismatch; append version required")
            evaluations.append(old)
            continue
        if p["asset_id"] not in labels["assets"]:
            ev={"episode_id": p["episode_id"], "asset_id": p["asset_id"], "cutoff_at": p["cutoff_at"], "status":"UNRESOLVED_DATA", "reason":"missing_asset_label_bundle", "horizons": {}}
        else:
            ev=score_prediction(p, labels["assets"][p["asset_id"]])
        ev.update(prediction_sha256=ph, lock_sha256=lh, source_bundle_sha256=source_hash, evaluator_version="0.2.0")
        write_once(path,ev); evaluations.append(ev)
    summary=summarize(evaluations)
    sp=Path(output_dir)/"evaluation_summary.v001.json"
    if sp.exists():
        if read_json(sp)!=summary: raise ValueError("existing evaluation summary mismatch")
    else: write_once(sp,summary)
    return summary
