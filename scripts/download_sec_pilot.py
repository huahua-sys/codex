#!/usr/bin/env python3
"""Two original MSFT 10-K filing packages only. Separate fetch and offline review.

Companyfacts is a locator, never the source of an admitted historical amount.
Only original-accession XBRL/inline XBRL values with an independently retrieved
accepted-time source can become VERIFIED records. No prices/outcomes are read.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo
from lxml import etree, html

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/round_002/sec_pilot"
MANIFEST = ROOT / "data/manifests/ROUND_002_SEC_PILOT_SOURCES.json"
REVIEW = ROOT / "research/audit/SEC_PILOT_PIT_REVIEW.json"
FACTS_PATH = ROOT / "data/raw/round_002/probes/SEC_companyfacts_MSFT.json"
SUBMISSIONS_PATH = ROOT / "data/raw/round_002/probes/SEC_submissions_MSFT.json"
UTC = dt.timezone.utc
CONCEPTS = {
    2016: ["SalesRevenueNet", "NetIncomeLoss", "OperatingIncomeLoss", "PaymentsToAcquirePropertyPlantAndEquipment"],
    2023: ["RevenueFromContractWithCustomerExcludingAssessedTax", "NetIncomeLoss", "OperatingIncomeLoss", "PaymentsToAcquirePropertyPlantAndEquipment"],
}

def now(): return dt.datetime.now(UTC).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text())
def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n")

def fetch(url, filename, manifest):
    record = {"url": url, "requested_at": now(), "role": "ORIGINAL_SOURCE_ACQUISITION_NOT_PREDICTION"}
    path = RAW / filename
    try:
        time.sleep(0.2)  # Sequential and below SEC fair-access request limit.
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 InvestmentResearchLab/0.3 public archival research pilot", "Accept-Encoding": "identity"})
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read()
            headers = {k: v for k, v in response.headers.items() if k.lower() in {"date", "last-modified", "content-type", "etag"}}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        record.update(status="SUCCESS", source_path=str(path.relative_to(ROOT)),
                      source_sha256=sha(path), retrieved_at=now(), bytes=len(body), response_headers=headers)
    except Exception as error:
        record.update(status="FAILED", error_type=type(error).__name__, error=str(error), completed_at=now())
    manifest["access_attempts"].append(record)
    return record

def locate(facts, year):
    start, end = f"{year-1}-07-01", f"{year}-06-30"
    rows = [r for r in facts["facts"]["us-gaap"][CONCEPTS[year][0]]["units"]["USD"]
            if r.get("start") == start and r.get("end") == end and r.get("form") == "10-K"
            and r.get("filed", "") >= end and r.get("filed", "") <= f"{year}-09-30"]
    if not rows: raise ValueError("No first original-year 10-K locator for " + str(year))
    selected = sorted(rows, key=lambda r: (r["filed"], r["accn"]))[0]
    return {"year": year, "accession": selected["accn"], "locator_filing_date": selected["filed"],
            "observed_period_start": start, "observed_period_end": end,
            "research_cutoff": f"{year}-09-30T23:59:59+00:00", "locator_status": "NOT_YET_ORIGINAL_AMOUNT_VERIFIED"}

def submission_row(table, accession):
    values = table.get("filings", {}).get("recent", table)
    for index, number in enumerate(values.get("accessionNumber", [])):
        if number == accession:
            return {k: v[index] for k, v in values.items() if isinstance(v, list) and len(v) > index}
    return None

def download():
    facts, submissions = read(FACTS_PATH), read(SUBMISSIONS_PATH)
    if int(facts["cik"]) != 789019 or int(submissions["cik"]) != 789019:
        raise ValueError("Unexpected issuer; pilot is MSFT only")
    manifest = {"pilot_id": "SEC_MSFT_TWO_ORIGINAL_FILINGS", "created_at": now(),
                "issuer": "MSFT", "cik": "0000789019", "access_attempts": [], "filings": [],
                "locator_inputs": [{"source_path": str(p.relative_to(ROOT)), "source_sha256": sha(p),
                                    "status": "CURRENT_API_LOCATOR_NOT_ORIGINAL_FILING_EVIDENCE"}
                                   for p in [FACTS_PATH, SUBMISSIONS_PATH]],
                "maximum_original_filing_packages": 2, "investment_hypotheses_tested": 0}
    selected = [locate(facts, year) for year in [2016, 2023]]
    historical = None
    if submission_row(submissions, selected[0]["accession"]) is None:
        shard = next(x for x in submissions["filings"].get("files", []) if x["filingFrom"] <= selected[0]["locator_filing_date"] <= x["filingTo"])
        result = fetch("https://data.sec.gov/submissions/" + shard["name"], shard["name"], manifest)
        if result["status"] == "SUCCESS": historical = read(ROOT / result["source_path"])
    for item in selected:
        accession = item["accession"]
        row = submission_row(submissions, accession) or (submission_row(historical, accession) if historical else None)
        item["submissions_locator"] = row
        prefix = f"MSFT_{item['year']}"
        base = "https://www.sec.gov/Archives/edgar/data/789019/" + accession.replace("-", "") + "/"
        item["filing_index"] = fetch(base + accession + "-index.html", prefix + ".filing-index.html", manifest)
        item["directory_index"] = fetch(base + "index.json", prefix + ".directory-index.json", manifest)
        primary = row.get("primaryDocument") if row else None
        # The file index is an original-accession locator, not a source of facts.
        if not primary and item["filing_index"]["status"] == "SUCCESS":
            tree = html.fromstring((ROOT / item["filing_index"]["source_path"]).read_bytes())
            for tr in tree.xpath("//tr"):
                cells = tr.xpath("./td")
                if len(cells) >= 4 and cells[3].text_content().strip() == "10-K":
                    links = cells[2].xpath(".//a/@href")
                    if links: primary = links[0].split("/")[-1]; break
        item["primary_document_name"] = primary
        if primary:
            item["primary_document"] = fetch(base + primary, prefix + ".primary.html", manifest)
        else:
            item["primary_document"] = {"status": "FAILED", "error": "Primary original 10-K not located"}
        # Pre-inline 2016 requires the same-accession XBRL instance; 2023 primary is inline.
        if item["year"] == 2016 and item["directory_index"]["status"] == "SUCCESS":
            inventory = read(ROOT / item["directory_index"]["source_path"])["directory"]["item"]
            names = [x["name"] for x in inventory if x["name"].lower().endswith(".xml")
                     and "20160630" in x["name"] and not any(z in x["name"].lower() for z in ["_cal", "_def", "_lab", "_pre"])]
            if len(names) == 1:
                item["xbrl_instance"] = fetch(base + names[0], prefix + ".original-instance.xml", manifest)
            else:
                item["xbrl_instance"] = {"status": "FAILED", "error": "Original instance inventory ambiguous: " + str(names)}
        manifest["filings"].append(item)
        write(MANIFEST, manifest)
        print(json.dumps({"year": item["year"], "accession": accession,
                          "primary_document_name": primary, "primary_status": item["primary_document"]["status"],
                          "index_status": item["filing_index"]["status"],
                          "instance_status": item.get("xbrl_instance", {}).get("status", "INLINE_PRIMARY_EXPECTED")}, ensure_ascii=False))
    manifest["completed_at"] = now()
    write(MANIFEST, manifest)

def localname(value): return str(value).split("}")[-1].split(":")[-1].lower()
def contexts(tree):
    result = {}
    for node in tree.iter():
        if localname(node.tag) != "context": continue
        children = list(node.iter())
        get = lambda tag: next((x.text.strip() for x in children if localname(x.tag) == tag and x.text), None)
        result[node.get("id")] = {"start": get("startdate"), "end": get("enddate"),
                                 "entity": get("identifier"),
                                 "dimensional": any(localname(x.tag) in {"explicitmember", "typedmember", "segment", "scenario"} for x in children)}
    return result

def units(tree):
    out = {}
    for node in tree.iter():
        if localname(node.tag) == "unit":
            measures = [x.text.strip() for x in node.iter() if localname(x.tag) == "measure" and x.text]
            if len(measures) == 1 and not any(localname(x.tag) == "divide" for x in node.iter()):
                out[node.get("id")] = measures[0].split(":")[-1]
    return out

def original_facts(tree, year, inline):
    context_map, unit_map = contexts(tree), units(tree)
    out = []
    for node in tree.iter():
        concept = node.get("name", "").split(":")[-1] if inline else etree.QName(node).localname if isinstance(node.tag, str) else ""
        if concept not in CONCEPTS[year]: continue
        attrs = {k.lower(): v for k, v in node.attrib.items()}
        context = context_map.get(attrs.get("contextref"), {})
        if context.get("start") != f"{year-1}-07-01" or context.get("end") != f"{year}-06-30" or context.get("dimensional"): continue
        if unit_map.get(attrs.get("unitref")) != "USD": continue
        value_text = "".join(node.itertext()).strip().replace(",", "").replace("\u00a0", "").replace(" ", "")
        if not re.fullmatch(r"-?\d+(?:\.\d+)?", value_text): continue
        value = float(value_text) * 10 ** int(attrs.get("scale", "0"))
        if attrs.get("sign") == "-": value = -value
        out.append({"concept": concept, "value": int(value) if value.is_integer() else value,
                    "units": "USD", "context_id": attrs.get("contextref"), "unit_id": attrs.get("unitref"),
                    "source_numeric_text": value_text, "scale": attrs.get("scale", "0"),
                    "entity_identifier": context.get("entity"), "decimals": attrs.get("decimals"),
                    "observed_period_start": context["start"], "observed_period_end": context["end"]})
    return out

def accepted_time(item):
    source = item["filing_index"]
    if source.get("status") != "SUCCESS": return None, "ORIGINAL_ACCEPTED_INDEX_UNAVAILABLE"
    text = html.fromstring((ROOT / source["source_path"]).read_bytes()).text_content()
    match = re.search(r"Accepted\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", text)
    if not match: return None, "ACCEPTED_TIMESTAMP_NOT_FOUND_IN_ORIGINAL_INDEX"
    eastern = dt.datetime.strptime(match[1], "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("America/New_York"))
    accepted = eastern.astimezone(UTC)
    recent = (item.get("submissions_locator") or {}).get("acceptanceDateTime")
    if recent and dt.datetime.fromisoformat(recent.replace("Z", "+00:00")).astimezone(UTC) != accepted:
        return None, "SUBMISSIONS_AND_ORIGINAL_INDEX_ACCEPTED_TIME_CONFLICT"
    return accepted, {"raw_accepted_text": match[1], "interpretation_timezone": "America/New_York",
                      "original_index_url": source["url"], "original_index_sha256": source["source_sha256"],
                      "submissions_acceptance_timestamp": recent,
                      "note": "EDGAR accepted timestamp, not earnings release date; availability conservatively delayed to following local calendar day 00:00"}

def review():
    manifest, facts = read(MANIFEST), read(FACTS_PATH)
    report = {"pilot_id": manifest["pilot_id"], "reviewed_at": now(), "original_filing_packages": 2,
              "investment_tests_completed": 0, "sources_manifest_sha256": sha(MANIFEST),
              "records": [], "filing_checks": [], "later_locator_values_quarantined": [],
              "minimal_schema": ["record_id", "issuer_cik", "accession", "form", "concept", "value", "units", "observed_period_start", "observed_period_end", "context_id", "accepted_at", "published_at", "available_at", "availability_evidence", "source_path", "source_sha256", "vintage_id", "revision_of", "pit_status", "accounting_basis", "quality_flags"],
              "limitations": ["Only two annual reports, not quarterly forecasts or earnings revisions", "Companyfacts is a current locator, never historical source proof by itself", "No valuation or analyst expectation vintage", "2016/2023 revenue concepts/accounting bases differ; no naive growth comparison", "Capital expenditure is cash property/plant/equipment payments, not total investment commitments or finance leases", "Original accepted time is distinct from fiscal end, earnings release and earliest possible dissemination", "No MSFT prices, future outcomes or predictions read"]}
    for item in manifest["filings"]:
        year, accession = item["year"], item["accession"]
        accepted, evidence = accepted_time(item)
        source = item.get("xbrl_instance") if year == 2016 else item["primary_document"]
        checked = {"year": year, "accession": accession, "accepted_time_evidence": evidence,
                   "primary_document_status": item["primary_document"].get("status"), "facts_status": "POINT_IN_TIME_UNCERTAIN"}
        if not source or source.get("status") != "SUCCESS" or item["primary_document"].get("status") != "SUCCESS" or accepted is None:
            checked["reason"] = "Original report, original structured fact, or independent accepted time unavailable"
            report["filing_checks"].append(checked); continue
        rawpath = ROOT / source["source_path"]
        if sha(rawpath) != source["source_sha256"]: raise ValueError("Frozen original source hash changed")
        tree = etree.parse(str(rawpath), parser=etree.XMLParser(resolve_entities=False, no_network=True)).getroot() if year == 2016 else html.fromstring(rawpath.read_bytes())
        candidates = original_facts(tree, year, inline=year != 2016)
        avail = dt.datetime.combine(accepted.astimezone(ZoneInfo("America/New_York")).date()+dt.timedelta(days=1), dt.time(0), ZoneInfo("America/New_York")).astimezone(UTC)
        cutoff = dt.datetime.fromisoformat(item["research_cutoff"])
        for concept in CONCEPTS[year]:
            original = [r for r in candidates if r["concept"] == concept]
            locator = [r for r in facts["facts"]["us-gaap"][concept]["units"]["USD"]
                       if r.get("accn") == accession and r.get("start") == f"{year-1}-07-01" and r.get("end") == f"{year}-06-30"]
            values = {r["value"] for r in original}
            loc_values = {r["val"] for r in locator}
            verified = (len(values) == 1 and values == loc_values and avail <= cutoff
                        and all(str(r["entity_identifier"]).lstrip("0") == "789019" for r in original))
            record = {"record_id": f"MSFT:{accession}:{concept}:{year}-06-30", "issuer_cik": "0000789019",
                      "accession": accession, "form": "10-K", "concept": concept,
                      "value": next(iter(values)) if len(values) == 1 else None,
                      "units": "USD", "observed_period_start": f"{year-1}-07-01", "observed_period_end": f"{year}-06-30",
                      "accepted_at": accepted.isoformat(), "published_at": accepted.isoformat(),
                      "published_at_basis": "PUBLIC_ARCHIVED_EDGAR_ACCEPTED_TIME_PROXY_WITH_CONSERVATIVE_LAG_NOT_EARNINGS_RELEASE_TIME",
                      "available_at": avail.isoformat(), "research_cutoff_at": item["research_cutoff"],
                      "availability_evidence": evidence, "source_id": "SEC_ORIGINAL_MSFT_"+str(year),
                      "source_path": source["source_path"], "source_sha256": source["source_sha256"],
                      "original_primary_sha256": item["primary_document"]["source_sha256"],
                      "vintage_id": accession, "revision_of": None, "accounting_basis": "US_GAAP_AS_ORIGINALLY_FILED_NOT_CURRENT_RECAST",
                      "original_structured_evidence": original, "companyfacts_locator_values": sorted(loc_values),
                      "pit_status": "VERIFIED" if verified else "POINT_IN_TIME_UNCERTAIN",
                      "quality_flags": ["FOLLOWING_LOCAL_DAY_CONSERVATIVE_AVAILABILITY", "NO_LATER_ACCESSION_SUBSTITUTION", "NO_VALUATION_OR_EXPECTATION_DATA"]}
            report["records"].append(record)
            for later in facts["facts"]["us-gaap"][concept]["units"]["USD"]:
                if later.get("start") == record["observed_period_start"] and later.get("end") == record["observed_period_end"] and later.get("filed", "") > f"{year}-09-30" and later.get("val") not in values:
                    report["later_locator_values_quarantined"].append({"concept": concept, "observed_period_end": record["observed_period_end"], "original_value": record["value"], "later_locator_value": later["val"], "later_accession": later["accn"], "later_filed": later["filed"], "status": "KNOWN_ONLY_AFTER_T_LOCATOR_NOT_ORIGINAL_DOCUMENT_VERIFIED", "not_used_in_replay": True})
        checked["facts_status"] = "VERIFIED" if all(r["pit_status"] == "VERIFIED" for r in report["records"] if r["accession"] == accession) and any(r["accession"] == accession for r in report["records"]) else "POINT_IN_TIME_UNCERTAIN"
        report["filing_checks"].append(checked)
    report["verified_record_count"] = sum(r["pit_status"] == "VERIFIED" for r in report["records"])
    report["quarantined_record_count"] = sum(r["pit_status"] != "VERIFIED" for r in report["records"])
    write(REVIEW, report)
    print(json.dumps({"pilot_id": report["pilot_id"], "verified_records": report["verified_record_count"], "quarantined_records": report["quarantined_record_count"], "filing_statuses": [{"year":x["year"], "status":x["facts_status"]} for x in report["filing_checks"]]}, ensure_ascii=False))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fetch", action="store_true")
    mode.add_argument("--review", action="store_true", help="Offline only; no network calls")
    args = p.parse_args()
    if args.fetch: download()
    else: review()

if __name__ == "__main__": main()
