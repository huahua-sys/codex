#!/usr/bin/env python3
"""Refresh current indexes while appending cycle records; never mutate A/B locks."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lab.schema import read_json,utc_now,write_once
ROOT=Path(__file__).resolve().parents[1]
BATCHES=['ROUND_002_V003','NIGHT_XTIME_V003','NIGHT_SECTOR_V002','NIGHT_XASSET','NIGHT_ASHARE','NIGHT_EARLY','NIGHT_RECENT','NIGHT_CALENDAR_CONTROL']

def append(name,text):
    p=ROOT/name;p.write_text(p.read_text()+'\n'+text+'\n',encoding='utf-8')

def checkpoint(cycle,status):
    now=utc_now(); rows=[]; summaries={}
    for batch in BATCHES:
        base=ROOT/'research/replays'/batch
        sp=base/'run/evaluation_summary.v001.json'
        if not sp.exists():continue
        summaries[batch]=read_json(sp)
        for e in read_json(base/'selection.v001.json')['episodes']:
            eid=e['episode_id'];p=read_json(base/'run/predictions'/f'{eid}.v001.json')
            label=read_json(base/'run/labels'/f'{eid}.v001.json')
            rows.append((batch,e,p,label))
    mature=sum(x[3].get('horizons',{}).get('12m',{}).get('status')=='REVEALED' for x in rows)
    unresolved=len(rows)-mature;clusters=len({x[1]['cutoff_at'] for x in rows})
    insufficient=sum(not x[2].get('horizons') for x in rows)
    pending=unresolved-insufficient
    years=len({x[1]['cutoff_at'][:4] for x in rows})
    snapshot={'at':now,'cycle':cycle,'status':status,'selected_rows':len(rows),
              'mature_12m_rows':mature,'unresolved_12m_rows':unresolved,'shared_date_clusters':clusters,
              'valid_forecast_rows':len(rows)-insufficient,'insufficient_history_rows':insufficient,
              'pending_12m_rows':pending,'shared_calendar_years':years,
              'batches':summaries,'old_candidates_tested':0,'new_candidates':0,'validated_principles':0}
    write_once(ROOT/'research/checkpoints'/f'{cycle}.json',snapshot)
    f=read_json(ROOT/'CURRENT_FRAMEWORK.json')
    f.update(framework_version='0.2.0-research',last_updated=now,data_status='LIMITED_REAL_RECONSTRUCTED_QUOTES_AND_OFFICIAL_RELEASES')
    f['current_round'].update(status=status,ex_ante_judgment_locked=True,future_labels_revealed=True,
        actual_outcome='NO_ROBUST_PATTERN_YET',calibration_result='UNFITTED_PRIORS_NO_VALIDATED_CALIBRATION',
        valid_selection_rows=len(rows),mature_12m_rows=mature,shared_date_clusters=clusters)
    f['research_execution']={'latest_checkpoint':f'research/checkpoints/{cycle}.json',
        'valid_batches':list(summaries),'strict_quote_vintage_certified':False,'prospective_blind_test':False,
        'invalid_metadata_pilot_locks':120,'operational_framework_changed':False,'new_principles':[]}
    f['phase_status'].update(phase_2='MASKED_RULE_REPLAY_EXECUTED',phase_3='EXPLORATORY_COUNTEREXAMPLES_AND_CALIBRATION',
        phase_4='ORIGINAL_15_UNTESTED_NO_NEW_PRINCIPLE',phase_5='INDEPENDENT_BATCHES_NOT_PROSPECTIVE')
    (ROOT/'CURRENT_FRAMEWORK.json').write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n')
    intro=f'更新时间 {now}；{len(rows)} 个选择行，{len(rows)-insufficient} 条有效预测，{mature} 个成熟12m价格标签，{insufficient} 个不足历史行，{pending} 个12m尚未成熟行；{clusters} 个共享日期簇、{years} 个日历年份。日期和期限重叠，独立N未知。固定规则、宽概率先验、费用与现金假设均未经校准。原15假设仍未测试。\n'
    prediction=['# 预测总账\n',intro,'120个metadata泄漏pilot锁永久保留但不计入；未来不得修改已锁A。真实结果基于当前供应商历史序列重构，非原始quote vintage。所有期限使用5/21/63/126/252/504 session。\n',
      '|Episode|T / Asset|趋势 / p(up)|1w|1m|3m|6m|12m|24m|A / B|',
      '|---|---|---|---:|---:|---:|---:|---:|---:|---|']
    index=['# 历史案例索引\n',intro,'案例选择由日历全网格决定。结果类型由B揭晓后描述，不按结果补案例。跨币种数字是本币标签，不是可汇总投资组合。\n',
      '|Episode|Market / asset|Cutoff|Status|独立A / B / Episode|','|---|---|---|---|---|']
    for batch,e,p,l in rows:
        eid=e['episode_id'];a=f'research/replays/{batch}/run/predictions/{eid}.v001.md';b=f'research/replays/{batch}/run/labels/{eid}.v001.json'
        report=f'research/episode_library/{batch}/{eid}.md'
        pp=p.get('horizons',{}).get('12m',{}).get('p_up_scoring_probability')
        returns=[]
        for h in ('1w','1m','3m','6m','12m','24m'):
            r=l.get('horizons',{}).get(h,{})
            returns.append(f"{r['net_return']:.2%}" if r.get('status')=='REVEALED' else r.get('status','UNRESOLVED'))
        trend=p.get('regime','INSUFFICIENT')
        prediction.append(f"|{eid}|{e['cutoff_at'][:10]} / {e['asset_id']}|{trend} / {pp}|"+'|'.join(returns)+f'|[A]({a}) / [B]({b})|')
        extra=f' / [报告]({report})' if (ROOT/report).exists() else ''
        index.append(f"|{eid}|{e['market']} / {e['asset_id']}|{e['cutoff_at'][:10]}|{l['status']}|[A]({a}) / [B]({b}){extra}|")
    (ROOT/'PREDICTION_LEDGER.md').write_text('\n'.join(prediction)+'\n')
    (ROOT/'EPISODE_INDEX.md').write_text('\n'.join(index)+'\n')
    append('RESEARCH_LEDGER.md',f'## {cycle} — {now}\n\n{intro}\n状态 {status}；全锁先于B，V003已独立QA。工程失败见PIT_METADATA_LEAK_PILOT_INVALID；未修改旧预测。证据：[checkpoint](research/checkpoints/{cycle}.json)。投资结论 NO ROBUST PATTERN YET；继续反例与现金研究。')
    append('CHANGELOG.md',f'## {cycle} — {now}\n\n追加夜间checkpoint；更新索引与运行状态，{mature}成熟12m标签/{clusters}日期簇。投资框架权重与validated_principles保持不变。')
    append('CANDIDATE_PRINCIPLES.md',f'## {cycle} checkpoint\n\n{mature}个成熟12m标签用于新增固定趋势规则的探索性研究，未检验原15条盈利/估值/信用机制；原15文件保持原哈希。本cycle新增候选0，尚未证明可重复概率优势。')
    append('HYPOTHESIS_REGISTRY.md',f'## {cycle} — 新执行范围\n\nN-H-001 / R002-TREND-PRIOR-v001：63+252已知财富比率正/负组合是否改善12m概率与风险选择；冻结参数0次搜索。已执行{mature}个成熟标签，依赖{clusters}日期簇；EXPLORATORY_MASKED_NOT_PROSPECTIVE。原H-001–015仍未测，不能将趋势代理当其验证。')
    append('FAILED_HYPOTHESES.md',f'## {cycle} — 失败保存\n\nENGINEERING_FAILURE：120个v001/v002 pilot锁输入有未来metadata/counts，未揭晓、全部保留且排除。新V003同rule重锁后QA通过；详见[记录](research/audit/PIT_METADATA_LEAK_PILOT_INVALID.md)。市场规则的失效边界另在night分析中保留，不泛化为所有趋势无效。')
    append('OPEN_QUESTIONS.md',f'## {cycle} — 进度与新问题\n\nOQ-001部分解决：真实小数据已建立，但历史quote vintage、信用初始数据、预期/估值/行业基本面仍缺。OQ-008现金与sell正在独立研究。OQ-N01：负趋势后快速恢复是否解释WAIT漏掉赢家？需事前识别可观察条件，不能看反弹后选日期。OQ-N02：现金机会成本/持有期限/费用是否改变WAIT含义？OQ-N03：同趋势下盈利/信用/隐含预期能否区分相反结果？此轮趋势价格不足以识别。')
    (ROOT/'research/status/LATEST.md').write_text(f'# 最新研究状态\n\n{status} — {now}\n\n{intro}\n\n最新checkpoint：[{cycle}](../checkpoints/{cycle}.json)。主24例完成后已扩展，仍持续循环。NO ROBUST PATTERN YET；没有修改投资框架或晋升原则。未来输入严格隔离，但quote为当前供应商重构且历史先验可能污染，不能称真正前瞻盲测。\n')
    print(json.dumps({k:v for k,v in snapshot.items() if k!='batches'}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cycle',required=True);p.add_argument('--status',default='AUTONOMOUS_NIGHT_RESEARCH_RUNNING')
    a=p.parse_args();checkpoint(a.cycle,a.status)
