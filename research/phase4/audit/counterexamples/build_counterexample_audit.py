#!/usr/bin/env python3
"""Create source-backed audit cards. No prices, labels, or old results are read or changed."""
from pathlib import Path
import datetime, hashlib, json, re

ROOT = Path(__file__).resolve().parents[4]
AUDIT = ROOT / 'research/phase4/audit/counterexamples'
SOURCES = ROOT / 'sources/counterexamples'

def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

source_rows = []
for manifest in ['source_fetch_manifest.v001.json', 'china_sources.v001.json']:
    source_rows += json.loads((AUDIT / manifest).read_text())
source_rows.append(json.loads((AUDIT / 'gpif_source.v001.json').read_text()))
source_rows.append(json.loads((AUDIT / 'iea_landing_source.v001.json').read_text()))
source_rows += json.loads((AUDIT / 'jpx_cross_agent_sources.v001.json').read_text())

by_id = {}
for row in source_rows:
    key = row.get('id', row.get('source_id'))
    if key == 'jp_event_source_025':
        key = 'JPX_2017_01_30_BUYBACK'
    elif key == 'jp_event_source_031':
        key = 'JPX_2023_07_03_BUYBACK'
    row = dict(row, audit_source_id=key)
    if row.get('path'):
        p = ROOT / row['path']
        assert p.exists()
        assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256']
        row['signal_use_permitted'] = False
        row['use'] = 'RETROSPECTIVE_SOURCE_AUDIT_ONLY'
    by_id[key] = row

dates = {
 'FCIC_2011_FINANCIAL_CRISIS': ('2011-01; corrected printing includes errata as of 2011-02-25', 'EXACT_PUBLICATION_OF_THIS_CORRECTED_VERSION_UNCERTAIN'),
 'FSB_2020_11_17_HOLISTIC_REVIEW': ('2020-11-17', 'DATED_ORIGINAL_PDF; NO_PRE_CRISIS_AVAILABILITY'),
 'FED_2020_06_25_BANK_DISTRIBUTIONS': ('2020-06-25', 'OFFICIAL_RELEASE_DATE; EXACT_TIME_NOT_USED'),
 'FED_2020_03_23_LIQUIDITY': ('2020-03-23', 'OFFICIAL_RELEASE_DATE; FUTURE_PURCHASE_LANGUAGE_NOT_ACTUAL_FLOW'),
 'BOJ_2024_03_19_END_ETF_PURCHASES': ('2024-03-19', 'DATED_OFFICIAL_POLICY_PDF; PURCHASE_CESSATION_NOT_SALE'),
 'GPIF_2014_10_31_POLICY_MIX': ('effective 2014-10-31; document publication timestamp unconfirmed', 'POINT_IN_TIME_UNCERTAIN_FOR_PUBLICATION'),
 'SEC_2022_12_14_INSIDER_PLANS': ('2022-12-14', 'DATED_RULE_ADOPTION_RELEASE; EFFECTIVE_DATE_SEPARATE'),
 'FED_2020_11_09_STABILITY': ('2020-11 on PDF; filename 20201109 not sufficient alone', 'DATE_NOT_ADMITTED_AS_SIGNAL'),
 'BERKSHIRE_2008_SHAREHOLDER_LETTER': ('letter signed 2009-02-27; publication timestamp unconfirmed', 'KNOWN_ONLY_AFTER_2008; SIGNATURE_NOT_RELEASE_TIMESTAMP'),
 'GE_2017_ANNUAL_REPORT': ('2017 fiscal year; embedded Form 10-K signed 2018-02-23', 'POINT_IN_TIME_UNCERTAIN_FOR_THIS_REPORT_RELEASE'),
 'IEA_2022_PV_SUPPLY_CHAINS': ('landing page states report published 2022-07-07T03:00:00Z', 'CURRENT_HTML_NOT_ARCHIVED_2022_CONTENT_VERSION'),
 'IEA_2022_REPORT_LANDING': ('2022-07-07T03:00:00Z in current official publication metadata', 'PUBLISHER_DATE_ASSERTION_DOES_NOT_PROVE_ORIGINAL_CONTENT_VERSION'),
 'SSE_2015_11_13_MARGIN_CHANGE': ('announced 2015-11-13; effective 2015-11-23', 'DATED_OFFICIAL_RELEASE; GRANDFATHERED_OLD_CONTRACTS'),
 'CSRC_2023_08_27_MARGIN_CHANGE': ('announced 2023-08-27; effective after close 2023-09-08', 'DATED_OFFICIAL_RELEASE; PERMISSION_NOT_FLOW'),
 'CSRC_2024_02_05_MARGIN_LIQUIDATION': ('2024-02-05', 'DATED_OFFICIAL_Q_AND_A; JANUARY_AGGREGATE_KNOWN_ONLY_AFTER_JANUARY'),
 'JPX_2017_01_30_BUYBACK': ('2017-01-30', 'DATED_ORIGINAL_CORPORATE_PDF; EXECUTION_DISCLOSED_WITH_LAG'),
 'JPX_2023_07_03_BUYBACK': ('2023-07-03', 'DATED_ORIGINAL_CORPORATE_PDF; JUNE_EXECUTION_DISCLOSED_AFTER_JUNE'),
}
for key,row in by_id.items():
    row['publication_date_evidence'],row['point_in_time_quality'] = dates[key]

quotes = {
 'Q-FCIC-01': ('FCIC_2011_FINANCIAL_CRISIS', 'This printing includes all corrections contained in the errata sheet issued by the Commission as found on the FCIC website as of February 25, 2011.'),
 'Q-FCIC-02': ('FCIC_2011_FINANCIAL_CRISIS', 'We conclude a combination of excessive borrowing, risky investments, and lack of transparency put the financial system on a collision course with crisis.'),
 'Q-FCIC-03': ('FCIC_2011_FINANCIAL_CRISIS', 'When borrowers stopped making mortgage payments, the losses—amplified by derivatives—rushed through the pipeline.'),
 'Q-FSB-01': ('FSB_2020_11_17_HOLISTIC_REVIEW', 'Market dysfunction was exacerbated by the substantial sales of US Treasuries by some leveraged non-bank investors and foreign holders.'),
 'Q-FSB-02': ('FSB_2020_11_17_HOLISTIC_REVIEW', 'The increase in US Treasury price volatility also led to margin calls in spot markets for basis trade investors, some of whom encountered difficulties renewing funding for their trades.'),
 'Q-FSB-03': ('FSB_2020_11_17_HOLISTIC_REVIEW', 'Some investors in open-ended investment funds may have faced incentives to redeem ahead of others.'),
 'Q-FSB-04': ('FSB_2020_11_17_HOLISTIC_REVIEW', 'The policy measures succeeded in alleviating market strains to date, with announcement effects appearing to be particularly important in restoring confidence and shaping the expectations of market participants.'),
 'Q-FSB-05': ('FSB_2020_11_17_HOLISTIC_REVIEW', 'the exceptional measures taken by central banks were not aimed at addressing the underlying vulnerabilities that amplified the stress.'),
 'Q-FED-01': ('FED_2020_06_25_BANK_DISTRIBUTIONS', 'For the third quarter of this year, the Board is requiring large banks to preserve capital by suspending share repurchases, capping dividend payments, and allowing dividends according to a formula based on recent income.'),
 'Q-FED-02': ('FED_2020_03_23_LIQUIDITY', 'Supporting the flow of credit to employers, consumers, and businesses by establishing new programs that, taken together, will provide up to $300 billion in new financing.'),
 'Q-GE-01': ('GE_2017_ANNUAL_REPORT', 'Stock buyback $3.8 billion'),
 'Q-GE-02': ('GE_2017_ANNUAL_REPORT', 'Cut our quarterly dividend from $0.24/share'),
 'Q-GE-03': ('GE_2017_ANNUAL_REPORT', 'to $0.12/share in November, reflecting a reset of'),
 'Q-GE-04': ('GE_2017_ANNUAL_REPORT', 'a payout level that exceeded our free cash flow.'),
 'Q-BRK-01': ('BERKSHIRE_2008_SHAREHOLDER_LETTER', 'I bought a large amount of ConocoPhillips stock when oil and gas prices were near their peak.'),
 'Q-BRK-02': ('BERKSHIRE_2008_SHAREHOLDER_LETTER', 'Even if prices should rise, moreover, the terrible timing of my purchase has cost Berkshire several billion dollars.'),
 'Q-SEC-01': ('SEC_2022_12_14_INSIDER_PLANS', 'the amendments adopt cooling-off periods for persons other than issuers before trading can commence under a Rule 10b5-1 plan.'),
 'Q-SEC-02': ('SEC_2022_12_14_INSIDER_PLANS', 'Insiders that report on Forms 4 or 5 will be required to indicate by checkbox that a reported transaction was intended to satisfy the affirmative defense conditions of Rule 10b5-1(c) and to disclose the date of adoption of the trading plan.'),
 'Q-BOJ-01': ('BOJ_2024_03_19_END_ETF_PURCHASES', 'The Bank will discontinue purchases of exchange-traded funds (ETFs) and Japan real estate investment trusts (J-REITs).'),
 'Q-BOJ-02': ('BOJ_2024_03_19_END_ETF_PURCHASES', 'With the price stability target of 2 percent, it will conduct monetary policy as appropriate'),
 'Q-GPIF-01': ('GPIF_2014_10_31_POLICY_MIX', 'According to the Actuarial Valuation, the reserve asset level is to decrease for 10 years'),
 'Q-GPIF-02': ('GPIF_2014_10_31_POLICY_MIX', 'GPIF adopts tactical asset allocation within permissible ranges of deviation for each asset class'),
 'Q-IEA-01': ('IEA_2022_PV_SUPPLY_CHAINS', 'The net profitability of the solar PV sector for all supply chain segments has been volatile, resulting in several bankruptcies despite policy support.'),
 'Q-SSE-01': ('SSE_2015_11_13_MARGIN_CHANGE', '本次《实施细则》修改实施前尚未了结的融资融券合约及其展期，仍按照修改前的相关规定执行。'),
 'Q-CSRC-01': ('CSRC_2023_08_27_MARGIN_CHANGE', '本次调整同时适用于新开仓合约及存量合约，投资者不必了结存量合约即可适用新的保证金比例。'),
 'Q-CSRC-02': ('CSRC_2024_02_05_MARGIN_LIQUIDATION', '从实际平仓数据看，1月以来全市场累计平仓金额约9亿元，占融资规模的万分之6'),
 'Q-CSRC-03': ('CSRC_2024_02_05_MARGIN_LIQUIDATION', '有些投资者主动卖股票归还融资，会形成融资余额被动下降。'),
 'Q-JPX-01': ('JPX_2017_01_30_BUYBACK', 'Total value of shares acquired JPY 0'),
 'Q-JPX-02': ('JPX_2017_01_30_BUYBACK', 'Total value of shares acquired JPY 3,994,268,900'),
 'Q-JPX-03': ('JPX_2023_07_03_BUYBACK', 'Total value of shares acquired JPY 0'),
 'Q-JPX-04': ('JPX_2023_07_03_BUYBACK', 'Total value of shares acquired JPY 12,620,624,250'),
}
quote_rows=[]
for qid,(sid,quote) in quotes.items():
    row=by_id[sid]
    extract=ROOT / row.get('extract_path', f'research/phase4/audit/counterexamples/{sid}.extracted.txt')
    text=extract.read_text()
    assert norm(quote) in norm(text), f'quote missing: {qid}'
    start_word=norm(quote)[:40]
    lines=text.splitlines()
    candidates=[i+1 for i,line in enumerate(lines) if start_word[:25].lower() in norm(line).lower()]
    quote_rows.append({'quote_id':qid,'source_id':sid,'source_sha256':row['sha256'],'quote':quote,'extract_path':str(extract.relative_to(ROOT)),'candidate_line_starts':candidates[:4],'verification':'NORMALIZED_WHITESPACE_EXACT_SUBSTRING','signal_use_permitted':False})
(AUDIT/'SOURCE_MANIFEST.v001.json').write_text(json.dumps(list(by_id.values()),ensure_ascii=False,indent=2))
(AUDIT/'VERIFIED_EXCERPTS.v001.json').write_text(json.dumps(quote_rows,ensure_ascii=False,indent=2))
print(f'Sources verified: {len(by_id)}; exact quotes verified: {len(quote_rows)}')

