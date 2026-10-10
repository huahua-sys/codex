#!/usr/bin/env python3
"""Append source-date correction and two exact implementation documents, preserving v001."""
import importlib.util,json,pathlib,urllib.parse,hashlib
D=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fixedfetch',D/'fetch_framework_sources.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=D/'FRAMEWORK_SOURCE_LEDGER.v002.json'
if p.exists(): raise SystemExit('Refusing overwrite')
previous=D/'FRAMEWORK_SOURCE_LEDGER.v001.json'
a=json.loads(previous.read_text())
a['version']='v002';a['previous_ledger_sha256']=hashlib.sha256(previous.read_bytes()).hexdigest()
a['corrections']=[{'source_id':'FW21','v001_document_date_hint':'2024-07-26','corrected_document_date':'2024-04-12','basis':'Fetched PDF itself says Date:12/04/2024. This is initial announcement, not July implementation circular. v001 never admitted it as event.'}]
for x in a['sources']:
 if x['source_id']=='FW21': x['document_date_hint']='2024-04-12'
new=[('FW26','HKEX July remaining disclosure implementation','2024-07-26',urllib.parse.quote('https://www.hkex.com.hk/eng/prod/dataprod/Documents/24-07-26 Arrangement of OMD-C and MMDH for the Adjustment to Market Data Dissemination in Relation To Northbound Trading under Stock Connect - The Remaining Items.pdf',safe=':/'),['19 August 2024','26 July 2024']),('FW27','BOJ ETF lending zero and rule abolition','2026-01-16','https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2026/mpr260116b.pdf',['January 16, 2026','outstanding balance','zero','resume'])]
a['sources'].extend(m.fetch(x) for x in new)
p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
print([(x['source_id'],x['status'],x.get('matched_terms')) for x in a['sources'][-2:]])
