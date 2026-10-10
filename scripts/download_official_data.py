#!/usr/bin/env python3
"""Small original-release pack, never replace observation dates with release dates.

Run --download once in a network-enabled executor. Without that flag this script
only parses locally saved official archives. It never fetches equity outcomes.
Optional --probe tests a small source catalogue; --market-context downloads FRED
current histories into a quarantine and does NOT grant them PIT eligibility.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/round_002/official"
MANIFEST = ROOT / "data/manifests/ROUND_002_OFFICIAL_SOURCES.json"
AUDIT = ROOT / "research/audit/ROUND_002_OFFICIAL_ACCESS.json"
RECORDS = RAW / "release_records.json"
DATES = {
    2016: ("20160921", "09162016"),
    2017: ("20170920", "09142017"),
    2018: ("20180926", "09132018"),
    2019: ("20190918", "09122019"),
    2020: ("20200916", "09112020"),
    2021: ("20210922", "09142021"),
    2022: ("20220921", "09132022"),
    2023: ("20230920", "09132023"),
}
PROBES = {
    "FRED": "https://fred.stlouisfed.org/graph/graph.csv?id=DGS10&cosd=2016-01-01&coed=2016-01-10",
    "ALFRED_API_NO_KEY": "https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&file_type=json&realtime_start=2016-12-31&realtime_end=2016-12-31",
    "ALFRED_WEB": "https://alfred.stlouisfed.org/series?seid=CPIAUCSL",
    "SEC_EDGAR": "https://data.sec.gov/submissions/CIK0000320193.json",
    "BOJ_ORIGINAL": "https://www.boj.or.jp/en/mopo/outlook/gor1610b.pdf",
    "HKMA_ARCHIVE": "https://www.hkma.gov.hk/eng/news-and-media/press-releases/2016/12/20161215-3/",
    "NBS": "https://www.stats.gov.cn/english/",
    "PBOC": "http://www.pbc.gov.cn/en/3688006/index.html",
    "ECB_ORIGINAL": "https://www.ecb.europa.eu/press/pr/date/2016/html/pr161208.en.html",
    "BEA": "https://www.bea.gov/data/gdp/gross-domestic-product",
    "US_TREASURY": "https://home.treasury.gov/resource-center-data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2016",
}
FRED_SERIES = ["DGS2", "DGS10", "DFII10", "BAMLH0A0HYM2", "DTWEXBGS"]

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def sha(b):
    return hashlib.sha256(b).hexdigest()

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}: self.skip += 1
    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.skip: self.skip -= 1
        if tag in {"p", "div", "tr", "h1", "h2", "h3", "pre", "br"}: self.parts.append("\n")
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)
    def text(self):
        return re.sub(r"[ \t\r\f\v]+", " ", "".join(self.parts))

def visible(b):
    charset = re.search(br"charset\s*=\s*['\"]?([\w-]+)", b[:12000], re.I)
    encoding = charset.group(1).decode("ascii") if charset else "utf-8"
    try:
        decoded = b.decode(encoding)
    except UnicodeDecodeError:
        # Several archived BLS releases retain Windows punctuation with no meta
        # charset declaration. Preserve these characters; never alter raw bytes.
        decoded = b.decode("cp1252") if not charset else b.decode(encoding, "replace")
    p = VisibleText(); p.feed(decoded)
    return p.text()

def fetch(url, path=None):
    result = {"url": url, "tested_at": utcnow()}
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 InvestmentResearchLab/0.2 public archives"})
        with urllib.request.urlopen(request, timeout=35) as response:
            body = response.read(8 * 1024 * 1024 + 1)
            if len(body) > 8 * 1024 * 1024: raise ValueError("response exceeds deliberately small 8 MiB cap")
            result.update(status="ACCESSIBLE", http_status=response.status, final_url=response.url,
                          content_type=response.headers.get("Content-Type"), bytes=len(body), source_sha256=sha(body))
            if path:
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.exists() and path.read_bytes() != body:
                    previous = path.with_suffix(path.suffix + ".prior." + sha(path.read_bytes())[:12])
                    if not previous.exists(): previous.write_bytes(path.read_bytes())
                path.write_bytes(body)
                result["source_path"] = str(path.relative_to(ROOT))
    except Exception as exc:
        result.update(status="ACCESS_FAILED", error=f"{type(exc).__name__}: {exc}")
    return result

def specs():
    out = []
    for year, (fed_date, cpi_date) in DATES.items():
        out.extend([
            dict(source_id=f"FED-FOMC-{fed_date}", release_type="FOMC_STATEMENT", category="policy",
                 date=datetime.strptime(fed_date, "%Y%m%d").date().isoformat(),
                 url=f"https://www.federalreserve.gov/newsevents/pressreleases/monetary{fed_date}a.htm",
                 path=RAW / f"fomc_{fed_date}.html"),
            dict(source_id=f"BLS-CPI-{cpi_date}", release_type="CPI_FIRST_RELEASE", category="inflation",
                 date=datetime.strptime(cpi_date, "%m%d%Y").date().isoformat(),
                 url=f"https://www.bls.gov/news.release/archives/cpi_{cpi_date}.htm",
                 path=RAW / f"cpi_{cpi_date}.html"),
        ])
    return out

def fraction(value):
    value = value.strip().replace("-", " ").replace("\u00bc", " 1/4").replace("\u00bd", " 1/2").replace("\u00be", " 3/4")
    parts = value.split()
    total = 0.0
    for part in parts:
        if "/" in part:
            numerator, denominator = part.split("/"); total += float(numerator) / float(denominator)
        else: total += float(part)
    return total

def parse_release(spec):
    path = spec["path"]
    if not path.exists(): return None
    b = path.read_bytes(); full = visible(b); flat = re.sub(r"\s+", " ", full)
    day = datetime.strptime(spec["date"], "%Y-%m-%d")
    date_label = f"{day.strftime('%B')} {day.day}, {day.year}"
    date_match = re.search(rf"{day.strftime('%B')}\s+0?{day.day},?\s+{day.year}", flat)
    if spec["release_type"] == "FOMC_STATEMENT":
        time_match = re.search(r"For release at\s+(\d{1,2})(?::(\d{2}))?\s*p\.?m\.?\s*(E[SD]T)", flat, re.I)
        release_end = time_match.end() if time_match else 0
        possible_starts = [flat.find(marker, release_end) for marker in
                           ("Information received", "Recent indicators", "The Federal Reserve is committed")]
        possible_starts = [x for x in possible_starts if x >= 0]
        start = min(possible_starts) if possible_starts else -1
        stop = flat.find("Voting for", max(0, start))
        original = flat[max(0, start):stop if stop > start else max(0, start) + 14000]
        release_evidence = time_match.group(0) if time_match else None
        hour = int(time_match.group(1)) + 12 if time_match else None
        minute = int(time_match.group(2) or 0) if time_match else None
        fields = {}
        rate_value = r"(?:\d+[-\s]\d/\d|\d/\d|\d+(?:\.\d+)?)"
        rate_match = re.search(r"target range for the federal funds rate\s+(?:to|at|of)\s+(" + rate_value + r")\s+to\s+(" + rate_value + r")\s+percent", original, re.I)
        if rate_match:
            fields["fed_funds_target_low_pct"] = fraction(rate_match.group(1))
            fields["fed_funds_target_high_pct"] = fraction(rate_match.group(2))
            fields["rate_evidence"] = rate_match.group(0)
        fields["original_statement_text"] = original
    else:
        time_match = re.search(r"(?:Transmission of material in this release is embargoed until|embargoed until)\s+(\d{1,2}):(\d{2})\s*a\.?m\.?\s*\((E(?:[SD])?T)\)", flat, re.I)
        start = flat.find("CONSUMER PRICE INDEX")
        if start < 0: start = flat.find("The Consumer Price Index for All Urban Consumers")
        stop = flat.find("Table 1.", max(0, start))
        original = flat[max(0, start):stop if stop > start else max(0, start) + 20000]
        release_evidence = time_match.group(0) if time_match else None
        hour = int(time_match.group(1)) if time_match else None
        minute = int(time_match.group(2)) if time_match else None
        fields = {}
        annual = re.search(r"(?:Over the last 12 months|over the past year|over the last year),?\s*(?:the )?(?:all items index|index)\s+(?:increased|rose)\s+([\d.]+)\s+percent", original, re.I)
        if annual: fields["cpi_headline_yoy_pct_first_release"] = float(annual.group(1)); fields["headline_yoy_evidence"] = annual.group(0)
        monthly = re.search(r"Consumer Price Index for All Urban Consumers\s*\(CPI-U\)\s+(increased|rose|declined|fell)\s+([\d.]+)\s+percent", original, re.I)
        if monthly:
            sign = -1 if monthly.group(1).lower() in {"declined", "fell"} else 1
            fields["cpi_headline_mom_sa_pct_first_release"] = sign * float(monthly.group(2))
            fields["headline_mom_evidence"] = monthly.group(0)
        elif re.search(r"CPI-U\)\s+was unchanged", original, re.I): fields["cpi_headline_mom_sa_pct_first_release"] = 0.0
        core = re.search(r"(?:all items less food and energy index|index for all items less food and energy)\s+(?:rose|increased)\s+([\d.]+)\s+percent\s+(?:over|for)\s+(?:the\s+)?(?:last|past)\s+12\s+months", original, re.I)
        if core: fields["cpi_core_yoy_pct_first_release"] = float(core.group(1)); fields["core_yoy_evidence"] = core.group(0)
        fields["original_release_excerpt"] = original[:15000]
    verified = bool(date_match and time_match and start >= 0 and original)
    published = day.replace(hour=hour, minute=minute, tzinfo=ZoneInfo("America/New_York")) if verified else None
    iso = published.astimezone(timezone.utc).isoformat() if published else None
    record = {
        "record_id": spec["source_id"], "source_id": spec["source_id"], "release_type": spec["release_type"],
        "category": spec["category"], "market": "US", "reference_period": f"{day.year}-08" if spec["category"] == "inflation" else spec["date"],
        "observed_period_end": f"{day.year}-08-31" if spec["category"] == "inflation" else spec["date"],
        "published_at": iso, "available_at": iso, "publication_timezone": "America/New_York",
        "publication_date_evidence": date_match.group(0) if date_match else None,
        "publication_time_evidence": release_evidence, "published_at_precision": "MINUTE" if verified else "UNKNOWN",
        "availability_evidence": "Original official dated archive body and explicit public/embargo release time; public web channel.",
        "pit_status": "VERIFIED" if verified else "POINT_IN_TIME_UNCERTAIN",
        "source_url": spec["url"], "source_path": str(path.relative_to(ROOT)), "source_sha256": sha(b),
        "ingested_at": utcnow(), "vintage_id": spec["source_id"] + "-ORIGINAL_ARCHIVED_RELEASE", "revision_of": None,
        "value": fields, "fields": fields, "units": "percent where numeric", "currency": None,
        "quality_flags": ["ARCHIVED_RELEASE_RETRIEVED_TODAY_NOT_EXTERNAL_WAYBACK_SNAPSHOT", "CURRENT_NAVIGATION_EXCLUDED_FROM_RELEASE_TEXT"] + (["DISPLAY_DECODING_REPLACEMENT_RAW_BYTES_PRESERVED"] if "\ufffd" in original else []),
        "missing_reason": None if verified else "Release date/time/body pattern could not all be verified; do not feed Stage A.",
    }
    text_path = path.with_suffix(".original.txt")
    text_path.write_text(original + "\n")
    record["original_text_path"] = str(text_path.relative_to(ROOT))
    return record

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--market-context", action="store_true")
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    audit = json.loads(AUDIT.read_text()) if AUDIT.exists() else {"round_id": "ROUND_002", "access_attempts": [], "source_probes": [], "market_context": []}
    entries = specs()
    if args.download:
        attempts = list(ThreadPoolExecutor(max_workers=4).map(lambda s: dict(source_id=s["source_id"], **fetch(s["url"], s["path"])), entries))
        audit["access_attempts"].extend(attempts)
        write_json(AUDIT, audit)
    if args.probe:
        probes = list(ThreadPoolExecutor(max_workers=4).map(lambda x: dict(source_id=x[0], **fetch(x[1])), PROBES.items()))
        audit["source_probes"].extend(probes)
        write_json(AUDIT, audit)
    if args.market_context:
        quarantine = ROOT / "data/quarantine/round_002/fred_current_history"
        results = []
        for series in FRED_SERIES:
            url = f"https://fred.stlouisfed.org/graph/graph.csv?id={series}&cosd=2015-01-01&coed=2023-09-30"
            result = dict(source_id=f"FRED-{series}", pit_status="POINT_IN_TIME_UNCERTAIN", eligibility="EXCLUDED_STAGE_A", **fetch(url, quarantine / f"{series}.csv"))
            result["limitation"] = "Downloaded current historical values are not verified publication vintages. Lags do not repair revision risk."
            results.append(result)
        audit["market_context"].extend(results); write_json(AUDIT, audit)
    records = [r for s in entries if (r := parse_release(s)) is not None]
    write_json(RECORDS, records)
    write_json(MANIFEST, {
        "round_id": "ROUND_002", "built_at": utcnow(), "selection": "Latest scheduled September FOMC and August CPI release published in September for deterministic annual September 30 cutoffs 2016–2023; no outcome-based selection.",
        "release_record_path": str(RECORDS.relative_to(ROOT)), "source_count": len(records),
        "verified_release_count": sum(r["pit_status"] == "VERIFIED" for r in records),
        "sources": [{k:v for k,v in r.items() if k not in {"fields", "value"}} for r in records],
        "scope_limits": ["US official policy/inflation only; does not represent HK or Japan domestic policy.", "No vintage-verified credit, earnings, valuation, liquidity, breadth, sentiment or capital-action series.", "Archived release vintage, not today revised macro series.", "No causal or investment principle inferred by the downloader."]
    })
    print(json.dumps({"records": len(records), "verified": sum(r["pit_status"] == "VERIFIED" for r in records), "failed_access": sum(x.get("status") == "ACCESS_FAILED" for x in audit["access_attempts"]), "records_path": str(RECORDS)}, indent=2))

if __name__ == "__main__": main()
