#!/usr/bin/env python3
"""Presentation-only expansion of locked Phase 3 statistics; no new tests."""
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/phase3/analysis'
DOCS = ['EXPANDED_PANEL_REPORT.md', 'EFFECTIVE_SAMPLE_REPORT.md',
        'CROSS_TIME_VALIDATION.md', 'MULTIPLE_TESTING_LEDGER.md']
MARKER = '## 人工统计核验与完整分布（presentation v002）'
VARIABLES = ['H-P3-TREND', 'H-P3-DRAWDOWN', 'H-P3-VOL', 'H-P3-CREDIT']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def pct(value):
    return 'UNKNOWN' if value is None else f'{value*100:.2f}%'


def pp(value):
    return 'UNKNOWN' if value is None else f'{value*100:+.2f}pp'


def row(items):
    return '|' + '|'.join(map(str, items)) + '|'


def append(name, lines):
    path = ROOT / name
    old = path.read_text()
    if MARKER in old:
        raise RuntimeError('Presentation already added; do not duplicate: ' + name)
    # A one-block bootstrap degenerates. Do not print its repeated point as a
    # supported confidence interval in the prominent automatic summary table.
    if name == 'EXPANDED_PANEL_REPORT.md':
        improved = []
        for line in old.splitlines():
            if line.startswith('|') and 'UNRELIABLE_FEWER_THAN_4_BLOCKS' in line:
                pieces = line.split('|')
                pieces[7] = '不可推断（不足4块）'
                line = '|'.join(pieces)
            improved.append(line)
        old = '\n'.join(improved) + '\n'
    if name == 'CROSS_TIME_VALIDATION.md':
        improved = []
        for line in old.splitlines():
            if line.startswith('|') and ('|2020-2025|' in line or '|holdout|' in line):
                pieces = line.split('|')
                pieces[7] = '不可推断（不足4块）'
                line = '|'.join(pieces)
            improved.append(line)
        old = '\n'.join(improved) + '\n'
    path.write_text(old.rstrip() + '\n\n' + '\n'.join(lines) + '\n')


def main():
    prior = {name: sha(ROOT / name) for name in DOCS}
    dev = load(OUT / 'development.results.v001.json')
    later = load(OUT / 'holdout.results.v001.json')
    partitions = [dev, later]
    lock = load(OUT / 'development.lock.v001.json')
    for name, expected in lock['files'].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError('Frozen development changed.')
    laterlock = load(OUT / 'holdout.lock.v001.json')
    for name, expected in laterlock['files'].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError('Frozen holdout changed.')
    expanded = [MARKER, '',
        '**RAW OBSERVATIONS：2704固定选择格；2113合格价格feature；成熟且合格12m=2087、24m=1995。** 原始六期限行16224，不是16224个独立决策。≤2023有2021可计算价格label起点，但其中92历史feature不足，变量比较只纳入1929。', '',
        '**EFFECTIVE SAMPLE ASSESSMENT：N_effective=null。** 开发93季度簇/24年份/12个两年块；后期7季度簇/2年份/1块。全池USA工具多、较早年代工具少，日期等权仍不能消除存续工具、类别构成、不同日期组与共同全球regime偏差。', '',
        '后期只有一个两年块，机器bootstrap区间会退化为同一个点；这只是流程输出，不能解释为精确95%置信区间。2020–23开发年代只有两个块也不可推断。所有原数值保留在JSON，突出表格显示不可推断。', '',
        '### 主12m与次24m组内分布', '',
        '所有数值为未来同资产收益分布；P10/P90是分位点，不是尾部十分之一均值。正收益比例不是策略准确率。']
    for p in partitions:
        expanded += ['', f"#### {p['partition']}", '',
            '|期限|变量|组|N raw|均值|中位数|正收益比例|P25|P75|P10|P90|',
            '|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for z in p['all_results']:
            if z['cohort_type'] != 'ALL' or z['horizon'] not in ['12m', '24m']:
                continue
            for g in ['group1', 'group0']:
                s = z[g]
                expanded.append(row([z['horizon'], z['variable'], z[g+'_label'], s['n_raw']]
                    + [pct(s[k]) for k in ['mean', 'median', 'win_rate', 'p25', 'p75',
                                           'worst_decile_p10', 'best_decile_p90']]))
        expanded += ['', '|期限|变量|组|平均gross-MDD|最差gross-MDD|SPY/BIL配对N|平均配对差|',
                     '|---|---|---|---:|---:|---:|---:|']
        for z in p['all_results']:
            if z['cohort_type'] != 'ALL' or z['horizon'] not in ['12m', '24m']:
                continue
            for g in ['group1', 'group0']:
                s, b = z[g], z['benchmarks']['PAIRED_ASSET_BENCHMARK'][g]
                expanded.append(row([z['horizon'], z['variable'], z[g+'_label'],
                    pct(s['mean_max_drawdown']), pct(s['worst_max_drawdown']),
                    b['n_raw'], pp(b['mean'])]))
        expanded += ['', '|期限|变量|组|50/50 SPY/BIL配对N/平均差|60/40 SPY/IEF配对N/平均差|70/30 SPY/IEF配对N/平均差|',
                     '|---|---|---|---|---|---|']
        for z in p['all_results']:
            if z['cohort_type'] != 'ALL' or z['horizon'] not in ['12m', '24m']:
                continue
            for g in ['group1', 'group0']:
                cells = []
                for b in ['FIXED_50_50_SPY_BIL', 'FIXED_60_40_SPY_IEF', 'FIXED_70_30_SPY_IEF']:
                    q = z['benchmarks'][b][g]
                    cells.append(f"{q['n_raw']} / {pp(q['mean'])}")
                expanded.append(row([z['horizon'], z['variable'], z[g+'_label']] + cells))
    expanded += ['', '### 口径、机制和可执行性', '',
        '主MDD来自既有lab.evaluate的gross经济财富；固定配置helper使用after-cost净NAV和明确应收股息计价。固定配置残差字段采用同helper资产可比净收益减配置净收益，另保存与主label的delta。不能把gross-MDD与after-cost配置MDD直接相减；配对差也不是alpha。', '',
        '大跌组12m开发raw均值14.47%对6.52%，日期等权差却只有+1.77pp，区间跨0，平均MDD−23.81%对−15.22%。回撤后尾部和样本构成对漂亮平均数很重要。后期大跌只有2条12m和1条24m，不能承担独立确认。', '',
        '相对vol开发24m日期等权+9.00pp、区间[+1.74,+16.94]pp是值得反证的观察；但香港/德国/英国24m方向反例、2000年代12m负方向、较高平均MDD与跨行业差异均保留。后期正差仍只有一个全球时间块，不能升级。', '',
        '信用净收紧水平的主12m年代差从−8.50pp变为+1.37pp，二元门槛失败；不运行被拒绝交互，也不把信用水平改成变化率救结论。估值、盈利修正与信用利差、借款人现金流仍缺连续原时点数据，因此不能将价格反弹归因为错杀或Underreaction。', '',
        '没有重跑旧63/252策略、旧概率预测或切换配置。本面板未推翻Phase2“尚未建立edge”的证据边界，但不能冒称重新验证了旧规则全部性能。趋势可见状态的关联存在，独立预测作用与确认工具的增量价值均未建立。']
    append('EXPANDED_PANEL_REPORT.md', expanded)
    eff = [MARKER, '', '### RAW OBSERVATIONS', '',
        '2704选择格、2113合格价格feature、2087成熟12m。430格曾在旧asset/calendar-quarter抽样框出现（包含旧不足与待成熟格），其余2274格未在该旧框出现；这不是未见价格路径证明。', '',
        '### EFFECTIVE SAMPLE ASSESSMENT', '',
        '开发与后期的greedy无重叠清单各自在partition内计算：12m448与46，24m237与23。这些数字不能相加称全时期无重叠，因开发12/24m持仓区间会跨入后期；每资产合并的实际重叠由独立QA附录记录。即使合并剔除重叠，跨资产同一全球冲击仍存在。', '',
        '固定两年块也不能保证24m标签跨块的依赖完全消失。500重抽样不是500个新增经济周期，单块后期的500重复只是同样数据，退化区间不能支持准确估计。', '',
        '按最早entry贪心取样不看收益，已有变量分布全保存。开发大跌12m无重叠对照在SPY/QQQ/XLK/日本/黄金出现负差；部分行业/市场为正。控制重叠并未把所有资产变成同向，不能只看有利子样本。', '',
        '审阅：`research/phase3/analysis/STATISTICAL_METHOD_NOTES.v001.md`、各分区actual_nonoverlap和后续独立QA附录。']
    append('EFFECTIVE_SAMPLE_REPORT.md', eff)
    cross = [MARKER, '', '### RAW OBSERVATIONS', '',
        '开发变量比较1929主12m/1929次24m；后期158主12m/66次24m。后期大跌组主12m只有2、次24m只有1，信用24m无不收紧组。', '',
        '### EFFECTIVE SAMPLE ASSESSMENT', '',
        '开发结果及本文开发解释先封存；随后一次正式揭晓2024/25。后期只有1两年块，开发前瞻收益已跨到2024/25，旧研究也已接触路径，因此后期只能称计算隔离，不能称真正未来OOS或全新全球regime。', '',
        '### 主12m市场反例：日期等权组间差', '',
        '|分区|变量|CN|DE|EU|HK|JP|UK|US|', '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for p in partitions:
        for variable in VARIABLES:
            vals = {z['cohort']: z['group_difference']['difference_date_equal'] for z in p['all_results']
                    if z['cohort_type'] == 'market' and z['horizon'] == '12m' and z['variable'] == variable}
            cross.append(row([p['partition'], variable] + [pp(vals.get(m)) for m in ['CN','DE','EU','HK','JP','UK','US']]))
    cross += ['', '美国信用只进入US字段，其他市场UNKNOWN；US包含股票、国债、资源和现金混合工具，不等于股票单独效应。EU指STOXX50E，2008Q2之后feature才合格；DE为DAX performance指数，不能按普通price-only统一归因。', '',
        '12m开发趋势差在US约+0.10pp，其余市场负；24m七市场均负。该描述不证明反向策略可执行，也不代表趋势从不含信息。', '',
        '大跌12m开发年代方向+1.45/−7.11/+14.67pp，后期+32.03pp只是2条；24m开发年代+36.99/−11.34/+27.78pp，后期+21.40pp只是1条。信用12m年代−8.50/+1.37/+12.43pp，后期−0.94pp。跨年代方向边界阻止通用原则成立。', '',
        '高vol24m开发总池正差，但HK/DE/UK为负；后期总池正差只有1块、11条高组，对连续独立未来周期无确认能力。根协议门槛与旧JSON没有修改。', '',
        '真正未来检验需每月捕获当时源快照；首月末2026-10-30仍PENDING_DECISION，不能补造未发生的预测。']
    append('CROSS_TIME_VALIDATION.md', cross)
    testing = [MARKER, '', '### RAW OBSERVATIONS / EFFECTIVE SAMPLE ASSESSMENT', '',
        '固定2704格、2113有效feature、2087主12m；N_effective=null。四个变量各在开发与较晚分区报告，不是八个独立假说。', '',
        '两分区共10272单变量比较槽位，其中5273两组可比；51360基准槽位，包括恒零自身被动、缺失和重复分组；416个分区内实际无重叠变量槽位。214cohort规格由预先固定市场/行业/资产/年代及交叉构成，全部保留。', '',
        '经济二元假说登记1，gate共享开发数据，因年代方向反转运行格0；参数搜索0；新投资原则0。H-P3-VOL-ENDPOINT-v001是标签前的数学端点澄清，没有阈值搜索。', '',
        '单个高vol24m正区间或欧洲大跌正区间可能受多重比较影响，不能从几千相关槽位只挑有利数值。区间没有被宣传为multiple-testing-adjusted。', '',
        '后续H-P3-MATCHED-CONTROLS-v001是已看主结果后另行预登记的反证研究，须另计探索性study及全部组/期限/缺失；不得覆盖上述试验或复活失败交互。结果由该独立study文件追加。']
    append('MULTIPLE_TESTING_LEDGER.md', testing)
    metadata = {'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'mode': 'PRESENTATION_ONLY_NO_NEW_STATISTICAL_TESTS',
        'old_report_sha256': prior, 'new_report_sha256': {n: sha(ROOT / n) for n in DOCS},
        'analysis_inputs_sha256': {p: sha(OUT / p) for p in ['development.results.v001.json', 'holdout.results.v001.json']},
        'code_sha256': sha(Path(__file__)),
        'reason': 'Full distribution tables, hypothesis scope, methods compatibility and honest degenerate bootstrap display; raw results and locked statistical code unchanged.',
        'raw_observations': 2704, 'n_effective': None, 'new_experiments': 0}
    target = OUT / 'reports.presentation.v002.json'
    if target.exists():
        raise RuntimeError('Presentation manifest already exists.')
    target.write_text(json.dumps(metadata, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
    print(json.dumps({'presentation_reports': 4, 'new_experiments': 0, 'raw_results_changed': False}))


if __name__ == '__main__':
    main()
