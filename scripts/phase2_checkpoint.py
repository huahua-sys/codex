#!/usr/bin/env python3
"""Finalize Phase2 memory without touching frozen models, inputs or outcomes."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lab.schema import read_json,sha256,utc_now,write_once
ROOT=Path(__file__).resolve().parents[1]

def append(path,text):
    p=ROOT/path;p.write_text(p.read_text()+'\n'+text+'\n',encoding='utf-8')

def main():
    now=utc_now();f=read_json(ROOT/'CURRENT_FRAMEWORK.json')
    old=read_json(ROOT/'research/archive/ROUND_001/CURRENT_FRAMEWORK.json')
    protected=['validated_principles','candidate_principles','active_hypotheses','regime_rules',
               'industry_specific_rules','signals_to_monitor','sell_signals','risk_signals','price_in_checks']
    for k in protected:assert f[k]==old[k],k
    counts={'selection_rows':430,'valid_predictions':377,'mature_12m':374,'pending_12m':3,
            'mature_24m':359,'pending_24m':18,'insufficient_history':53,'date_clusters':43,
            'calendar_years':23,'independent_n':None,'new_phase2_replays':0,'new_phase2_predictions':0}
    reports=['ERROR_TAXONOMY.md','CONDITIONAL_EDGE_REPORT.md','INDUSTRY_SPECIFIC_RULES.md',
             'PRICE_IN_FRAMEWORK.md','SELL_FRAMEWORK.md','NO_TRADE_FRAMEWORK.md',
             'REGIME_DEPENDENCE_REPORT.md','SURVIVING_CANDIDATES.md','NIGHT_RESEARCH_REPORT.md']
    snapshot={'phase':'PHASE2_CONDITIONAL_EDGE','at':now,'status':'COMPLETE_NO_ESTABLISHED_EDGE',
        'counts':counts,'generic_timing':'NO_EVIDENCE_OF_GENERIC_TIMING_EDGE',
        'conditional_edge':'NO_CONDITIONAL_EDGE_ESTABLISHED','C1':'FRAGILE','C2':'INSUFFICIENT_INDEPENDENT_REGIMES',
        'random_date_placebo':'PLACEBO_NOT_EVALUABLE','new_candidate_principles':0,
        'new_validated_principles':0,'operational_framework_changed':False,
        'risk_observation':{'id':'RRC-001','confidence':'D','incremental_protection_established':False},
        'report_sha256':{r:sha256(ROOT/r) for r in reports},
        'prompt_sha256':sha256(ROOT/'sources/Codex_Investment_Research_Phase2_Conditional_Edge_Prompt.md')}
    out=ROOT/'research/checkpoints/PHASE2_FINAL.v001.json';write_once(out,snapshot)
    f.update(framework_version='0.3.0-phase2-research',last_updated=now,
             data_status='LIMITED_REAL_QUOTES_ORIGINAL_RELEASES_AND_TWO_ORIGINAL_FILINGS')
    f['current_round'].update(mode='PHASE2_CONDITIONAL_EDGE',status='COMPLETE_NO_ESTABLISHED_EDGE',
        actual_outcome='NO_EVIDENCE_OF_GENERIC_TIMING_EDGE_NO_CONDITIONAL_EDGE_ESTABLISHED',
        calibration_result='DESCRIPTIVE_UNCALIBRATED_PRIORS_NO_NEW_FORECASTS')
    f['research_execution'].update(latest_checkpoint='research/checkpoints/PHASE2_FINAL.v001.json',
        phase2_counts=counts,phase2_conditions={'Q-P2-C1':'FRAGILE','Q-P2-C2':'INSUFFICIENT_INDEPENDENT_REGIMES'},
        phase2_placebo_random_date_status='PLACEBO_NOT_EVALUABLE',risk_observation=snapshot['risk_observation'])
    f['documents'].update(phase2_report='CONDITIONAL_EDGE_REPORT.md',night_report='NIGHT_RESEARCH_REPORT.md',
        error_taxonomy='ERROR_TAXONOMY.md',surviving_candidates='SURVIVING_CANDIDATES.md')
    f['research_protocol_paths']['night_cohorts']='research/protocols/NIGHT_COHORTS_PROTOCOL.v001.md'
    for k in protected:assert f[k]==old[k],k
    (ROOT/'CURRENT_FRAMEWORK.json').write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n')
    # Historical narrative is explicitly scoped rather than silently erased.
    for name in ['HYPOTHESIS_REGISTRY.md','CANDIDATE_PRINCIPLES.md','FAILED_HYPOTHESES.md','DATA_INVENTORY.md','RESEARCH_LEDGER.md','OPEN_QUESTIONS.md']:
        p=ROOT/name;t=p.read_text();lines=t.splitlines()
        lines.insert(2,'> 当前Phase2状态：374成熟12m、377有效预测；没有通用/条件性优势证据，原15机制仍未测试。以下首段零资料/零执行等陈述为ROUND_001历史快照；本文件末尾是最新追加记录。')
        p.write_text('\n'.join(lines)+'\n')
    append('RESEARCH_LEDGER.md',f'## RL-P2-FINAL — {now}\n\n复用原282与扩展374结果，未新增Historical Replay/概率预测。完成错误分类、2经济组合、固定配置残差、601placebo条目/9扰动、8报告与night总结。16原宏观档+2原SEC报告/8facts已核；金融与CSI/Chi指数不足保留。C1脆弱、C2N1、随机日期条件N0，未晋升原则。\n\n更正CYCLE_003“56不足资料行”：实际53不足历史+3待成熟；原snapshot保留，CYCLE_004与本checkpoint已分开。\n\n[最终checkpoint](research/checkpoints/PHASE2_FINAL.v001.json)。下一步需要小连续信用/财务/预期序列；没有宣称全球DATA EXHAUSTED。')
    q=[('H-P2-001','估值便宜 + 盈利改善','同期估值与一致预期vintage'),
       ('H-P2-002','高估值 + 持续盈利上修','历史隐含增长、上修序列'),
       ('H-P2-003','基本面改善 + 趋势确认','先独立基本面信号；不救失败趋势规则'),
       ('H-P2-004','信用改善 + 错杀/抄底','历史信用初值、融资/现金流'),
       ('H-P2-005','高估值 + 信用收紧 + 盈利转负','三项同T数据及负对照'),
       ('H-P2-006','CapEx增加的行业现金回收差异','原资本投入/供给/合同/监管回收序列'),
       ('H-P2-007','极端悲观 + 基本面未恶化','当时positioning/情绪与原财务'),
       ('H-P2-008','实际合同/政策执行比讲话更有价值','执行/合同公开时间与当时预期')]
    body='## Phase2问题登记（理论待测，非新原则）\n\n|ID|命题|Status / 下一最小证据|\n|---|---|---|\n'
    for a,b,c in q:body+=f'|{a}|{b}|DATA_REQUIRED：{c}|\n'
    body+='|Q-P2-C1|高CPI + 年度政策下限增加，久期相对短债风险|EXECUTED_EXPLORATORY / FRAGILE / 2触发|\n|Q-P2-C2|高CPI + 近零政策利率，先预测政策变化|EXECUTED_EXPLORATORY / 1触发 / 无alpha证据|\n\n原H-001–015与CP/EXP文件不变，没有借相关价格结果验证这些机制。'
    append('HYPOTHESIS_REGISTRY.md',body)
    append('CANDIDATE_PRINCIPLES.md','## Phase2最终\n\n新增投资原则0；原15条仍未测，confidence与出处不变。RRC-001 D是相对全股票的风险观察，固定50/50提供反证，不是RETURN EDGE或增量风险原则。详见SURVIVING_CANDIDATES；没有A/B-/C晋升。')
    append('FAILED_HYPOTHESES.md','## Phase2冻结失败\n\nF-NIGHT-001：固定63/252组合及40/50/60先验未稳定增加主12m信息；八批均差于常数60%对照。F-NIGHT-002：weeklySPY/BIL未证明优于固定50/50及60/40/70/30；不能靠改费用/窗口/年份救活。仅记录NO EVIDENCE OF GENERIC TIMING EDGE，不证明所有趋势无效。\n\nF-P2-C1：高通胀+年度加息久期组合FRAGILE，2023方向反例、2021大亏未触发；日期/阈值变动翻号并含发布时间边界。是否局部有效待新的独立数据，不调整旧门槛。Q-P2-C2 N1是证据不足、不是已证伪。随机日期placebo N0是数据不足、不是规则通过或失败。')
    append('OPEN_QUESTIONS.md','## Phase2最终优先级\n\n1. 在固定下跌起点，同T信用/再融资和盈利/现金流，能否区分暂时冲击与结构恶化？最小连续历史信用vintage与两行业原财务，不按赢家抽样。\n2. 基本面改善相对当时预期/逆向估值是否仍有增量？两份MSFT原档只能作工程种子，不足检测上修/CapEx机制。\n3. 基础配置之外，是否有与风险预算匹配的局部保护？冻结失败规则，未来独立检验，不在旧样本寻找最优窗口。\n\n有效随机日期检验需补所选日期之前的连续原宏观release；不能重抽直到条件可用。完整PIT报价vintage与历史行业成分依然缺。')
    append('PREDICTION_LEDGER.md','\n## Phase2补记\n\n没有新增锁定概率预测或重复旧回放。条件表48期限行、102固定配置记录、601placebo运行条目都是探索性分析，不加入377预测分母；概率校准仍来自原锁定40/50/60%先验。详见ERROR_TAXONOMY与CONDITIONAL_EDGE_REPORT。')
    append('CHANGELOG.md',f'## PHASE2_FINAL — {now}\n\n冻结失败通用规则；追加8条件问题+2有限宏观检验、残差基准、placebo/扰动与SEC原档QA。完成9份主报告，原30CP/EXP与操作性框架不变，原则晋升0。待导出ZIP按独立manifest核验。')
    append('DATA_INVENTORY.md','## SEC pilot最终准入\n\n两份MSFT2016/2023原10-K共8原事实核验完成，accepted时刻+次日本地00:00保守可用性，非earliest earnings release。原namespace/context/USD/scale/来源SHA可追溯；不是8个投资样本。companyfacts后续accession数值继续隔离，未核2018原文/原因。最小字段清单不是已验证JSON Schema，入engine还需要单独adapter。')
    append('DATA_SOURCE_CATALOG.md','## Phase2新增来源实测\n\nSEC companyfacts/submissions MSFT均HTTP200；两2016/2023原filing package的8source字节与8facts通过离线独立核验。原SEC可以提供filing accepted时间，保守次日可用；今日companyfacts仅locator，按财期取最新值不准入。原始filing单位/报表范围/上下文与revision另核，不能将2份文件当盈利预期样本。19个市场source中CSI300/CHINEXT仅当前1行（HTTP200但无历史），SSE历史可用；XLF隔离、BIL含真实普通reverse split。ALFRED一个vintage请求503，Treasury一个URL404，未将其写成来源整体不可用。所有数据免费公开取得，本轮没有新增海量数据。')
    (ROOT/'research/status/LATEST.md').write_text(f'# 最新状态\n\nPHASE2_COMPLETE_NO_ESTABLISHED_EDGE — {now}\n\n430选择记录 / 377有效锁定预测 / 374成熟12m / 53不足历史 / 3待成熟12m；43日期、23年份，独立N未知。Phase2新增Replay=0，新增概率预测=0。NO EVIDENCE OF GENERIC TIMING EDGE；C1 FRAGILE；C2 N1；random-date PLACEBO_NOT_EVALUABLE。\n\n8份Phase2报告与NIGHT_RESEARCH_REPORT完成，所有旧预测和原15CP/15EXP不变；操作性框架无改动，live=false、validated=[]。研究资料与状态JSON已更新。\n\n先读[报告](../../CONDITIONAL_EDGE_REPORT.md)、[最终checkpoint](../checkpoints/PHASE2_FINAL.v001.json)、[独立QC](../audit/PHASE2_QUALITY_SCIENTIFIC_REVIEW.v001.md)。导出目录/workspace/outputs/investment_research_phase2，ZIP为/workspace/outputs/Investment_Research_Lab_Phase2.zip。\n\n下一步是小连续原始信用/财务/预期数据和独立新样本。当前是完成本阶段与科学边界checkpoint，不是宣称全球数据耗尽。\n')
    print(json.dumps({'status':snapshot['status'],'counts':counts,'operational_keys_unchanged':protected,'checkpoint':str(out)}))

if __name__=='__main__':main()
