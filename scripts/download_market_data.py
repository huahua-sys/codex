#!/usr/bin/env python3
"""Small public quote acquisition. Administrator only; stdout contains metadata only.

Current Yahoo histories are NOT original historical vintages. Yahoo OHLC and cash
dividends are treated as split-normalized. Canonical reconstruction multiplies
pre-split records by all subsequently reported split ratios, with that choice
visible in provenance. This is never evidence of an original quote archive.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
UTC = dt.timezone.utc
ASSETS = {
    "SPY": ("SPY", "US", "USD", "ETF", "S&P 500", "America/New_York", "1993-01-29"),
    "HSI": ("^HSI", "HK", "HKD", "INDEX", "Hang Seng Index", "Asia/Hong_Kong", "1969-11-24"),
    "N225": ("^N225", "JP", "JPY", "INDEX", "Nikkei 225", "Asia/Tokyo", "1950-09-07"),
    "QQQ": ("QQQ", "US", "USD", "ETF", "Nasdaq 100", "America/New_York", "1999-03-10"),
    "SOXX": ("SOXX", "US", "USD", "ETF", "Semiconductors", "America/New_York", "2001-07-10"),
    "IEF": ("IEF", "US", "USD", "ETF", "7-10Y US Treasuries", "America/New_York", "2002-07-22"),
    "TLT": ("TLT", "US", "USD", "ETF", "20Y+ US Treasuries", "America/New_York", "2002-07-22"),
    "GLD": ("GLD", "US", "USD", "ETF", "Physical gold trust", "America/New_York", "2004-11-18"),
    "UUP": ("UUP", "US", "USD", "ETF", "US dollar futures basket", "America/New_York", "2007-02-20"),
    "BIL": ("BIL", "US", "USD", "ETF", "1-3 month US Treasury bills cash proxy", "America/New_York", "2007-05-25"),
    "XLK": ("XLK", "US", "USD", "ETF", "Technology", "America/New_York", "1998-12-16"),
    "XLF": ("XLF", "US", "USD", "ETF", "Financials", "America/New_York", "1998-12-16"),
    "XLE": ("XLE", "US", "USD", "ETF", "Energy", "America/New_York", "1998-12-16"),
    "XLI": ("XLI", "US", "USD", "ETF", "Industrials", "America/New_York", "1998-12-16"),
    "XLY": ("XLY", "US", "USD", "ETF", "Consumer discretionary", "America/New_York", "1998-12-16"),
    "XLV": ("XLV", "US", "USD", "ETF", "Healthcare", "America/New_York", "1998-12-16"),
    "XLU": ("XLU", "US", "USD", "ETF", "Utilities", "America/New_York", "1998-12-16"),
    "FEZ": ("FEZ", "US", "USD", "ETF", "Euro Stoxx 50 US-listed proxy", "America/New_York", "2002-10-15"),
    "CSI300": ("000300.SS", "CN", "CNY", "INDEX", "CSI 300", "Asia/Shanghai", "2005-04-08"),
    "SSE": ("000001.SS", "CN", "CNY", "INDEX", "Shanghai Composite", "Asia/Shanghai", "1991-07-15"),
    "CHINEXT": ("399006.SZ", "CN", "CNY", "INDEX", "ChiNext", "Asia/Shanghai", "2010-06-01"),
}
SPDR_SPLIT_SOURCE = "https://investors.statestreet.com/investor-news-events/press-releases/news-details/2025/State-Street-Investment-Management-Announces-Share-Splits-for-Five-Select-Sector-SPDR-ETFs/default.aspx"
SPLIT_EVIDENCE = {
    "BIL": {"date": "2017-11-30", "ratio": 0.5,
            "source_url": "https://www.streetinsider.com/Press%2BReleases/State%2BStreet%2BGlobal%2BAdvisors%2BAnnounces%2BETF%2BShare%2BSplits/13511071.html",
            "second_source_url": "https://www.feib.com.tw/upload/wealthmanagement/pdf/ETFs/Y444.pdf",
            "original_wire_url": "https://www.businesswire.com/news/home/20171115005810/en/",
            "source_quality": "ISSUER_AUTHORED_WIRE_REPUBLICATION_AND_ISSUER_FINANCIAL_HIGHLIGHTS_MIRROR",
            "legal_execution_date": "2017-11-29",
            "legal_date_vs_trading_unit_date": "Issuer financial highlights report Nov29 reverse split; issuer-authored wire says post-split trading effective Nov30"},
    "SOXX": {"date": "2024-03-07", "ratio": 3.0,
             "source_url": "https://www.sec.gov/Archives/edgar/data/1100663/000119312523298660/d611816d497.htm",
             "second_source_url": "https://www.ishares.com/us/literature/tax-information/form-8937-ishares-semiconductor-etf-3-6-2024.pdf"},
    **{asset: {"date": "2025-12-05", "ratio": 2.0, "source_url": SPDR_SPLIT_SOURCE}
       for asset in ["XLK", "XLE", "XLY", "XLU"]},
}

def iso(t):
    return t.astimezone(UTC).isoformat()

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def boundaries(day, market, timezone):
    """Observed-date schedule. Closes are conservative upper bounds, not calendars.

    Half-day close bounds deliberately remain the full-day close. This delays
    information and cannot make a daily OHLC record available before its close.
    Opens are normal-session opens; unusual opens/halts cannot be proven here.
    """
    tz = ZoneInfo(timezone)
    if market == "US": opening, closing = dt.time(9, 30), dt.time(16)
    elif market == "HK":
        opening = dt.time(10) if day < dt.date(2011, 3, 7) else dt.time(9, 30)
        closing = dt.time(16)
    elif market == "JP":
        opening = dt.time(9)
        closing = dt.time(15, 30) if day >= dt.date(2024, 11, 5) else dt.time(15)
    else: opening, closing = dt.time(9, 30), dt.time(15)
    start = dt.datetime.combine(day, opening, tz)
    end = dt.datetime.combine(day, closing, tz)
    available = dt.datetime.combine(day + dt.timedelta(days=1), dt.time(0), tz)
    return iso(start), iso(end), iso(available)

def acquire(asset_id, start, end, round_id, offline=False):
    symbol, market, currency, kind, underlying, timezone, inception = ASSETS[asset_id]
    source_id = "YAHOO_CHART_" + asset_id
    period1 = int(dt.datetime.fromisoformat(start).replace(tzinfo=UTC).timestamp())
    period2 = int((dt.datetime.fromisoformat(end).replace(tzinfo=UTC) + dt.timedelta(days=1)).timestamp())
    query = urllib.parse.urlencode({"period1": period1, "period2": period2,
                                   "interval": "1d", "events": "div,splits"})
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + urllib.parse.quote(symbol, safe="") + "?" + query
    requested_at = iso(dt.datetime.now(UTC))
    result = {"asset_id": asset_id, "symbol": symbol, "source_id": source_id,
              "source_url": url, "requested_at": requested_at}
    try:
        rawdir = ROOT / "data" / "raw" / round_id.lower() / "market"
        rawdir.mkdir(parents=True, exist_ok=True)
        rawpath = rawdir / (asset_id + ".yahoo.raw.json")
        if offline:
            body = rawpath.read_bytes()
            old_manifest = json.loads((ROOT / "data" / "manifests" / (round_id + "_MARKET_SOURCES.json")).read_text())
            old = old_manifest["sources"][asset_id]
            response_headers, retrieved_at = old.get("response_headers", {}), old["retrieved_at"]
            url = old["source_url"]
            result.update({"source_url": url, "offline_recanonicalization": True})
        else:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 InvestmentResearchLab/0.2 (public research)", "Accept": "application/json"})
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read()
                response_headers = {k: v for k, v in response.headers.items()
                                    if k.lower() in {"content-type", "date", "last-modified", "etag"}}
            retrieved_at = iso(dt.datetime.now(UTC))
            rawpath.write_bytes(body)
        digest = hashlib.sha256(body).hexdigest()
        payload = json.loads(body)
        chart = payload["chart"]
        if chart.get("error") or not chart.get("result"):
            raise ValueError("Yahoo chart returned error or no result: " + str(chart.get("error")))
        chart = chart["result"][0]
        quotes = chart["indicators"]["quote"][0]
        timestamps = chart.get("timestamp", [])
        raw_events = chart.get("events", {})
        splits = sorted(raw_events.get("splits", {}).values(), key=lambda s: s["date"])
        def future_split_factor(timestamp):
            factor = 1.0
            for split in splits:
                if split["date"] > timestamp:
                    factor *= float(split["numerator"]) / float(split["denominator"])
            return factor
        prices, actions, rejected = [], [], []
        for index, timestamp in enumerate(timestamps):
            day = dt.datetime.fromtimestamp(timestamp, ZoneInfo(timezone)).date()
            row = {k: quotes.get(k, [None] * len(timestamps))[index]
                   for k in ["open", "high", "low", "close", "volume"]}
            if not all(isinstance(row[k], (int, float)) and row[k] > 0
                       for k in ["open", "high", "low", "close"]):
                rejected.append({"date": str(day), "reason": "MISSING_OR_NONPOSITIVE_OHLC"})
                continue
            session_open, session_close, available = boundaries(day, market, timezone)
            if dt.datetime.fromisoformat(session_close) > dt.datetime.fromisoformat(retrieved_at):
                rejected.append({"date": str(day), "reason": "INCOMPLETE_CURRENT_SESSION"})
                continue
            factor = future_split_factor(timestamp)
            prices.append({"record_id": source_id + ":PRICE:" + str(day),
                           "asset_id": asset_id, "date": str(day),
                           "session_open_at": session_open, "session_close_at": session_close,
                           "available_at": available,
                           **{k: row[k] * factor for k in ["open", "high", "low", "close"]},
                           "volume": row["volume"], "source_id": source_id,
                           "source_sha256": digest, "pit_status": "KNOWN_MARKET_OBSERVATION_RECONSTRUCTED",
                           "quality_flags": ["CURRENT_QUOTE_VINTAGE", "AVAILABILITY_INFERRED_FROM_OBSERVED_SESSION",
                                             "SESSION_CLOSE_CONSERVATIVE_BOUND"]})
        for category, action_type in [("dividends", "dividend"), ("splits", "split")]:
            for event in sorted(raw_events.get(category, {}).values(), key=lambda e: e["date"]):
                day = dt.datetime.fromtimestamp(event["date"], ZoneInfo(timezone)).date()
                _, _, available = boundaries(day, market, timezone)
                action = {"record_id": source_id + ":" + action_type.upper() + ":" + str(day),
                          "asset_id": asset_id, "date": str(day), "available_at": available,
                          "action_type": action_type, "source_id": source_id,
                          "source_sha256": digest, "pit_status": "KNOWN_CORPORATE_ACTION_RECONSTRUCTED",
                          "quality_flags": ["CURRENT_ACTION_VINTAGE", "EXDATE_NOT_ANNOUNCEMENT_DATE"]}
                if action_type == "split":
                    action["ratio"] = float(event["numerator"]) / float(event["denominator"])
                else:
                    action["amount"] = float(event["amount"]) * future_split_factor(event["date"])
                actions.append(action)
        prices.sort(key=lambda p: p["date"])
        if not prices:
            raise ValueError("No valid complete daily rows")
        if len({p["date"] for p in prices}) != len(prices):
            raise ValueError("Duplicate observed daily dates")
        metadata = {
            "asset_id": asset_id, "symbol": symbol, "source_id": source_id,
            "market": market, "currency": currency, "instrument_type": kind,
            "underlying": underlying, "timezone": timezone,
            "inception_reference_date": inception,
            "inception_date_status": "SECONDARY_REFERENCE_NOT_HISTORICAL_LISTING_ARCHIVE",
            "source_url": url, "source_sha256": digest, "retrieved_at": retrieved_at,
            "response_headers": response_headers,
            "price_basis": "UNADJUSTED", "source_price_basis": "SPLIT_NORMALIZED",
            "price_reconstruction": "Multiply each pre-split Yahoo OHLC by product of later split ratios; do not use adjclose.",
            "price_reconstruction_verified_against_exchange_archive": False,
            "dividend_basis": "Yahoo split-normalized cash dividend multiplied by subsequent split factors",
            "split_count": len(splits), "dividend_count": sum(a["action_type"] == "dividend" for a in actions),
            "action_coverage": "COMPLETE" if kind == "ETF" else "NOT_APPLICABLE_PRICE_INDEX",
            "action_coverage_evidence": "Yahoo events=div,splits requested for entire price interval; complete means provider-reported coverage, not independent exchange verification",
            "total_return_eligible": kind == "ETF" and not splits,
            "split_action_validation_required": bool(splits),
            "execution_eligibility": "SIMULATED_NEXT_OBSERVED_NORMAL_SESSION_OPEN" if kind == "ETF" else "NONTRADEABLE_INDEX_BENCHMARK_ONLY",
            "availability_convention": "Following local calendar day 00:00 after conservative session-close bound; inferred market observability, not archived server timestamp",
            "session_clock_method": "ZoneInfo normal-session clock. Close is conservative full-day bound on half days; no complete historical halt/calendar audit.",
            "point_in_time_quality": "OBSERVED_DAILY_PRICES_CURRENT_QUOTE_VINTAGE_NOT_ARCHIVED_VINTAGE",
            "original_vintage_status": "NOT_ARCHIVED_PROVIDER_CORRECTIONS_POSSIBLE",
            "no_splits_in_analysis_interval_confirmed": not bool(splits),
            "historical_publication_timestamps_verified": False,
            "revision_risk": "Provider correction/backfill possible; original vintages unavailable; source bytes now frozen",
            "survivorship_risk": "Fixed currently surviving ETF/index sample; no market-universe inference or delisted-asset coverage",
            "adjclose_used": False, "latest_metadata_used_as_historical_feature": False,
            "limitations": ["No original historical vendor snapshot", "No dividend payment dates; exdate reinvestment convention only", "No security-level constituents or breadth", "No historical costs, bid-ask, halts or FX execution", "Index level is price return only and not a directly executable investment"],
            "first_date": prices[0]["date"], "last_date": prices[-1]["date"],
            "row_count": len(prices), "rejected_rows": rejected,
            "raw_path": str(rawpath.relative_to(ROOT)),
        }
        split_actions = [a for a in actions if a["action_type"] == "split"]
        ordinary_split_verified = False
        if asset_id in SPLIT_EVIDENCE and split_actions:
            evidence = SPLIT_EVIDENCE[asset_id]
            ordinary_split_verified = (len(split_actions) == 1
                                       and split_actions[0]["date"] == evidence["date"]
                                       and abs(split_actions[0]["ratio"] - evidence["ratio"]) < 1e-12)
            metadata["ordinary_split_evidence"] = {
                **evidence, "provider_date_ratio_match": ordinary_split_verified,
                "review_method": ("Issuer-authored wire republication and fund financial-highlights mirror reviewed via web tool; original wire inaccessible; no raw primary bytes archived here"
                                  if asset_id == "BIL" else "Primary page content reviewed via web tool; no raw primary bytes archived here"),
                "role": "ADMINISTRATOR_UNIT_RECONSTRUCTION_ONLY_NOT_KNOWN_AT_T_NEWS",
                "does_not_verify_every_dividend_amount": True,
            }
        if ordinary_split_verified:
            metadata["split_action_validation_required"] = False
            metadata["total_return_eligible"] = kind == "ETF"
        metadata["total_return_validation"] = (
            "CONDITIONAL_PROVIDER_REPORTED_TOTAL_RETURN_EXDATE_REINVESTMENT"
            if metadata["total_return_eligible"] else "NOT_APPROVED_OR_NOT_APPLICABLE")
        metadata["dividend_amounts_independently_reconciled"] = False
        if asset_id == "XLF":
            # An in-kind XLRE distribution is not a conventional stock split.
            # Treating a vendor pseudo-split as a share-count change would invent
            # total return and can also contaminate all earlier OHLC units.
            for record in prices + actions:
                record["pit_status"] = "POINT_IN_TIME_UNCERTAIN"
                record["quality_flags"].append("UNRESOLVED_XLF_XLRE_2016_SPINOFF_ADJUSTMENT")
            metadata.update({
                "price_basis": "UNRESOLVED_SPINOFF_ADJUSTED",
                "action_coverage": "INCOMPLETE",
                "total_return_eligible": False,
                "data_eligibility": "DATA_REQUIRED_XLF_SPINOFF_RECONCILIATION",
                "unsupported_corporate_action": {
                    "event": "XLRE in-kind distribution, not a normal split",
                    "ex_date_reference": "2016-09-19",
                    "primary_source_url": "https://www.sec.gov/Archives/edgar/data/1064641/000119312516699787/d246445d497.htm",
                    "publication_time_status": "NOT_USED_AS_PIT_SIGNAL_DOCUMENT_DATE_IS_NOT_FILING_TIME",
                    "scope": "Entire XLF bundle excluded until reconstruction and allocation are independently reconciled; earlier historical values may be back-adjusted",
                },
            })
            metadata["limitations"].append("All XLF rows quarantined; unsupported spin-off reconciliation is not a normal split")
            metadata["total_return_validation"] = "NOT_APPROVED_XLF_IN_KIND_SPINOFF"
        canonicalpath = rawdir / (asset_id + ".canonical.json")
        bundle = {"asset_id": asset_id, "prices": prices, "actions": actions,
                  "coverage_end": prices[-1]["date"], "action_coverage": metadata["action_coverage"],
                  "metadata": metadata}
        write_json(canonicalpath, bundle)
        metadata["canonical_path"] = str(canonicalpath.relative_to(ROOT))
        metadata["canonical_sha256"] = hashlib.sha256(canonicalpath.read_bytes()).hexdigest()
        result.update({"status": "SUCCESS", "metadata": metadata})
    except Exception as error:
        result.update({"status": "FAILED", "error_type": type(error).__name__, "error": str(error)})
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--assets", default=None)
    selection.add_argument("--core", action="store_true", help="SPY plus native Hong Kong and Japan indices")
    selection.add_argument("--extended", action="store_true", help="Eight US sector ETFs; appends to existing manifest")
    selection.add_argument("--supplemental", action="store_true", help="QQQ, IEF, GLD, UUP and cash benchmark BIL")
    selection.add_argument("--china", action="store_true", help="Bounded access test of three mainland-native Yahoo series; all bytes quarantined")
    parser.add_argument("--start", default="2010-01-01")
    parser.add_argument("--end", default="2026-10-08")
    parser.add_argument("--round", default="ROUND_002")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--offline", action="store_true", help="Rebuild canonical rows from existing frozen source bytes without network")
    args = parser.parse_args()
    asset_selection = ("XLK,SOXX,XLF,XLE,XLI,XLY,XLV,XLU" if args.extended
                       else "QQQ,IEF,GLD,UUP,BIL" if args.supplemental
                       else "CSI300,SSE,CHINEXT" if args.china
                       else (args.assets or "SPY,HSI,N225"))
    chosen = [x.strip() for x in asset_selection.split(",") if x.strip()]
    if len(chosen) > 15:
        parser.error("Maximum 15 instruments per download batch")
    if any(x not in ASSETS for x in chosen):
        parser.error("Unknown asset; available: " + ",".join(ASSETS))
    manifestpath = ROOT / "data" / "manifests" / (args.round + "_MARKET_SOURCES.json")
    auditpath = ROOT / "research" / "audit" / (args.round + "_PRICE_ACCESS.json")
    manifest = json.loads(manifestpath.read_text()) if manifestpath.exists() else {
        "round_id": args.round, "role": "ADMINISTRATOR_QUARANTINED_INPUT",
        "created_at": iso(dt.datetime.now(UTC)), "sources": {}, "access_attempts": []}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(args.workers, 4)) as executor:
        results = list(executor.map(lambda asset: acquire(asset, args.start, args.end, args.round, args.offline), chosen))
    for result in results:
        manifest["access_attempts"].append(result)
        if result["status"] == "SUCCESS":
            manifest["sources"][result["asset_id"]] = result["metadata"]
        # Never print price rows, returns or future outcomes.
        m = result.get("metadata", {})
        print(json.dumps({"asset_id": result["asset_id"], "status": result["status"],
                          "row_count": m.get("row_count"), "first_date": m.get("first_date"),
                          "last_date": m.get("last_date"), "canonical_path": m.get("canonical_path"),
                          "split_count": m.get("split_count"), "error": result.get("error")}, ensure_ascii=False))
    manifest["updated_at"] = iso(dt.datetime.now(UTC))
    write_json(manifestpath, manifest)
    write_json(auditpath, {"round_id": args.round, "updated_at": manifest["updated_at"],
                          "scope": "Small public daily price data; no future returns calculated here",
                          "attempts": manifest["access_attempts"],
                          "successful_assets": sorted(manifest["sources"]),
                          "current_history_is_original_vintage": False})
    return 0 if all(r["status"] == "SUCCESS" for r in results) else 1

if __name__ == "__main__":
    raise SystemExit(main())
