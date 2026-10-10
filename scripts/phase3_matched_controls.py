#!/usr/bin/env python3
"""New, post-panel falsification: same-quarter economic-class contrasts.

This does not change any old experiment, run a strategy, rescue the failed
credit gate, or claim fresh out-of-sample evidence. All contrasts are retained.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.phase3_analyze import rows_from_labels,VARIABLES,summary,clean
OUT=ROOT/'research/phase3/matched';OUT.mkdir(parents=True,exist_ok=True)
PATHS=['research/phase3/features/decision_points.v001.json','research/phase3/labels/development.v001.json','research/phase3/labels/holdout.v001.json','research/phase3/analysis/development.lock.v001.json','research/phase3/analysis/holdout.lock.v001.json','scripts/phase3_analyze.py',__file__]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,d):
    b=(json.dumps(clean(d),ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    with Path(p).open('xb') as f:f.write(b)
def klass(r):
    if r['industry'] in ['Broad','Growth','Technology','Semiconductor','Financials_Banks','Industrials','Consumer','Healthcare','Energy_Resources','Utilities']:return 'EQUITY'
    if r['industry'].startswith('Treasury_'):return 'TREASURY_DURATION'
    return r['industry']
def register():
    save(OUT/'PREREGISTRATION.v001.json',{'hypothesis_id':'H-P3-MATCHED-CONTROLS-v001','registered_at':datetime.now(timezone.utc).isoformat(),'stage':'EXPLORATORY_FALSIFICATION_AFTER_ALL_MAIN_RESULTS_KNOWN','why':'Raw drawdown mean advantage shrank after date weighting; high-vol24m interval can reflect composition, common regimes or risk premium. Attack by within-quarter class contrasts, no parameter changes.','sources':{str(Path(x).resolve().relative_to(ROOT)):sha(ROOT/x) for x in PATHS},'horizons':['12m','24m'],'variables':list(VARIABLES),'strata':'market x currency x economic class x return basis, never across incompatible local returns','equity_classes':['Broad','Growth','Technology','Semiconductor','Financials_Banks','Industrials','Consumer','Healthcare','Energy_Resources','Utilities'],'treasury_class':['IEF','TLT','SHY'],'matching':'Only quarters with both groups. Difference of equal-asset group means within that exact quarter and stratum, then equal quarters. No outcome used to match. Singleton/no-opposite strata explicitly unavailable.','paired_SPY_residual':'For US equities only SAME_EXECUTION benchmark labels; still not beta/volatility-risk-matched alpha.','MDD':'same primary gross economic daily-close measure in both sides, not net fixed-allocation MDD','bootstrap':{'replicates':500,'seed':20261009,'unit':'joint two-calendar-year blocks','independent_n':None},'credit_interaction':'Original gate remains NOT_RUN_GATE_FAILED; these are single-variable controls, not an alternative credit+drawdown strategy','new_labels_or_probabilities':0,'no_threshold_or_period_changes':True,'multiple_testing':'4 variables x 2 horizons x all fixed strata; exploratory, no promotion based on lucky cell'})
    print('matched-control method locked before new comparator computation')
def ci(cells,key):
    if not cells:return {'mean':None,'ci95':None,'blocks':0,'status':'NOT_IDENTIFIED_NO_BOTH_GROUPS'}
    by={}
    for c in cells:by.setdefault((c['year']-2000)//2,[]).append(c[key])
    blocks=sorted(by);s=np.array([sum(by[b]) for b in blocks]);n=np.array([len(by[b]) for b in blocks]);idx=np.random.default_rng(20261009).integers(0,len(blocks),size=(500,len(blocks)));v=s[idx].sum(1)/n[idx].sum(1)
    return {'mean':np.mean([c[key] for c in cells]),'ci95':np.quantile(v,[.025,.975]).tolist(),'blocks':len(blocks),'status':'DESCRIPTIVE_NOT_CAUSAL' if len(blocks)>=4 else 'UNRELIABLE_FEWER_THAN_4_BLOCKS'}
def run():
    reg=read(OUT/'PREREGISTRATION.v001.json')
    for p,h in reg['sources'].items():assert sha(ROOT/p)==h,p
    features=read(ROOT/PATHS[0])['points'];rows=[]
    for part in ['development','holdout']:rows+=rows_from_labels(features,read(ROOT/f'research/phase3/labels/{part}.v001.json'),part)
    strata=sorted({(r['market'],r['currency'],klass(r),r['return_basis']) for r in rows})
    results=[];allcells=[]
    for st in strata:
        for v in VARIABLES:
            for h in ['12m','24m']:
                groups={}
                for r in rows:
                    if r['horizon']!=h or not r['feature_eligible'] or r['label_status']!='REVEALED' or r['groups'][v] is None or (r['market'],r['currency'],klass(r),r['return_basis'])!=st:continue
                    groups.setdefault(r['calendar_quarter'],{0:[],1:[]})[r['groups'][v]].append(r)
                cells=[];residual=[]
                for q,g in sorted(groups.items()):
                    if not g[0] or not g[1]:continue
                    c={'stratum':st,'variable':v,'horizon':h,'quarter':q,'year':int(q[:4]),'n_group1':len(g[1]),'n_group0':len(g[0]),'return_difference':float(np.mean([r['net_return'] for r in g[1]])-np.mean([r['net_return'] for r in g[0]])),'mdd_difference':float(np.mean([r['max_drawdown'] for r in g[1]])-np.mean([r['max_drawdown'] for r in g[0]])),'point_ids_group1':[r['point_id'] for r in g[1]],'point_ids_group0':[r['point_id'] for r in g[0]]};cells.append(c)
                    if st[0]=='US' and st[2]=='EQUITY':
                        b=[[r['benchmark_differences'].get('PAIRED_ASSET_BENCHMARK') for r in g[k] if r['benchmark_differences'].get('PAIRED_ASSET_BENCHMARK') is not None] for k in [1,0]]
                        if b[0] and b[1]:residual.append(dict(c,return_difference=float(np.mean(b[0])-np.mean(b[1]))))
                r={'stratum':st,'variable':v,'horizon':h,'RAW_OBSERVATIONS':sum(len(g[0])+len(g[1]) for g in groups.values()),'matched_raw_observations':sum(c['n_group1']+c['n_group0'] for c in cells),'both_group_quarters':len(cells),'EFFECTIVE_SAMPLE_ASSESSMENT':{'n_effective':None,'global_regime_dependence':True,'overlapping_forward_returns':True,'within_quarter_sector_correlation':True},'return_contrast':ci(cells,'return_difference'),'gross_MDD_contrast':ci(cells,'mdd_difference'),'quarter_difference_distribution':summary([c['return_difference'] for c in cells]),'SPY_residual_contrast':ci(residual,'return_difference'),'missing_opposite_group_quarters':sum(not g[0] or not g[1] for g in groups.values()),'alpha_identified':False};results.append(r);allcells+=cells
    body={'hypothesis_id':reg['hypothesis_id'],'results':results,'matched_cells':allcells,'comparison_slots':len(results),'identified_comparisons':sum(r['both_group_quarters']>0 for r in results),'RAW_OBSERVATIONS':'Reused main panel, zero new decision points or forecasts','EFFECTIVE_SAMPLE_ASSESSMENT':{'n_effective':None,'matched_dates_do_not_remove_asset_beta_or_global_regime':True},'investment_principles_promoted':0,'credit_gate_rerun':False}
    save(OUT/'RESULTS.v001.json',body);save(OUT/'RESULTS.lock.v001.json',{'result_sha256':sha(OUT/'RESULTS.v001.json'),'registered_sha256':sha(OUT/'PREREGISTRATION.v001.json'),'completed_at':datetime.now(timezone.utc).isoformat()})
    lines=['# 同季度、同类资产反证','', 'H-P3-MATCHED-CONTROLS-v001；主面板结果已知后的探索性反证，不是新OOS，不改原门槛/结果。','', 'RAW OBSERVATIONS：复用2087成熟12m/1995成熟24m候选行（准确口径以主报告为准）；新增决策点/预测=0。EFFECTIVE SAMPLE ASSESSMENT：独立N未知；同季度成对去部分共同时间影响，但行业beta、风险与共同全球周期未识别。','', '|类层|变量|期限|双方季度|组间净收益差|两年块区间|gross MDD差|','|---|---|---|---:|---:|---|---:|']
    for r in results:
        if r['stratum'][0]!='US' or r['stratum'][2] not in ['EQUITY','TREASURY_DURATION']:continue
        c=r['return_contrast'];iv=c['ci95'];lines.append('|'+ '|'.join([r['stratum'][2],r['variable'],r['horizon'],str(r['both_group_quarters']),'UNKNOWN' if c['mean'] is None else f"{c['mean']*100:.2f}pp",'UNKNOWN' if iv is None else f'[{iv[0]*100:.2f},{iv[1]*100:.2f}]pp','UNKNOWN' if r['gross_MDD_contrast']['mean'] is None else f"{r['gross_MDD_contrast']['mean']*100:.2f}pp"])+'|')
    lines+=['','所有市场/类层/失败与无对组格保存在RESULTS.v001.json，不删除singleton。美国SLOOS同一季度复用于全部US资产，无法在同date横截面识别其独立作用；这不把原数据门槛失败当作信用理论被证伪。','SPY残差不是严格beta/risk-matched alpha；这里不提出持仓或买卖规则，不把一次正区间升级原则。', '源码、方法、来源及结果各有独立锁。']
    (OUT/'REPORT.v001.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'comparison_slots':len(results),'identified':body['identified_comparisons'],'new_decision_points':0,'new_principles':0}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['register','run']);a=p.parse_args();register() if a.stage=='register' else run()
