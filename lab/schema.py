"""Input contracts and append-only artifact helpers, using Python's standard library."""
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

PIT_VERIFIED = {"VERIFIED", "VERIFIED_CONSERVATIVE_SESSION_LAG"}
PRICE_RECONSTRUCTED = "KNOWN_MARKET_OBSERVATION_RECONSTRUCTED"
ACTION_RECONSTRUCTED = "KNOWN_CORPORATE_ACTION_RECONSTRUCTED"
HORIZONS = {"1w": 5, "1m": 21, "3m": 63, "6m": 126, "12m": 252, "24m": 504}
CONTEXT_CATEGORIES = ("Macro", "Rates", "Inflation", "Credit", "Liquidity", "Valuation", "Breadth", "Industry", "Earnings", "Policy", "Capital Actions", "News", "Sentiment")


def timestamp(value):
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timezone is required: " + str(value))
    return dt.astimezone(timezone.utc)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_bytes(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def write_once(path, obj, text=False):
    """Create once. Re-running may verify an identical artifact, never replace one."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = obj.encode("utf-8") if text else json_bytes(obj)
    with path.open("xb") as out:
        out.write(payload)
    return sha256(path)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_records(records, cutoff=None, require_prices=False, allow_reconstructed_actions=False, require_publication=False):
    seen = set()
    for row in records:
        rid = row.get("record_id")
        if not rid or rid in seen:
            raise ValueError("missing/duplicate record_id: " + str(rid))
        seen.add(rid)
        if row.get("pit_status") not in PIT_VERIFIED and not (require_prices and row.get("pit_status") == PRICE_RECONSTRUCTED) and not (allow_reconstructed_actions and row.get("pit_status") == ACTION_RECONSTRUCTED):
            raise ValueError("ineligible PIT status: " + str(rid))
        at = timestamp(row["available_at"])
        if row.get("published_at") and timestamp(row["published_at"]) > at:
            raise ValueError("publication after claimed availability: " + str(rid))
        if require_publication and (not row.get("published_at") or not row.get("availability_evidence")):
            raise ValueError("verified context needs publication and availability evidence: " + str(rid))
        if cutoff is not None and at > timestamp(cutoff):
            raise ValueError("POST_CUTOFF record rejected: " + str(rid))
        if not row.get("source_id") or not row.get("source_sha256"):
            raise ValueError("missing provenance: " + str(rid))
        if row.get("date") and datetime.fromisoformat(row["date"]).date() > at.date():
            raise ValueError("observation after availability: " + str(rid))
        if require_prices:
            if not row.get("session_open_at") or not row.get("session_close_at"):
                raise ValueError("explicit session open and close timestamps required: " + str(rid))
            opening, closing = timestamp(row["session_open_at"]), timestamp(row["session_close_at"])
            if opening >= closing or closing > at:
                raise ValueError("full OHLC unavailable before session close: " + str(rid))
            for field in ("open", "high", "low", "close"):
                if not isinstance(row.get(field), (float, int)) or not math.isfinite(row[field]) or row[field] <= 0:
                    raise ValueError("invalid OHLC: " + str(rid))
            if row["high"] < max(row["open"], row["close"], row["low"]) or row["low"] > min(row["open"], row["close"], row["high"]):
                raise ValueError("inconsistent OHLC: " + str(rid))


def filter_records(records, cutoff, allow_reconstructed_prices=False, allow_reconstructed_actions=False):
    """Admin helper; Stage A instead rejects any unfiltered future row."""
    kept, rejected = [], []
    for row in records:
        reason = None
        if row.get("pit_status") not in PIT_VERIFIED and not (allow_reconstructed_prices and row.get("pit_status") == PRICE_RECONSTRUCTED) and not (allow_reconstructed_actions and row.get("pit_status") == ACTION_RECONSTRUCTED):
            reason = "POINT_IN_TIME_UNCERTAIN"
        elif not row.get("available_at"):
            reason = "POINT_IN_TIME_UNCERTAIN"
        elif timestamp(row["available_at"]) > timestamp(cutoff):
            reason = "KNOWN_ONLY_AFTER_T"
        (rejected if reason else kept).append({"record_id": row.get("record_id"), "reason": reason} if reason else row)
    return kept, rejected


def validate_input(packet):
    for field in ("episode_id", "asset_id", "market", "currency", "cutoff_at", "prices"):
        if field not in packet:
            raise ValueError("input missing " + field)
    timestamp(packet["cutoff_at"])
    validate_records(packet["prices"], packet["cutoff_at"], require_prices=True)
    validate_actions(packet.get("actions", []), packet["cutoff_at"])
    validate_records(packet.get("context", []), packet["cutoff_at"], require_publication=True)
    for row in packet["prices"]+packet.get("actions",[])+packet.get("context",[]):
        for field in ("asset_id", "market"):
            if field in row and row[field] != packet[field]:
                raise ValueError("record belongs to different " + field)
    if len({r["date"] for r in packet["prices"]}) != len(packet["prices"]):
        raise ValueError("duplicate price date")
    metadata = packet.get("metadata", {})
    basis = metadata.get("price_basis", "UNADJUSTED")
    if basis not in {"UNADJUSTED", "AS_REPORTED_OHLC_NO_ADJCLOSE"}:
        raise ValueError("Stage A requires unadjusted prices reconstructed by admin; future split-normalization is ineligible")
    if basis == "AS_REPORTED_OHLC_NO_ADJCLOSE" and not metadata.get("no_splits_in_analysis_interval_confirmed"):
        raise ValueError("as-reported OHLC requires explicit no-splits interval audit")
    if any(r.get("pit_status") == PRICE_RECONSTRUCTED for r in packet["prices"]) and metadata.get("original_vintage_status") != "NOT_ARCHIVED_PROVIDER_CORRECTIONS_POSSIBLE":
        raise ValueError("reconstructed prices require original-vintage limitation")
    if any(r.get("pit_status") == ACTION_RECONSTRUCTED for r in packet.get("actions", [])) and metadata.get("original_vintage_status") != "NOT_ARCHIVED_PROVIDER_CORRECTIONS_POSSIBLE":
        raise ValueError("reconstructed actions require original-vintage limitation")
    return packet


def validate_actions(actions, cutoff=None):
    validate_records(actions, cutoff, allow_reconstructed_actions=True)
    event_keys = set()
    for action in actions:
        if action.get("action_type") not in {"dividend", "split"} or not action.get("date"):
            raise ValueError("unsupported/missing corporate action")
        datetime.fromisoformat(action["date"])
        key = (action["date"], action["action_type"])
        if key in event_keys:
            raise ValueError("duplicate action economic event; consolidate source-priority before importing")
        event_keys.add(key)
        if action["action_type"] == "split":
            split_ratio(action)
        elif not isinstance(action.get("amount"), (float, int)) or not math.isfinite(action["amount"]) or action["amount"] < 0:
            raise ValueError("invalid dividend amount")


def split_ratio(action):
    ratio = float(action["ratio"])
    if not math.isfinite(ratio) or ratio <= 0:
        raise ValueError("split ratio must be positive")
    return ratio


def historical_wealth(prices, actions):
    """Past chain: actual known splits + dividend at ex-date close, no future actions."""
    by_date = {}
    for action in actions:
        by_date.setdefault(action["date"], []).append(action)
    ordered = sorted(prices, key=lambda r: r["date"])
    wealth, out = 1.0, []
    previous = None
    for row in ordered:
        if previous is not None:
            shares, dividend = 1.0, 0.0
            for a in by_date.get(row["date"], []):
                if a["action_type"] == "split":
                    shares *= split_ratio(a)
            for a in by_date.get(row["date"], []):
                if a["action_type"] == "dividend":
                    dividend += float(a["amount"]) * shares
                elif a["action_type"] != "split":
                    raise ValueError("unsupported corporate action")
            wealth *= (shares * row["close"] + dividend) / previous
        out.append((row, wealth))
        previous = row["close"]
    return out
