#!/usr/bin/env python3
"""Portable complete Phase3 export, retaining exact Phase2 content and restore hashes."""
import hashlib,json,shutil,sys,zipfile
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.restore_export_inputs import encoded,restore
DEST=Path('/workspace/outputs/investment_research_phase3')
ZIP=DEST.parent/'Investment_Research_Lab_Phase3_Complete.zip'
DELIVERY=Path('/workspace/scratch/investment_research_delivery_20261009')
REQUIRED=['SAMPLE_EXPANSION_PROTOCOL.md','EXPANDED_PANEL_REPORT.md','EFFECTIVE_SAMPLE_REPORT.md','CROSS_TIME_VALIDATION.md','INDUSTRY_MECHANISM_LIBRARY.md','CRISIS_VS_CORRECTION_REPORT.md','UNDERREACTION_REPORT.md','TEMPORARY_VS_STRUCTURAL_REPORT.md','MULTIPLE_TESTING_LEDGER.md','PHASE3_SURVIVING_PRINCIPLES.md','PHASE3_RESEARCH_REPORT.md','DEEP_EPISODE_LIBRARY_REPORT.md','RESEARCH_CONSTITUTION.md','RESEARCH_LEDGER.md','FAILED_HYPOTHESES.md','HYPOTHESIS_REGISTRY.md','CANDIDATE_PRINCIPLES.md','OPEN_QUESTIONS.md','CURRENT_FRAMEWORK.json','PREDICTION_LEDGER.md','CHANGELOG.md','research/status/LATEST.md']
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def build_zip(path,files,base):
    tmp=path.with_suffix('.tmp.zip')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:z.write(p,str(p.relative_to(base)))
    with zipfile.ZipFile(tmp) as z:assert z.testzip() is None
    tmp.replace(path)
def main():
    assert not ZIP.exists(),'Existing final export must not be overwritten; use a new version'
    DEST.mkdir(parents=True,exist_ok=True);DELIVERY.mkdir(parents=True,exist_ok=True)
    prior=Path('/workspace/outputs/investment_research_phase2');oldzip=prior.parent/'Investment_Research_Lab_Phase2.zip'
    oldsha=sha(oldzip);assert oldsha=='1209aed0c0530b4aed3df6172a4ba5b644cb3bea7045b3e58a570088b93bad5d'
    plan=json.loads((prior/'DATA_RESTORE_BLUEPRINTS.json').read_text());large={r['path'] for r in plan['files']}
    assert len(large)==565
    selected=[p for p in ROOT.iterdir() if p.is_file() and p.suffix in ('.md','.json')]
    for directory in ['lab','scripts','schemas','tests','sources','data','research']:
        selected += [p for p in (ROOT/directory).rglob('*') if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix!='.pyc' and str(p.relative_to(ROOT)) not in large]
    for p in sorted(set(selected)):
        target=DEST/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
    shutil.copyfile(prior/'DATA_RESTORE_BLUEPRINTS.json',DEST/'DATA_RESTORE_BLUEPRINTS.json')
    shutil.copyfile(prior/'README_FOR_REVIEW.md',DEST/'README_PHASE2_FOR_REVIEW.md')
    readme='''# 完整研究文件交付 — Phase3 + 上轮资料

本包是可继续工作的完整便携项目，不只是报告列表。包含本轮全部原来源、代码、schema、特征/标签/锁、统计JSON/CSV、失败与反例、273dossier、QA、checkpoint与永久记忆；上轮源/预测/282及扩展冻结结果保留。旧Phase2 ZIP另行原样交付，不覆盖。

人工先读PHASE3_RESEARCH_REPORT.md（15个回答）、PHASE3_SURVIVING_PRINCIPLES.md、SAMPLE_EXPANSION_PROTOCOL.md、EXPANDED_PANEL_REPORT.md、EFFECTIVE_SAMPLE_REPORT.md及CROSS_TIME_VALIDATION.md；再读4机制专题、MULTIPLE_TESTING_LEDGER、DEEP_EPISODE_LIBRARY_REPORT与research/status/LATEST.md。上轮审查入口README_PHASE2_FOR_REVIEW.md。

结果：2704规则格/2113有效feature/2087成熟12m/1995成熟24m，独立N未知。原SLOOS104表/85发布准入/19隔离。US相对波动关联经两后续反证cycle暂存，C/LEVEL2非操作，alpha/underreaction/经济机制未识别；LEVEL3原则0，CURRENT_FRAMEWORK9operative字段不变。273dossier中249价格、184价格+原信用且均缺基本面；不是273个已识别机制或新概率预测。

文件哈希和分阶段隔离不证明模型从未知道未来；报价为今天供应商重构，历史vintage未证，当前存续ETF选择、相关与重叠、跨币不可交易指数、历史费用等限制见报告。2024–25仅计算标签隔离，非真正future OOS。原120不合格pilot始终禁止评分。

重复输入的无损处理：565个原input/admin bundle合计约1.6GB重复报价已用DATA_RESTORE_BLUEPRINTS.json引用同一份旧canonical压缩。此包每个原文件SHA都能重构核验，不是删证据或改样本。解压进入包根目录运行：

```bash
python3 scripts/restore_export_inputs.py --verify-only
```

不联网、也不写大重复文件即可核验全部565原SHA。需要原A/B全部目录则运行 `python3 scripts/restore_export_inputs.py`；已有文件只核验不覆盖。研究默认审查不需恢复。旧冻结程序重跑只能验证原锁，不得改旧预测、调失败策略或覆盖报告。

未来执行用 `scripts/phase3_forward_v002.py`，原v001工程beta及锁保留。第一真实capture2026-10-30，目前真实capture/decisions/probability/outcomes0；7资产×24月份=168计划，不是实验，未部署cron。新v002修正简单收益波动、252峰值端点与完整持有sessions基准匹配；实际月末下载快照、真实锁时间之后下一开盘，缺当时捕获绝不历史回填。使用说明及安全核验在research/phase3/forward_v002/README.md。

EXPORT_MANIFEST.json含每个交付文件SHA，EXPORT_RESTORE_VERIFICATION.json记录565无损恢复验收。压缩包CRC与ZIP SHA在随包外部DELIVERY_VERIFICATION.json（ZIP自身哈希不能循环写入其内容）中。无购买、账号密钥或隐藏workspace配置。
'''
    (DEST/'README_FOR_REVIEW.md').write_text(readme)
    verification=restore(DEST,verify_only=True);(DEST/'EXPORT_RESTORE_VERIFICATION.json').write_bytes(encoded(verification))
    for p in REQUIRED:assert (DEST/p).is_file(),p
    assert (DEST/'scripts/phase3_forward_v002.py').is_file()
    manifest={'exported_at':datetime.now(timezone.utc).isoformat(),'scope':'Full portable research Phase3 including unchanged Phase2 evidence; no old ZIP overwritten','deduplicated_original_files':565,'restore_verification':verification,'files':[]}
    for p in sorted(DEST.rglob('*')):
        if p.is_file() and p.name!='EXPORT_MANIFEST.json':manifest['files'].append({'path':str(p.relative_to(DEST)),'size_bytes':p.stat().st_size,'sha256':sha(p)})
    (DEST/'EXPORT_MANIFEST.json').write_bytes(encoded(manifest))
    build_zip(ZIP,sorted(p for p in DEST.rglob('*') if p.is_file()),DEST)
    # A smaller report-only fallback is explicitly distinct from the full data/code package.
    reports=DEST.parent/'Investment_Research_Lab_Phase3_Reports.zip'
    reportpaths=[p for p in DEST.iterdir() if p.is_file() and p.suffix in ['.md','.json'] and p.name!='DATA_RESTORE_BLUEPRINTS.json']
    reportpaths += [p for p in (DEST/'research/phase3').rglob('*.md')]
    reportpaths += [p for p in (DEST/'research/phase3/figures').glob('*') if p.is_file()]
    build_zip(reports,sorted(set(reportpaths)),DEST)
    copied=[]
    for p in [ZIP,oldzip,reports]:
        target=DELIVERY/p.name
        if target.resolve()!=p.resolve():shutil.copyfile(p,target)
        target.chmod(0o644);assert sha(target)==sha(p)
        with zipfile.ZipFile(target) as z:assert z.testzip() is None
        copied.append({'file':p.name,'download_path':str(target),'bytes':target.stat().st_size,'sha256':sha(target),'zip_crc':'PASS'})
    summary=DEST/'PHASE3_RESEARCH_REPORT.md';shutil.copyfile(summary,DELIVERY/summary.name)
    result={'created_at':datetime.now(timezone.utc).isoformat(),'complete_exported_files':len(manifest['files'])+1,'original_input_sha_verified':565,'required_phase3_reports':'PASS','old_phase2_zip_unchanged':sha(oldzip)==oldsha,'delivery_files':copied,'report_markdown_path':str(DELIVERY/summary.name),'manifest_all_sources_verified':True,'browser_receipt_status':'Downloadable files prepared; user click receipt is not asserted'}
    # Independent read-back of every copy, not just zip existence.
    with zipfile.ZipFile(DELIVERY/ZIP.name) as z:
        for r in manifest['files']:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256'],r['path']
        for r in REQUIRED:assert r in z.namelist()
    (DELIVERY/'DELIVERY_VERIFICATION.json').write_bytes(encoded(result))
    (ZIP.parent/'Investment_Research_Lab_Phase3.export_verification.json').write_bytes(encoded(result))
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
