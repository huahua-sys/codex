#!/usr/bin/env python3
"""Human-readable A/B dossiers, with explicit outcome separation and no new forecasts."""
import json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/phase4'
def text(v):
    if v is None:return 'UNKNOWN / NOT_IDENTIFIED'
    if isinstance(v,(list,dict)):return json.dumps(v,ensure_ascii=False)
    return str(v)
def pc(v):return 'NA' if v is None else f'{100*v:.2f}%'
def main():
    es=json.loads((BASE/'data/events.all.v001.json').read_text())['events']
    ls=json.loads((BASE/'labels/event_reactions.v001.json').read_text())['records']
    labels={l['event_id']:l for l in ls}
    output=ROOT/'BEHAVIORAL_EVENT_LIBRARY';output.mkdir(exist_ok=True)
    index=['# 行为事件库 — Phase4 v001','',
           'A记录先source-first锁定，随后计算B价格反应。历史已知/模型记忆风险存在；非真正盲测。',
           'JSON原证据：research/behavioral_events；Evidence Card：research/evidence_cards。',
           '收益是供应商重构的open/close价格收益，分红未包含。公司事件的宽基反应不能当公司收益或主体效果。','',
           '|Event|Market|Family|Action|Published|Parent|PIT|','|---|---|---|---|---|---|---|']
    groups=defaultdict(list)
    for e in es:groups[(e['market'],e['family'])].append(e)
    for e in es:
        eid=e['event_id'];l=labels[eid]
        lines=[f'# {eid} — {e["market"]} / {e["family"]}','',
               '## STAGE A — KNOWN_AT_T（原始锁定记录只读）','']
        for name in ['published_date','available_at','participant_type','constraint','trigger',
                     'observed_action','action_status','action_type','flow_size','flow_duration',
                     'assets','voluntary_or_forced','price_sensitive','information_based',
                     'pit_status','publication_date_evidence','source_file_hashes']:
            lines.append(f'- **{name}**：{text(e.get(name))}')
        lines+=['','当时已知：','']+[f'- {text(v)}' for v in e['known_at_t']]
        lines+=['','当时未知：','']+[f'- {text(v)}' for v in e['unknown_at_t']]
        lines+=['','原资料：','']+[f'- {u}' for u in e.get('source_urls',[])]
        lines+=['','## STAGE B — KNOWN_ONLY_AFTER_T（结果标签）','',
                f'量化范围：{l["asset"]}宽基价格context；{l["status"]}。',
                '此处不是个股资本分配回报、真实赎回证券损失或因果效果。','',
                '|Horizon|Entry→Exit|Gross price|Matched time difference|MAE(close)|MFE(close)|','|---|---|---|---|---|---|']
        for h,b in l.get('horizons',{}).items():
            r=b['event'];lines.append('|'+ '|'.join([h,f'{r.get("entry_date","NA")}→{r.get("exit_date",r["status"])}',
                pc(r.get('gross_price_return')),pc(b['matched_time_difference']),
                pc(r.get('maximum_adverse_close_excursion')),pc(r.get('maximum_favorable_close_excursion'))])+'|')
        similar=[q for q in groups[(e['market'],e['family'])] if q['event_id']!=eid]
        similar=sorted(similar,key=lambda q:(abs((__import__('datetime').date.fromisoformat(q['published_date'])-__import__('datetime').date.fromisoformat(e['published_date'])).days),q['event_id']))[:3] if e.get('published_date') and all(q.get('published_date') for q in similar) else similar[:3]
        lines+=['','## 机制与最接近对照','',
                f'机制假说：{text(e.get("mechanism"))}',
                f'替代解释：{text(e.get("alternative_explanation"))}',
                f'否证：{text(e.get("falsifier"))}',
                'Temporary Mispricing / Structural Deterioration / Mixed：**UNCLEAR / NOT_IDENTIFIED**。没有独立的持有人资金缺口及资产现金流/偿付证据，不能按后来反弹分类。',
                'Counterfactual：季度同资产价格状态匹配仅描述，缺估值、资产信用、真正暴露强度及无干预组；不可称因果对照。',
                'Closest Similar Events（同市场同族、发布日期最近三条，未按结果选择）：'+', '.join(q['event_id'] for q in similar),
                'Similarities：相同参与者/制度族；Differences：具体约束、执行阶段、实际规模、剩余容量及经济环境须看各原卡，不能仅凭相似标题类比。',
                'Generalization：尚未成立；相同program/company、相邻披露、全球regime使独立N未知。',
                '概率预测：0新增；证据/机制可信度与上涨概率不相同。','']
        lines+=['|Case|Date|Constraint|Observed Action|Size / Basis|Duration|3m price (after-T)|',
                '|---|---|---|---|---|---|---|']
        for q in [e]+similar:
            result=labels[q['event_id']].get('horizons',{}).get('3m',{}).get('event',{})
            cells=[q['event_id'],q.get('published_date'),q.get('constraint'),q.get('observed_action'),
                   q.get('flow_size'),q.get('flow_duration'),pc(result.get('gross_price_return'))]
            lines.append('|'+ '|'.join(text(v).replace('|','/').replace('\n',' ') for v in cells)+'|')
        lines+=['','经济差异表直接引用原卡：金额的scope/交割阶段不同不可合并。3m价格差是结果，不是“真正决定结果的变量”；在没有信用/估值/经营证据时保持未识别。','']
        (output/f'{eid}.md').write_text('\n'.join(lines))
        index.append(f'|[{eid}]({eid}.md)|{e["market"]}|{e["family"]}|{e["action_status"]}|{e.get("published_date")}|{e["parent_episode"]}|{e["pit_status"]}|')
        (ROOT/f'research/behavioral_events/{eid}.outcome.v001.json').write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n')
    (output/'INDEX.md').write_text('\n'.join(index)+'\n')
    print(f'{len(es)} human dossiers generated; original A records untouched.')
if __name__=='__main__':main()
