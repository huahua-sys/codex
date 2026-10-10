#!/usr/bin/env python3
"""Append-only sensitivity of a known exploratory association, never a strategy."""
import argparse, json, sys
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from scripts.phase3_matched_controls import sha, read, save, ci, klass
from scripts.phase3_analyze import rows_from_labels, summary
OUT=ROOT/'research/phase3/vol_falsification'; OUT.mkdir(parents=True,exist_ok=True)
ASSETS=['SPY','QQQ','XLK','SOXX','KBE','XLI','XLY','XLV','XLE','XLU']
PATHS=['research/phase3/features/decision_points.v001.json','research/phase3/labels/development.v001.json','research/phase3/labels/holdout.v001.json','research/phase3/matched/RESULTS.v001.json','scripts/phase3_matched_controls.py','scripts/phase3_analyze.py','scripts/phase3_vol_falsification.py']
def register():
    save(OUT/'PREREGISTRATION.v001.json',{'hypothesis_id':'H-P3-VOL-FALSIFICATION-v001','registered_at':datetime.now(timezone.utc).isoformat(),'prior_results_known':True,'purpose':'Attack positive US same-quarter volatility association: sector composition, temporal overlap, era stability. All deletion controls reported; none used to choose assets, thresholds or strategy.','sources':{p:sha(ROOT/p) for p in PATHS},'assets':ASSETS,'variable':'H-P3-VOL','horizons':['12m','24m'],'variants':['ALL']+['OMIT_'+a for a in ASSETS],'eras':['ALL','2000-2009','2010-2019','2020-2025'],'estimand':'Same-quarter equal-asset high-minus-not-high net holding return, then equal quarters. Gross MDD measured consistently.','nonoverlap':'ALL assets only: greedily choose earliest both-group quarter whose earliest entry is strictly after latest exit of previously chosen quarter; applies across all US equity rows and both partitions jointly. Keeps actual session endpoint dates. Time gaps/selected subset disclosed, not independent world count.','bootstrap':'500 fixed-seed 20261009 joint two-calendar-year blocks; descriptive intervals, not multiple-testing corrected','comparison_slots':88,'nonoverlap_slots':2,'new_samples':0,'new_probabilities':0,'alpha_identified':False,'do_not_promote_on_positive_interval':True})
    print('Registered all deletion/era/overlap checks before their computation')
def run():
    reg=read(OUT/'PREREGISTRATION.v001.json')
    for p,h in reg['sources'].items():assert sha(ROOT/p)==h,p
    features=read(ROOT/PATHS[0])['points']; rows=[]
    for part in ['development','holdout']:rows+=rows_from_labels(features,read(ROOT/f'research/phase3/labels/{part}.v001.json'),part)
    out=[]; nonoverlap=[]
    for h in ['12m','24m']:
        for variant in reg['variants']:
            omit=variant[5:] if variant.startswith('OMIT_') else None
            for era in reg['eras']:
                qgroups={}
                for r in rows:
                    if r['asset_id'] not in ASSETS or r['asset_id']==omit or r['horizon']!=h or not r['feature_eligible'] or r['label_status']!='REVEALED' or r['groups']['H-P3-VOL'] is None:continue
                    if era!='ALL' and not int(era[:4])<=r['year']<=int(era[5:]):continue
                    qgroups.setdefault(r['calendar_quarter'],{0:[],1:[]})[r['groups']['H-P3-VOL']].append(r)
                cells=[]
                for q,g in sorted(qgroups.items()):
                    if not g[0] or not g[1]:continue
                    rr=g[0]+g[1]
                    cells.append({'quarter':q,'year':int(q[:4]),'n_raw':len(rr),'point_ids':[r['point_id'] for r in rr],'entry':min(r['entry_date'] for r in rr),'exit':max(r['exit_date'] for r in rr),'return_difference':float(np.mean([r['net_return'] for r in g[1]])-np.mean([r['net_return'] for r in g[0]])),'mdd_difference':float(np.mean([r['max_drawdown'] for r in g[1]])-np.mean([r['max_drawdown'] for r in g[0]]))})
                result={'horizon':h,'variant':variant,'era':era,'n_raw':sum(c['n_raw'] for c in cells),'both_group_quarters':len(cells),'return_contrast':ci(cells,'return_difference'),'gross_MDD_contrast':ci(cells,'mdd_difference'),'quarter_difference_distribution':summary([c['return_difference'] for c in cells]),'cells':cells,'n_effective':None}
                out.append(result)
                if variant=='ALL' and era=='ALL':
                    selected=[]; end=None
                    for c in cells:
                        if end is None or c['entry']>end:selected.append(c);end=c['exit']
                    nonoverlap.append({'horizon':h,'n_raw':sum(c['n_raw'] for c in selected),'both_group_quarters':len(selected),'return_contrast':ci(selected,'return_difference'),'gross_MDD_contrast':ci(selected,'mdd_difference'),'quarter_difference_distribution':summary([c['return_difference'] for c in selected]),'cells':selected,'n_effective':None,'caveat':'Actual held periods do not overlap; common global/sector regime dependence and small selective calendar coverage remain.'})
    save(OUT/'RESULTS.v001.json',{'hypothesis_id':reg['hypothesis_id'],'comparisons':out,'nonoverlap':nonoverlap,'comparison_slots':len(out),'nonoverlap_slots':len(nonoverlap),'new_samples':0,'new_predictions':0,'investment_principles':0,'alpha_identified':False})
    save(OUT/'RESULTS.lock.v001.json',{'completed_at':datetime.now(timezone.utc).isoformat(),'preregistration_sha256':sha(OUT/'PREREGISTRATION.v001.json'),'results_sha256':sha(OUT/'RESULTS.v001.json')})
    lines=['# 相对波动关联的后续反证','','RAW OBSERVATIONS：复用原面板，新决策点/预测=0。EFFECTIVE SAMPLE ASSESSMENT：独立N未知；不重叠持有期也不等于独立经济世界。','主结果及matched结果已知以后另登记；探索性敏感度，全部10遗漏对照×4年代×2期限保留，不按最好结果选资产。没有策略优化、三变量组合或未来OOS。','','|期限|遗漏对照|年代|双方季度|净差pp|块区间pp|gross MDD差pp|','|---|---|---|---:|---:|---|---:|']
    def show(r,name,era):
        c=r['return_contrast']; iv=c['ci95']; m=r['gross_MDD_contrast']['mean']
        return '|'+ '|'.join([r['horizon'],name,era,str(r['both_group_quarters']),'UNKNOWN' if c['mean'] is None else f"{100*c['mean']:.2f}",'UNKNOWN' if iv is None else f'[{100*iv[0]:.2f},{100*iv[1]:.2f}]','UNKNOWN' if m is None else f'{100*m:.2f}'])+'|'
    lines += [show(r,r['variant'],r['era']) for r in out]
    lines += ['','## 实际跨分区无重叠起点','','|期限|对照|范围|双方季度|净差pp|块区间pp|gross MDD差pp|','|---|---|---|---:|---:|---|---:|']+[show(r,'GREEDY_STRICT_NO_OVERLAP','ALL') for r in nonoverlap]
    lines += ['','删掉一个行业的正值不证明alpha；同类ETF不同duration、beta、风险溢价、行业资本周期仍未被识别。不得将未来收益估计的风险解释反填到过去信号。全分布和具体point IDs见锁定JSON；CI没有multiple testing校正，少于4时间块不可推断。']
    (OUT/'REPORT.v001.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'comparison_slots':len(out),'nonoverlap':[{k:r[k] for k in ['horizon','both_group_quarters','return_contrast']} for r in nonoverlap]}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['register','run']);a=p.parse_args();register() if a.stage=='register' else run()
