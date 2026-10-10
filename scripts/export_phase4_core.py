#!/usr/bin/env python3
"""Export new Phase4 core, preserving the previous 135MB archive byte-for-byte."""
import hashlib, json, shutil, zipfile
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=Path('/workspace/outputs/Investment_Research_Phase4')
ZIP=Path('/workspace/outputs/Investment_Research_Phase4_CORE.zip')
DOCS=['MARKET_ECOLOGY_US.md','MARKET_ECOLOGY_CHINA.md','MARKET_ECOLOGY_JAPAN.md',
      'MARGINAL_PLAYER_MAP_US.md','MARGINAL_PLAYER_MAP_CHINA.md','MARGINAL_PLAYER_MAP_JAPAN.md',
      'CONSTRAINED_CAPITAL_FRAMEWORK.md','MARKET_FOOTPRINTS.md','PANIC_AND_FORCED_LIQUIDATION_FRAMEWORK.md',
      'SLOW_MONEY_TREND_FRAMEWORK.md','EXPECTATION_GAP_FRAMEWORK.md','CAPITAL_CYCLE_FRAMEWORK.md',
      'REVEALED_PREFERENCE_FRAMEWORK.md','RULE_CHANGE_MONITOR.md','HUMAN_DECISION_ARCHITECTURE.md',
      'FAILED_MECHANISM_CASES.md','PHASE4_MARKET_ECOLOGY_REPORT.md','README_PHASE4.md']
MEMORY=['RESEARCH_LEDGER.md','HYPOTHESIS_REGISTRY.md','FAILED_HYPOTHESES.md','CANDIDATE_PRINCIPLES.md',
        'OPEN_QUESTIONS.md','CHANGELOG.md','CURRENT_FRAMEWORK.json','PREDICTION_LEDGER.md',
        'MULTIPLE_TESTING_LEDGER.md','research/status/LATEST.md']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if DEST.exists() or ZIP.exists():raise FileExistsError('Refusing to overwrite a completed export')
    baseline=ROOT/'research/phase4/audit/PRE_PHASE4_BASELINE.v001.json'
    assert sha('/workspace/scratch/InvestmentResearchLab.zip')=='54afd13ebdfebfc6c0f719617991d41fb2625b48d0d5a7b19fc2280ea2cd7095'
    selected={ROOT/f for f in DOCS+MEMORY}
    for directory in ['BEHAVIORAL_EVENT_LIBRARY','research/behavioral_events','research/evidence_cards','research/phase4']:
        for p in (ROOT/directory).rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts:continue
            # Large original downloads are retained in the full Git repository.
            # Core retains manifests, excerpts, code, metadata, all event/label records.
            if 'research/phase4/sources/' in str(p.relative_to(ROOT)) and p.suffix.lower() not in {'.json','.md','.py','.txt'}:
                continue
            selected.add(p)
    selected.update(p for p in (ROOT/'scripts').glob('*phase4*.py'))
    selected.add(ROOT/'sources/Codex_Phase4_Market_Ecology_Constrained_Capital_Prompt.md')
    missing=[str(f) for f in selected if not f.is_file()]
    if missing:raise FileNotFoundError(missing)
    DEST.mkdir(parents=True)
    records=[]
    for p in sorted(selected):
        rel=p.relative_to(ROOT);q=DEST/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
        records.append({'path':str(rel),'size_bytes':q.stat().st_size,'sha256':sha(q)})
    manifest={'created_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'All Phase4 core documents, full cards/dossiers/labels/statistics/code/audits and source indexes/excerpts. Large raw downloads and previous price data are in full Git project.',
              'excluded_raw_downloads_explicit':True,'input_source_index':'research/phase4/data/SOURCE_FILE_INDEX.v001.json',
              'original_full_archive_sha256':'54afd13ebdfebfc6c0f719617991d41fb2625b48d0d5a7b19fc2280ea2cd7095',
              'files':records}
    (DEST/'CORE_EXPORT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    with zipfile.ZipFile(ZIP,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(DEST)))
    with zipfile.ZipFile(ZIP) as z:
        assert z.testzip() is None
        for r in records:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
    assert ZIP.stat().st_size<10_000_000, 'Core package exceeds 10MB target'
    shared=Path('/workspace/scratch/Investment_Research_Phase4_CORE.zip')
    assert not shared.exists();shutil.copyfile(ZIP,shared);shared.chmod(0o644)
    receipt={'created_at_utc':datetime.now(timezone.utc).isoformat(),'archive':str(ZIP),
             'shared_copy':str(shared),'size_bytes':ZIP.stat().st_size,'sha256':sha(ZIP),
             'manifested_files':len(records),'crc':'PASS','readback_all_file_hashes':'PASS',
             'original_135mb_archive_unchanged':True,'recipient_download_confirmed':False}
    Path('/workspace/outputs/PHASE4_CORE_EXPORT_VERIFICATION.v001.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
