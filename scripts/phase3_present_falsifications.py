#!/usr/bin/env python3
"""Append locked counterexample studies to Phase 3 reports, without new tests."""
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/phase3'
DOCS = ['EXPANDED_PANEL_REPORT.md', 'EFFECTIVE_SAMPLE_REPORT.md',
        'CROSS_TIME_VALIDATION.md', 'MULTIPLE_TESTING_LEDGER.md']
MARKER = '## 后续两轮反证checkpoint（presentation v004）'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def pp(value):
    return 'UNKNOWN' if value is None else f'{value*100:+.2f}pp'


def interval(value):
    return 'UNKNOWN' if value is None else f'[{value[0]*100:.2f}, {value[1]*100:.2f}]pp'


def append(name, lines):
    p = ROOT / name
    text = p.read_text()
    if MARKER in text:
        raise RuntimeError('Checkpoint already presented: ' + name)
    if name == 'EXPANDED_PANEL_REPORT.md':
        text = text.replace('状态：LEVEL 1 — DESCRIPTIVE；没有运行或调参旧择时规则，没有新增投资原则。',
            '状态：主面板LEVEL 1 — DESCRIPTIVE；后续反证形成PAC-P3-001（C级、LEVEL 2限定关联候选），零LEVEL 3投资原则。没有运行或调参旧择时规则。')
    p.write_text(text.rstrip() + '\n\n' + '\n'.join(lines) + '\n')


def main():
    old = {n: digest(ROOT / n) for n in DOCS}
    matched_path = BASE / 'matched/RESULTS.v001.json'
    vol_path = BASE / 'vol_falsification/RESULTS.v001.json'
    qa_path = BASE / 'audit/OUTCOME_PATH_INTEGRITY_QA.v005.json'
    matched, vol, qa = read(matched_path), read(vol_path), read(qa_path)
    if matched['comparison_slots'] != 104 or matched['identified_comparisons'] != 12 or len(vol['comparisons']) != 88:
        raise RuntimeError('Unexpected locked counterexample contract.')
    totals = {h: sum(x['merged_greedy_nonoverlap'] for x in qa['merged_nonoverlap_appendix']
                     if x['horizon'] == h) for h in ['12m', '24m']}
    sums = {h: sum(x['partition_internal_sum'] for x in qa['merged_nonoverlap_appendix']
                   if x['horizon'] == h) for h in ['12m', '24m']}
    if totals != {'12m': 480, '24m': 245} or sums != {'12m': 494, '24m': 260}:
        raise RuntimeError('Unexpected global nonoverlap audit counts.')
    scope = [MARKER, '',
        '**RAW OBSERVATIONS：复用2704固定格、2087成熟12m/1995成熟24m；两轮新增决策点/预测=0。**', '',
        '**EFFECTIVE SAMPLE ASSESSMENT：N_effective=null。** 同季度同币种同类对照去除了部分共同日期影响，但行业beta、风险溢价、资本周期、估值、金融基本面和全球环境尚未匹配。所有后续研究是看过主结果之后另预登记的探索性反证，不是独立未来OOS。', '',
        '### 同季度同类对照：104槽位只有12可识别', '',
        '|市场/类层|变量|期限|双方季度|净收益差|两年块区间|gross-MDD差|',
        '|---|---|---|---:|---:|---|---:|']
    for x in matched['results']:
        if x['both_group_quarters']:
            scope.append('|'+ '|'.join(map(str, [x['stratum'][0]+'/'+x['stratum'][2], x['variable'],
                x['horizon'], x['both_group_quarters'], pp(x['return_contrast']['mean']),
                interval(x['return_contrast']['ci95']), pp(x['gross_MDD_contrast']['mean'])])) +'|')
    scope += ['', '其余92槽位是无对组、singleton或不可识别，全部保存而不删除。美国SLOOS信用状态同一个美国季度复用于各工具，无法在同date横截面匹配收紧与不收紧；原H-P3-DD-CREDIT门槛仍失败，不另跑交互救结论。', '',
        '美国股票的大跌对照12/24m差+3.66/+6.09pp，区间均跨0，gross-MDD更差约7.88/9.87pp。此前漂亮的大跌平均数没有变成同日期稳定优势。', '',
        '美国股票相对vol的12/24m对照差+7.66/+14.24pp，当前描述区间暂未跨0；美国国债久期类的对应点差−2.41/−2.59pp且区间跨0。它不是跨资产通用信号，也不证明风险匹配后的alpha。', '',
        '### 全部遗漏与实际无重叠反证', '',
        'H-P3-VOL-FALSIFICATION-v001预先登记11个版本（ALL及逐个删去10个US股票ETF）×4年代×2期限=88槽位，全部结果保留，不按最好的删减选证券。全时期所有遗漏对照点差仍正；早期2000–09区间跨0，年代和行业边界没有消失。', '',
        '|严格跨分区无重叠|双方季度|净差|描述块区间|gross-MDD差|',
        '|---|---:|---:|---|---:|']
    for x in vol['nonoverlap']:
        # Fields are explicit in the preregistered result; use exact frozen
        # summaries rather than recomputing future-return contrasts here.
        scope.append('|'+ '|'.join(map(str, [x['horizon'], x['both_group_quarters'],
            pp(x['return_contrast']['mean']), interval(x['return_contrast']['ci95']),
            pp(x['gross_MDD_contrast']['mean'])])) +'|')
    scope += ['', '14/10双方季度是按实际entry/exit严格贪心、共同限制全部US股票的日历起点；不是14/10个独立经济世界。部分年份没有可对照组、实际持有期仍可能同一全球regime，500bootstrap不会增加真实周期。', '',
        '这两轮存活的有限观察登记为PAC-P3-001，最高C级、LEVEL2、PREDICTIVE_ASSOCIATION_ONLY，限定US股票相对自身过去vol状态与12/24m相对收益。没有识别causal mechanism或risk-matched alpha，没有买入/仓位/择时规则，也没有新LEVEL3投资原则。', '',
        '最重要的未解决反证：更早年代区间跨0；非US市场/国债方向不一致；beta、行业风险和存续ETF池未匹配；共同路径已被看过；大量相关切片可能给出偶然正区间。下一步优先建立独立未来记录和风险/盈利/预期数据，不调阈值。', '',
        '来源：`research/phase3/matched/PREREGISTRATION.v001.json`、`RESULTS.v001.json`、`REPORT.v001.md`及`research/phase3/vol_falsification/`同名三文件，原主统计JSON和旧282/374结果保持冻结。']
    append('EXPANDED_PANEL_REPORT.md', scope)
    effective = [MARKER, '', '**RAW OBSERVATIONS：仍为2704选择格；新增决策点/概率预测0。**', '',
        '**EFFECTIVE SAMPLE ASSESSMENT：N_effective=null。**', '',
        '|主期限|分区内计数之和（不能称全球无重叠）|QA合并两分区后每资产greedy合计|分区和高估|',
        '|---|---:|---:|---:|',
        '|12m|494|480|14|', '|24m|260|245|15|', '',
        '独立QA：`research/phase3/audit/OUTCOME_PATH_INTEGRITY_QA.v005.json`。480/245仍是各资产无重叠记录之和，资产间相关和全球环境未消失，不能当独立N。此前partition各自448+46、237+23仅保留为内部算法输出。', '',
        '另一套US相对vol反证按共同实际持有区间严格挑双方季度，12m14、24m10；它与上述per-asset 480/245是不同粒度，不能混用。固定最早起点算法没有看收益挑样本，完整point IDs已在锁结果保存。', '',
        '同季度对照104槽位仅12可识别；美国信用同quarter没有横截面两组，海外单资产同类也大多无对组。matched不可识别是数据结构限制，不能假装已经完成跨五国同风险机制验证。', '',
        '新增88遗漏/年代槽+2严格无重叠槽共90，是复用相同数据的相关敏感度，不是90次独立世界测试。样本扩展提高了研究覆盖，不自动提高证据等级。']
    append('EFFECTIVE_SAMPLE_REPORT.md', effective)
    cross = [MARKER, '', 'RAW OBSERVATIONS：主panel仍2704；两个后续study新增决策点和预测为0。', '',
        'EFFECTIVE SAMPLE ASSESSMENT：同一开发/后来价格路径多次被复用，独立N未识别；后续探索研究登记晚于主结果，不允许称新的OOS。', '',
        '|US股票相对vol同季度对照|2000–09|2010–19|2020–25|',
        '|---|---|---|---|']
    for h in ['12m', '24m']:
        cells = []
        for e in ['2000-2009', '2010-2019', '2020-2025']:
            x = next(v for v in vol['comparisons'] if v['horizon'] == h and v['variant'] == 'ALL' and v['era'] == e)
            cells.append(f"{pp(x['return_contrast']['mean'])}; {interval(x['return_contrast']['ci95'])}; Q={x['both_group_quarters']}")
        cross.append('|'+ '|'.join([h]+cells)+'|')
    cross += ['', '早期点差正但区间跨0；2020以后只有少量双方quarter/时间块，不能根据窄bootstrap区间推断跨危机稳定。遗漏对照全时期正值不能替代独立非US风险匹配或未来验证。', '',
        '国债久期类的相对vol12/24m点差负，说明产业/资产现金流与久期结构须分别建机制。US股票关联暂存PAC-P3-001（C，限定LEVEL2），不是通用规律；原操作性框架、旧预测和信用拒绝门槛不改。']
    append('CROSS_TIME_VALIDATION.md', cross)
    ledger = [MARKER, '', 'RAW OBSERVATIONS：仍2704固定格，复用2087成熟12m/1995成熟24m；新增起点/预测0。EFFECTIVE SAMPLE ASSESSMENT：N_effective=null。', '',
        '|新增study|预定描述槽位|可识别/具体约束|登记时已经看过的结果|',
        '|---|---:|---|---|',
        '|H-P3-MATCHED-CONTROLS-v001|104|只有12有双方同季度同类组；其余92保存不可识别|全部主面板development+later|',
        '|H-P3-VOL-FALSIFICATION-v001：ALL+全部10遗漏×4年代×2期限|88|全部遗漏结果保留，不挑最佳；共享同一资产/年份/标签|全部主面板+matched|',
        '|同假说严格跨分区无重叠：两个期限|2|14/10双方季度，不是独立世界N|同上|', '',
        '额外对照194槽，连同主变量报告10272槽共10466描述比较槽；另有主报告51360基准槽和416分区内无重叠变量槽。不同报告/子样本大量重复同数据，不应将这些整数称独立实验数或multiplicity校正后的p值。', '',
        '本阶段登记4单变量，信用×回撤1个提案因gate失败不运行，另两探索性反证study。阈值/市场/原日期/期限/费用未改；参数优化0；新决策点/预测0；LEVEL3新原则0。PAC-P3-001是限US股票C级关联候选，升级未来需独立验证。', '',
        '历史筛选也必须保留：旧8batch复用同一冻结规则；前阶段记录4study families；C1/C2共601placebo运行项（非601独立投资样本）和9预定扰动。原15候选/15设计未完成对应机制检验，不算15成功或失败实证。历史所有posthoc描述对照无法统一去重，`OLD_CUMULATIVE_COMPARISON_COUNT_UNKNOWN`，因此新观察不能当研究者零筛选历史的confirmatory发现。', '',
        '正区间未做multiple-testing校正，没有保护理论。所有失败、缺组、相反市场/资产类、遗漏和早年代结果保留，最高存活评价C/LEVEL2，仍可能来自beta、风险溢价、存续偏差与共同regime。']
    append('MULTIPLE_TESTING_LEDGER.md', ledger)
    metadata = {'written_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'mode': 'PRESENTATION_OF_ALREADY_LOCKED_COUNTEREXAMPLES_NO_NEW_TESTS',
        'old_report_sha256': old, 'new_report_sha256': {n: digest(ROOT / n) for n in DOCS},
        'sources_sha256': {str(p.relative_to(ROOT)): digest(p) for p in [matched_path, vol_path, qa_path]},
        'new_decisions': 0, 'new_forecasts': 0, 'new_investment_principles': 0,
        'raw_observations': 2704, 'n_effective': None,
        'recorded_followup_comparison_slots': 194,
        'operative_framework_changed': False}
    out = BASE / 'analysis/reports.falsification_presentation.v004.json'
    if out.exists():
        raise RuntimeError('Manifest already written.')
    out.write_text(json.dumps(metadata, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
    print(json.dumps({'reports_updated': 4, 'followup_slots_recorded': 194, 'new_tests_by_presentation': 0}))


if __name__ == '__main__':
    main()
