#!/usr/bin/env python3
"""Portable review export with exact source deduplication, not a new study."""
import hashlib,json,shutil,sys,zipfile
from datetime import datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.restore_export_inputs import encoded,restore,stamp
ROOT=Path(__file__).resolve().parents[1]
DEST=Path('/workspace/outputs/investment_research_phase2')
ZIP=DEST.parent/'Investment_Research_Lab_Phase2.zip'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def export():
    DEST.mkdir(parents=True,exist_ok=True)
    canonical={}
    source_objs={}
    for p in sorted((ROOT/'data/raw/round_002/market').glob('*.canonical.json')):
        x=json.loads(p.read_text());aid=x['asset_id'];source_objs[aid]=x
        canonical[aid]={'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
    plan={'purpose':'Lossless deduplication of repeated daily rows; no data changed',
          'canonical_sources':canonical,'files':[],'invalid_pilot_status':'PRESERVED_BUT_NEVER_VALIDATED_OR_SCORED'}
    large=set()
    def mode(aid,k,rows,cutoff=None):
        full=source_objs[aid][k]
        if cutoff:
            statuses={'VERIFIED','VERIFIED_CONSERVATIVE_SESSION_LAG',
                      'KNOWN_MARKET_OBSERVATION_RECONSTRUCTED' if k=='prices' else 'KNOWN_CORPORATE_ACTION_RECONSTRUCTED'}
            expected=[r for r in full if r.get('pit_status') in statuses and r.get('available_at') and stamp(r['available_at'])<=stamp(cutoff)]
            if rows==expected:return 'KNOWN_CUTOFF'
        elif rows==full:return 'FULL'
        if not rows:return 'EMPTY'
        raise ValueError('source differs from immutable original rows: '+aid+' '+k)
    for p in sorted((ROOT/'research/replays').rglob('*.input.v001.json')):
        x=json.loads(p.read_text());aid=x['asset_id'];b={'kind':'INPUT','path':str(p.relative_to(ROOT)),
            'sha256':sha(p),'asset_id':aid,'body':{k:v for k,v in x.items() if k not in ('prices','actions')}}
        for k in ('prices','actions'):b[k+'_mode']=mode(aid,k,x.get(k,[]),x['cutoff_at'])
        plan['files'].append(b);large.add(p)
    for p in sorted((ROOT/'research/replays').rglob('admin_bundle.v001.json')):
        x=json.loads(p.read_text());b={'kind':'ADMIN_BUNDLE','path':str(p.relative_to(ROOT)),
            'sha256':sha(p),'body':x,'asset_modes':{}}
        for aid,asset in x['assets'].items():
            b['asset_modes'][aid]={}
            for k in ('prices','actions'):
                b['asset_modes'][aid][k]=mode(aid,k,asset.pop(k,[]))
        plan['files'].append(b);large.add(p)
    # Explicit project allowlist: no workspace credentials, hidden dirs or caches.
    selected=[p for p in ROOT.iterdir() if p.is_file() and p.suffix in ('.md','.json')]
    for dirname in ('lab','scripts','schemas','tests','sources','data','research'):
        selected.extend(p for p in (ROOT/dirname).rglob('*') if p.is_file() and not p.is_symlink()
                        and '__pycache__' not in p.parts and p.suffix!='.pyc' and p not in large)
    for p in sorted(set(selected)):
        target=DEST/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
    (DEST/'DATA_RESTORE_BLUEPRINTS.json').write_bytes(encoded(plan))
    readme='''# Phase2 审查入口

研究内容：延续已有Investment Research Lab，冻结失败通用择时规则，分类原282与扩展374成熟12m结果；两个经济条件、固定配置残差、placebo/扰动、Price-In与行业逻辑。

最重要结论：NO EVIDENCE OF GENERIC TIMING EDGE；NO CONDITIONAL EDGE ESTABLISHED。C1脆弱（2触发），C2只有1触发；random-date条件N0，PLACEBO_NOT_EVALUABLE。没有A级/B-/C晋升，没有新增操作性投资原则。

失败结论：原趋势先验未稳定优于固定概率；weeklySPY/BIL没有证明优于50/50、60/40、70/30。相对全股票减回撤不能冒充增量择时能力。原失败锁与记录保留。

当前候选：RETURN EDGE候选0；RRC-001只是D级相对全股票风险观察，固定50/50构成重要反证。资料不足的盈利、估值、信用、资本周期机制尚未被验证或证伪。

人工优先阅读：

1. CONDITIONAL_EDGE_REPORT.md（17个核心回答）
2. ERROR_TAXONOMY.md（False Positive / False Negative与真实缺口）
3. SURVIVING_CANDIDATES.md、FAILED_HYPOTHESES.md
4. research/phase2/conditional.interpretation.v001.md（脆弱性与发布时间边界）
5. research/phase2/benchmarks.results.v002.md（主与敏感性费用、固定配置残差）
6. REGIME_DEPENDENCE_REPORT.md、PRICE_IN_FRAMEWORK.md、INDUSTRY_SPECIFIC_RULES.md
7. SELL_FRAMEWORK.md、NO_TRADE_FRAMEWORK.md
8. NIGHT_RESEARCH_REPORT.md、research/status/LATEST.md
9. research/audit/PHASE2_QUALITY_SCIENTIFIC_REVIEW.v001.md（独立QC）

下一步：小连续信用/融资、原财务与历史预期/估值序列；固定下跌起点和负对照；补足随机日期之前的原宏观发布，不重抽直到好看。不继续调整失败通用规则。

数据/证据边界：430选择记录、377有效预测、374成熟12m、53不足历史、3待成熟12m；43日期/23年份，独立N未知。Phase2没有新增Historical Replay/概率预测。报价是当前供应商的历史重构，非原始quote vintage或真正前瞻盲测；原公告与两SEC filings另有发布时间证据。合成工程资料不算投资证据。

可复现性：本包包含全部重要报告、源字节、源清单、脚本、原预测/锁/标签、案例报告及checkpoint。避免重复存储约1.6GB行政bundle/输入，每个原文件以无损blueprint引用同一份canonical历史；所有原哈希保持不变。DATA_RESTORE_BLUEPRINTS.json不是新数据或修改过的输入。

在包根目录运行 `python3 scripts/restore_export_inputs.py --verify-only`，可不联网重构并核对全部原SHA而不写重复大文件；要恢复完整研究文件运行 `python3 scripts/restore_export_inputs.py`。已有文件只核验不覆盖。120个不合格pilot始终不准入，即使恢复也不成为合法案例。默认审查无需恢复大文件；需要运行原A/B程序前恢复，并按各原selection/prereg路径操作，原A重跑只核验不得改预测。

EXPORT_MANIFEST.json记录复制文件哈希；EXPORT_RESTORE_VERIFICATION.json记录重构验证；根目录保留原研究布局，历史ROUND001零数据快照是归档，不是当前状态。原供应商快照下载/公司行动局限详见DATA_SOURCE_CATALOG与DATA_INVENTORY。
'''
    (DEST/'README_FOR_REVIEW.md').write_text(readme,encoding='utf-8')
    verification=restore(DEST,verify_only=True)
    (DEST/'EXPORT_RESTORE_VERIFICATION.json').write_bytes(encoded(verification))
    manifest={'exported_at':datetime.now().astimezone().isoformat(),'original_project':str(ROOT),
              'deduplicated_original_files':len(plan['files']),'restore_verification':verification,'files':[]}
    for p in sorted(DEST.rglob('*')):
        if p.is_file() and p.name!='EXPORT_MANIFEST.json':
            manifest['files'].append({'path':str(p.relative_to(DEST)),'size_bytes':p.stat().st_size,'sha256':sha(p)})
    (DEST/'EXPORT_MANIFEST.json').write_bytes(encoded(manifest))
    temp=ZIP.with_suffix('.tmp.zip')
    with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(DEST)))
    with zipfile.ZipFile(temp) as z:
        assert z.namelist() and z.testzip() is None
        for name in ['README_FOR_REVIEW.md','CONDITIONAL_EDGE_REPORT.md','ERROR_TAXONOMY.md',
                     'INDUSTRY_SPECIFIC_RULES.md','PRICE_IN_FRAMEWORK.md','SELL_FRAMEWORK.md',
                     'NO_TRADE_FRAMEWORK.md','REGIME_DEPENDENCE_REPORT.md','SURVIVING_CANDIDATES.md']:
            assert name in z.namelist(),name
    assert temp.stat().st_size>0;temp.replace(ZIP)
    result={'zip_path':str(ZIP),'zip_bytes':ZIP.stat().st_size,'zip_sha256':sha(ZIP),
            'exported_files':len(manifest['files'])+1,'restored_hashes_verified':len(plan['files']),
            'zip_integrity':'PASS','required_reports':'PASS'}
    (ZIP.parent/'Investment_Research_Lab_Phase2.export_verification.json').write_bytes(encoded(result))
    print(json.dumps(result))

if __name__=='__main__':export()
