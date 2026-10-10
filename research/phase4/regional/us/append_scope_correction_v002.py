#!/usr/bin/env python3
"""Append-only QA correction; original event bytes/lock remain preserved."""
import json
from datetime import datetime,timezone
from acquire_us_sources import ROOT,OUT,savej,digest

old=OUT/'events.json';lock=json.loads((OUT/'events.lock.v001.json').read_text())
assert digest(old.read_bytes())==lock['sha256']
rows=json.loads(old.read_text());changes=[]
for e in rows:
    if e['family']!='corporate_capital_allocation':continue
    before=e['observed_action']
    e['observed_action']='披露此前季度的common-stock-repurchase现金支出，非当日新回购指令；现金流行不识别公开市场执行量。'
    if e['published_date'].startswith('2009'):
        e['observed_action']+='2009原文另明确该季度无常规股份回购；2200万美元是现金流行金额，其交易类别未识别。'
        e['flow_size']['basis']+='; NOT_CONFIRMED_OPEN_MARKET_BUYING; 2009 source separately states no quarterly regular share repurchases'
        e['unknown_at_t'].append('2009现金流2200万美元与原文零常规回购的交易类别/税扣桥接，未独立识别')
    changes.append({'event_id':e['event_id'],'field':'observed_action','old':before,'new':e['observed_action']})
target=OUT/'events.v002.json';assert not target.exists()
savej(target,rows)
savej(OUT/'events.lock.v002.json',{'file':str(target.relative_to(ROOT)),'sha256':digest(target.read_bytes()),'locked_at':datetime.now(timezone.utc).isoformat(),'previous_sha256':lock['sha256'],'previous_file':str(old.relative_to(ROOT)),'change_reason':'Independent QA found cross-year 2009 explanatory sentence repeated in every corporate event, potentially confusing event-specific evidence. Narrowed the sentence to its original 2009 source only, explicitly distinguished cash-row from open-market buying. No selected event, dates, numerical amount or outcomes changed.','changes':changes,'price_outcome_accessed_before_lock':False})
print({'append_only_version':'v002','events':len(rows),'corporate_scope_corrections':len(changes),'old_sha_unchanged':digest(old.read_bytes())==lock['sha256']})
