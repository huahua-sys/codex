#!/usr/bin/env python3
"""Original Federal Reserve SLOOS archive acquisition; no market outcomes.

Every invocation registers this exact code hash before downloading anything.
All source bytes are append-only. Numeric extraction is deliberately conservative.
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'research/phase3/data/credit'
UA = 'Mozilla/5.0 (compatible; InvestmentResearchLab historical research)'
BASE = 'https://www.federalreserve.gov'
LANDINGS = [BASE + '/data/sloos.htm', BASE + '/data/sloos/sloos-historical.htm']
YEARS = list(range(2000, 2026))
MONTHS = {x: i + 1 for i, x in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'])}

def sha(x):
    return hashlib.sha256(x).hexdigest()

def write_once(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
    if path.exists():
        if path.read_bytes() != raw:
            raise RuntimeError('Refusing overwrite: ' + str(path))
    else:
        path.write_bytes(raw)

def relative(path):
    return str(path.relative_to(ROOT))

def register(mode):
    code = Path(__file__).read_bytes()
    design = (ROOT/'research/phase3/design.v001.json').read_bytes()
    old = sorted(DEST.glob('code_registration.*.json'))
    path = DEST/f'code_registration.{len(old)+1:03d}.json'
    write_once(path, {'code_sha256':sha(code),'code_path':relative(Path(__file__)),
                     'design_sha256':sha(design),'mode':mode,
                     'registered_at':dt.datetime.now(dt.timezone.utc).isoformat(),
                     'source_scope':'Official SLOOS quarterly releases 2000–2025; maximum 104 release pages; no return data.',
                     'variable':'Domestic banks C&I large/middle-market loan standards net tightening percentage',
                     'numeric_rule':'Exact official net value or exactly derivable from original respondent counts; approximations are UNKNOWN.',
                     'date_rule':'Original release statement only; local next-day midnight when time not proved.'})
    return relative(path)

def get(url, role, parents=None):
    key = sha(url.encode())[:16]
    rawpath = DEST/'raw'/f'{key}.bin'
    metapath = DEST/'raw'/f'{key}.source.json'
    if rawpath.exists() and metapath.exists():
        return rawpath.read_bytes(), json.loads(metapath.read_text())
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    try:
        req = urllib.request.Request(url, headers={'User-Agent':UA})
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
            status = response.status
            final = response.url
            mime = response.headers.get('Content-Type')
        rawpath.parent.mkdir(parents=True, exist_ok=True)
        rawpath.write_bytes(raw)
        meta = {'url':url,'final_url':final,'accessed_at':now,'http_status':status,
                'source_sha256':sha(raw),'source_path':relative(rawpath),'content_type':mime,
                'role':role,'linked_from':parents or [],'revision_risk':'Original release archive currently hosted; possible unrecorded hosting corrections; not contemporaneous capture.'}
        write_once(metapath,meta)
        return raw,meta
    except Exception as exc:
        error = {'url':url,'accessed_at':now,'role':role,'error':str(exc),'http_status':getattr(exc,'code',None)}
        out = DEST/'errors'/f'{key}.{int(time.time())}.json'
        write_once(out,error)
        print(json.dumps(error),flush=True)
        return None,error

def links(raw, url):
    tree = html.fromstring(raw)
    out = []
    for a in tree.xpath('//a[@href]'):
        href = urllib.parse.urljoin(url,a.get('href'))
        if urllib.parse.urlparse(href).hostname != 'www.federalreserve.gov':
            continue
        text = ' '.join(a.text_content().split())
        out.append({'url':href.split('#')[0],'text':text,'parent_url':url})
    return out

def flat(raw):
    tree = html.fromstring(raw)
    for element in tree.xpath('//script|//style'):
        element.getparent().remove(element)
    return ' '.join(tree.text_content().split())

def infer_survey(link):
    url = link['url'].lower()
    m = re.search(r'(?:sloos-|snloansurvey/|sloos/)(20\d\d)(\d\d)(?:[/.-]|$)', url)
    if m:
        year,month = map(int,m.groups())
        return year, month
    return None

def discover():
    found = {}
    archives = []
    for url in LANDINGS:
        raw, meta = get(url, 'archive_landing')
        if raw is None:
            continue
        ll = links(raw,url)
        for item in ll:
            survey = infer_survey(item)
            if survey and survey[0] in YEARS:
                if re.search(r'(?:default\.htm|sloos-20\d{4}\.htm)$',item['url'],re.I):
                    found[item['url']] = item
            if any(x in item['url'].lower() for x in ['historical','snloansurvey']) and not survey:
                archives.append(item)
        print(json.dumps({'landing':url,'status':meta['http_status'],'links':len(ll),'archive_links':archives}),flush=True)
    # Official historical index links may lead to another official index.
    seen = set(LANDINGS)
    for item in archives[:8]:
        url = item['url']
        if url in seen:
            continue
        seen.add(url)
        raw, meta = get(url,'archive_index',[item['parent_url']])
        if raw is None:
            continue
        for child in links(raw,url):
            survey = infer_survey(child)
            if survey and survey[0] in YEARS and re.search(r'(?:default\.htm|sloos-20\d{4}\.htm)$',child['url'],re.I):
                found[child['url']] = child
    selected = sorted(found.values(), key=lambda x:(infer_survey(x),x['url']))
    version = 'v002' if (DEST/'release_index.v001.json').exists() else 'v001'
    supplemental = [x for x in selected if x['text'].lower() in ['march','september']]
    selected = [x for x in selected if x not in supplemental]
    write_once(DEST/f'release_index.{version}.json',{'records':selected,'count':len(selected),
        'supplemental_excluded':supplemental,'parser_change':'Includes official /data/sloos/YYYYMM/default.htm migration; regular quarterly archive labels only, supplementary March/September excluded before any market outcomes.',
        'selection':'All archive-linked 2000–2025 quarterly original releases. No market returns observed.'})
    print(json.dumps({'discovered_release_pages':len(selected),'first':selected[:3],'last':selected[-3:]}),flush=True)

def release_date(raw):
    text = flat(raw)
    # Do not infer from the survey month or URL. Require a release statement.
    month = '(?:'+'|'.join(MONTHS)+')'
    patterns = [r'(?:For release at|Release Date\s*:|Date of Release\s*:)(.{0,100}?'+month+r'\s+\d{1,2},?\s+20\d{2})',
                r'('+month+r'\s+\d{1,2},?\s+20\d{2}.{0,100}?For release at)']
    for pattern in patterns:
        m = re.search(pattern,text,re.I)
        if not m:
            continue
        quote = m.group(0)
        d = re.search(r'('+month+r')\s+(\d{1,2}),?\s+(20\d{2})',quote,re.I)
        month_name = next(k for k in MONTHS if k.lower()==d.group(1).lower())
        date = dt.date(int(d.group(3)),MONTHS[month_name],int(d.group(2)))
        available = dt.datetime.combine(date+dt.timedelta(days=1),dt.time(),ZoneInfo('America/New_York')).astimezone(dt.timezone.utc)
        return {'publication_date':date.isoformat(),'published_at':None,
                'available_at':available.isoformat(),'publication_evidence_quote':quote,
                'publication_time_quality':'DATE_PROVED_CONSERVATIVE_NEXT_LOCAL_DAY'}
    return {'publication_date':None,'published_at':None,'available_at':None,
            'publication_evidence_quote':None,'publication_time_quality':'POINT_IN_TIME_UNCERTAIN'}

def collect():
    index_version = 'v002' if (DEST/'release_index.v002.json').exists() else 'v001'
    index = json.loads((DEST/f'release_index.{index_version}.json').read_text())['records']
    if len(index)>104:
        raise RuntimeError('More than 104 original release pages; duplicate index requires explicit audit.')
    records = []
    for i,item in enumerate(index):
        raw,meta=get(item['url'],'original_release',[item['parent_url']])
        year,month = infer_survey(item)
        record = {'survey_year':year,'survey_month':month,'source':meta,'tables':[],
                  'value':None,'variable':'Domestic C&I large/middle-market loan standards net tightening percentage'}
        if raw is not None:
            record.update(release_date(raw))
            tablelinks = [x for x in links(raw,item['url']) if re.search(r'(?:table[-_]?1|/table1)(?:\.htm|\.pdf|$)',x['url'],re.I)]
            for table in tablelinks[:1]:
                table_raw,table_meta=get(table['url'],'original_table1',[item['url']])
                record['tables'].append(table_meta)
        else:
            record.update({'publication_date':None,'published_at':None,'available_at':None,
                           'publication_time_quality':'SOURCE_UNAVAILABLE'})
        records.append(record)
        if i%10==0 or i==len(index)-1:
            print(json.dumps({'collected':i+1,'of':len(index)}),flush=True)
    write_once(DEST/f'acquisition_records.{index_version}.json',{'records':records,'raw_observations':len(records),
               'effective_sample_assessment':'Quarterly surveys, serially dependent, respondent pool varies. Independence unknown; not independent investments.'})

def pdf_text(meta):
    path=ROOT/meta['source_path']
    out=DEST/'extracted'/f"{meta['source_sha256']}.txt"
    if not out.exists():
        result=subprocess.run(['pdftotext','-layout',str(path),'-'],capture_output=True,check=True)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_bytes(result.stdout)
    return out.read_text(errors='replace'),relative(out)

def document_text(meta):
    raw=(ROOT/meta['source_path']).read_bytes()
    if raw.startswith(b'%PDF'):
        return pdf_text(meta)
    tree=html.fromstring(raw)
    for element in tree.xpath('//script|//style'):
        element.getparent().remove(element)
    return '\n'.join(' '.join(x.split()) for x in tree.text_content().splitlines()),None

def exact_counts(meta):
    text,path=document_text(meta)
    compressed=' '.join(text.split())
    # Table 1 must refer to domestically chartered respondents, never foreign branches.
    if 'large and middle' not in compressed.lower() or not re.search(r'All\s*Respondents',compressed,re.I):
        return {'value':None,'value_quality':'QUESTION_OR_POPULATION_NOT_VERIFIED','text_path':path}
    if 'branches and agencies of foreign banks' in compressed[:800].lower():
        return {'value':None,'value_quality':'FOREIGN_BANKS_NOT_DOMESTIC','text_path':path}
    labels=['Tightened considerably','Tightened somewhat','Remained basically unchanged','Eased somewhat','Eased considerably','Total']
    counts={}
    rows={}
    if meta['url'].lower().endswith('.htm'):
        tree=html.fromstring((ROOT/meta['source_path']).read_bytes())
        table=None
        for candidate in tree.xpath('//table'):
            ss=' '.join(candidate.text_content().split())
            if all(label.lower() in ss.lower() for label in labels[:-1]):
                table=candidate
                break
        if table is None:
            return {'value':None,'value_quality':'EXACT_TABLE_NOT_FOUND','text_path':path}
        for row in table.xpath('./tr|./thead/tr|./tbody/tr|./tfoot/tr'):
            cells=[' '.join(c.text_content().split()) for c in row.xpath('./th|./td')]
            if len(cells)<3:
                continue
            label=next((lab for lab in labels if cells[0].lower().rstrip('.')==lab.lower()),None)
            if label:
                if label in counts or not re.fullmatch(r'\d+',cells[1]) or not re.fullmatch(r'\d+(?:\.\d+)?',cells[2]):
                    return {'value':None,'value_quality':'AMBIGUOUS_EXACT_COUNT_ROW','text_path':path}
                counts[label]=int(cells[1]); rows[label]={'quote':' | '.join(cells),'published_pct':float(cells[2])}
    else:
        # Restrict to first large/middle standards section before small-firm question B.
        start=re.search(r'A\.\s*Standards for large and middle[-–]?market firms',compressed,re.I)
        if not start:
            return {'value':None,'value_quality':'LARGE_MIDDLE_SECTION_NOT_FOUND','text_path':path}
        stop=re.search(r'B\.\s*Standards for small firms',compressed[start.end():],re.I)
        section=compressed[start.end():start.end()+stop.start()] if stop else compressed[start.end():start.end()+2200]
        for label in labels:
            mm=list(re.finditer(re.escape(label)+r'\s+(\d+)\s+(\d+(?:\.\d+)?)',section,re.I))
            if len(mm)==1:
                counts[label]=int(mm[0].group(1));rows[label]={'quote':mm[0].group(0),'published_pct':float(mm[0].group(2))}
    if set(counts)!=set(labels) or counts['Total']<=0 or sum(counts[k] for k in labels[:-1])!=counts['Total']:
        return {'value':None,'value_quality':'COUNT_TOTAL_FAILED','counts':counts,'rows':rows,'text_path':path}
    n=counts['Total']
    if any(abs(100*counts[k]/n-rows[k]['published_pct'])>.061 for k in labels):
        return {'value':None,'value_quality':'PUBLISHED_PERCENT_COUNT_MISMATCH','counts':counts,'rows':rows,'text_path':path}
    numerator=counts['Tightened considerably']+counts['Tightened somewhat']-counts['Eased somewhat']-counts['Eased considerably']
    return {'value':100*numerator/n,'value_quality':'EXACT_DERIVED_FROM_ORIGINAL_RESPONDENT_COUNTS',
            'counts':counts,'rows':rows,'text_path':path,'numerator':numerator,'denominator':n,
            'formula':'100*(tightened_considerably+tightened_somewhat-eased_somewhat-eased_considerably)/all_domestic_respondents'}

def proof_from_text(text):
    month='(?:'+'|'.join(MONTHS)+')'
    text=' '.join(text.split())
    # Original PDF covers explicitly state release date, separated from survey month.
    m=re.search(r'For release at.{0,120}?('+month+r')\s+(\d{1,2}),?\s+(20\d{2})',text,re.I)
    if not m:
        return None
    month_name=next(k for k in MONTHS if k.lower()==m.group(1).lower())
    date=dt.date(int(m.group(3)),MONTHS[month_name],int(m.group(2)))
    return {'date':date,'quote':m.group(0),'quality':'ORIGINAL_RELEASE_COVER_DATE'}

def date_papers():
    records=json.loads((DEST/'acquisition_records.v002.json').read_text())['records']
    proofs=[]
    for i,record in enumerate(records):
        raw=(ROOT/record['source']['source_path']).read_bytes()
        doclinks=[x for x in links(raw,record['source']['url']) if
                  x['url'].lower().endswith('.pdf') and ('fullreport' in x['url'].lower() or 'full-report' in x['url'].lower() or x['text'].lower() in ['full report','pdf'] or
                  'summary.pdf' in x['url'].lower())]
        proof=None; docs=[]
        for item in doclinks[:1]:
            paper,meta=get(item['url'],'original_full_report_cover',[record['source']['url']])
            if paper is None:
                continue
            txt,txtpath=document_text(meta)
            proof=proof_from_text(txt[:7000])
            docs.append({'source':meta,'text_path':txtpath,'cover_excerpt':txt[:1300]})
            if proof:
                proof={'publication_date':proof['date'].isoformat(),'quote':proof['quote'],'quality':proof['quality'],
                       'source':meta,'text_path':txtpath}
        proofs.append({'survey_year':record['survey_year'],'survey_month':record['survey_month'],
                       'release_url':record['source']['url'],'date_proof':proof,'papers':docs})
        if i%10==0 or i==len(records)-1:
            print(json.dumps({'date_papers':i+1,'of':len(records),'date_proved_so_far':sum(bool(x['date_proof']) for x in proofs)}),flush=True)
    version='v002' if (DEST/'date_proofs.v001.json').exists() else 'v001'
    write_once(DEST/f'date_proofs.{version}.json',{'records':proofs,'parser_note':'Explicit original cover release-date statement; official href variants full-report and plain SLOOS PDF included. No market labels used.'})

def calendars():
    records=json.loads((DEST/'acquisition_records.v002.json').read_text())['records']
    previous=json.loads((DEST/'date_proofs.v001.json').read_text())['records']
    proven={x['release_url']:x for x in previous if x['date_proof']}
    entries=[]
    for record in records:
        if record['source']['url'] in proven:
            continue
        raw=(ROOT/record['source']['source_path']).read_bytes()
        text=flat(raw)
        mm=re.search(r'Last update:\s*('+'|'.join(MONTHS)+r')\s+(\d{1,2}),?\s+(20\d{2})',text,re.I)
        # Last update is only an URL-location clue; it never proves the release date.
        if not mm:
            entries.append({'release_url':record['source']['url'],'date_proof':None,'reason':'NO_CALENDAR_LOCATION_CLUE'})
            continue
        month_name=next(k for k in MONTHS if k.lower()==mm.group(1).lower())
        clue=dt.date(int(mm.group(3)),MONTHS[month_name],int(mm.group(2)))
        url=BASE+'/newsevents/'+str(clue.year)+'-'+month_name.lower()+'.htm'
        calendar,meta=get(url,'historical_release_calendar',[record['source']['url']])
        proof=None
        if calendar is not None:
            tree=html.fromstring(calendar)
            matches=[]
            for node in tree.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," row ")]'):
                cols=node.xpath('./div')
                if len(cols)!=3:
                    continue
                ss=[' '.join(c.text_content().split()) for c in cols]
                if 'Senior Loan Officer Opinion Survey' in ss[1] and re.fullmatch(r'\d{1,2}',ss[2]):
                    matches.append((int(ss[2]),' | '.join(ss)))
            if len(matches)==1:
                day,quote=matches[0]
                actual=dt.date(clue.year,clue.month,day)
                # Original page and calendar must agree; differing dates need extra audit.
                if actual==clue:
                    proof={'publication_date':actual.isoformat(),'quote':quote,
                           'quality':'OFFICIAL_HISTORICAL_CALENDAR_MATCHING_ORIGINAL_PAGE_DATE','source':meta,'text_path':None}
            entries.append({'release_url':record['source']['url'],'date_proof':proof,'calendar_source':meta,
                            'location_clue':mm.group(0),'matches':matches})
        else:
            entries.append({'release_url':record['source']['url'],'date_proof':None,'calendar_source':meta,'location_clue':mm.group(0)})
    write_once(DEST/'calendar_proofs.v001.json',{'records':entries,'selection':'All original releases without explicit PDF cover date; last-update month only locates official calendar; exact matching required.'})
    print(json.dumps({'calendar_proved':sum(bool(x['date_proof']) for x in entries),'attempted_records':len(entries)}),flush=True)

def extract():
    records=json.loads((DEST/'acquisition_records.v002.json').read_text())['records']
    dp='v002' if (DEST/'date_proofs.v002.json').exists() else 'v001'
    proofs=json.loads((DEST/f'date_proofs.{dp}.json').read_text())['records']
    proofs+=json.loads((DEST/'calendar_proofs.v001.json').read_text())['records']
    dates={x['release_url']:x['date_proof'] for x in proofs if x['date_proof']}
    final=[]
    for record in records:
        table=record['tables'][0]
        value=exact_counts(table)
        dateproof=dates.get(record['source']['url'])
        if dateproof and dateproof['quality']=='ORIGINAL_RELEASE_COVER_DATE':
            fullcheck=exact_counts(dateproof['source'])
            comparable=fullcheck.get('value') is not None
            value['dated_full_report_crosscheck']={'source_path':dateproof['source']['source_path'],
                'source_sha256':dateproof['source']['source_sha256'],'parser_quality':fullcheck['value_quality'],
                'counts_match':value.get('counts')==fullcheck.get('counts') if comparable else None,
                'note':'Some modern full reports contain only summary rather than table; UNKNOWN crosscheck does not replace original exact table evidence.'}
            if comparable and value.get('counts')!=fullcheck.get('counts'):
                value['value']=None;value['value_quality']='DATED_RELEASE_TABLE_COUNT_MISMATCH_QUARANTINED'
        good=bool(dateproof and value['value'] is not None)
        available=None
        if dateproof:
            dd=dt.date.fromisoformat(dateproof['publication_date'])
            available=dt.datetime.combine(dd+dt.timedelta(days=1),dt.time(),ZoneInfo('America/New_York')).astimezone(dt.timezone.utc).isoformat()
        final.append({'record_id':f"SLOOS_ORIGINAL_{record['survey_year']}_{record['survey_month']:02d}",
                      'survey_year':record['survey_year'],'survey_month':record['survey_month'],
                      'series_id':'SLOOS_CI_LARGE_MIDDLE_NET_TIGHTENING',
                      'source_id':f"FED_SLOOS_TABLE1_{record['survey_year']}_{record['survey_month']:02d}",
                      'source_sha256':table['source_sha256'],'source_path':table['source_path'],'source_url':table['url'],
                      'original_release_source':record['source'],
                      'publication_date':dateproof['publication_date'] if dateproof else None,
                      'published_at':available,'available_at':available,
                      'timestamp_semantics':'published_at field is conservative availability upper bound, not claimed actual release time; date-only next New York day 00:00.',
                      'pit_status':'VERIFIED_CONSERVATIVE_SESSION_LAG' if good else 'POINT_IN_TIME_UNCERTAIN',
                      'value':value['value'] if good else None,'unusable_extracted_value':value['value'] if not good else None,
                      'unit':'PERCENTAGE_POINTS_OF_RESPONDENTS_NET_TIGHTENING',
                      'value_evidence':value,'availability_evidence':dateproof,
                      'revision_risk':'Currently hosted original survey release/table; not separately archived contemporaneous vendor snapshot; possible silent corrections.',
                      'quality':'DATE_AND_EXACT_ORIGINAL_COUNTS_VERIFIED' if good else 'DATE_OR_EXACT_COUNTS_NOT_PROVED',
                      'market_scope':'US domestic banks only; not local credit of non-US assets.'})
    summary={'raw_observations':len(final),'usable_original_releases':sum(x['value'] is not None for x in final),
             'exact_numeric_tables':sum(x['value_evidence']['value'] is not None for x in final),
             'publication_dates_verified':sum(x['available_at'] is not None for x in final),
             'effective_sample_assessment':{'n_effective':None,'year_clusters':len(set(x['survey_year'] for x in final if x['value'] is not None)),
                 'notes':'Quarterly surveys overlap bank respondents and lending cycle; serial/global regime dependence. Credit records are source releases, not independent investments.'},
             'no_outcome_data_read':True}
    write_once(DEST/'credit.records.v001.json',{'records':final,'summary':summary})
    write_once(DEST/'credit.records.lock.v001.json',{'sha256':sha((DEST/'credit.records.v001.json').read_bytes()),
                   'code_sha256':sha(Path(__file__).read_bytes()),'summary':summary})
    print(json.dumps(summary),flush=True)

def normalize():
    original=DEST/'credit.records.v001.json'
    obj=json.loads(original.read_text())
    audit=[]
    for record in obj['records']:
        prior_available=record['available_at'];prior_value=record['value']
        evidence=record['availability_evidence']
        record['published_at_upper_bound']=prior_available
        record['observed_server_publication_timestamp_known']=False
        if evidence is None:
            record['published_at_precision']='UNKNOWN'
            record['published_at_is_official_stated_exact_minute']=False
        elif evidence['quality']=='ORIGINAL_RELEASE_COVER_DATE':
            quote=evidence['quote']
            match=re.search(r'For release at\s*(\d{1,2}):(\d{2})\s*([ap])\.?\s*m\.?\s*(?:ET|EST|EDT)',quote,re.I)
            if match is None:
                raise RuntimeError('Cannot normalize official time: '+record['record_id']+' '+quote)
            hh=int(match.group(1));minute=int(match.group(2));am_pm=match.group(3).lower()
            if not 1<=hh<=12 or not 0<=minute<=59:
                raise RuntimeError('Invalid stated release minute')
            hour=hh%12+(12 if am_pm=='p' else 0)
            date=dt.date.fromisoformat(record['publication_date'])
            published=dt.datetime.combine(date,dt.time(hour,minute),ZoneInfo('America/New_York')).astimezone(dt.timezone.utc)
            record['published_at']=published.isoformat()
            record['published_at_precision']='OFFICIAL_RELEASE_STATEMENT_MINUTE'
            record['published_at_is_official_stated_exact_minute']=True
            record['timestamp_semantics']='published_at is original PDF officially stated release date and ET minute converted with America/New_York; it is not an observed server log. available_at remains conservative next-local-day 00:00.'
            if published>=dt.datetime.fromisoformat(record['available_at']):
                raise RuntimeError('Stated release time not before conservative availability')
        else:
            record['published_at_precision']='DATE_ONLY_CONSERVATIVE_UPPER_BOUND'
            record['published_at_is_official_stated_exact_minute']=False
            record['timestamp_semantics']='Official historical calendar proves publication_date. published_at stores conservative next-local-day 00:00 upper bound, explicitly not an exact release timestamp; available_at is unchanged.'
        audit.append({'record_id':record['record_id'],'value_unchanged':record['value']==prior_value,
                      'available_at_unchanged':record['available_at']==prior_available,
                      'published_at_precision':record['published_at_precision']})
    obj['normalization']={'previous_version':'credit.records.v001.json','previous_sha256':sha(original.read_bytes()),
                         'reason':'Separate official stated release minute from conservative availability; date-only calendar records retain explicitly typed upper bound. Values, availability, scope, missingness and selection remain identical.'}
    write_once(DEST/'credit.records.v002.json',obj)
    write_once(DEST/'credit.records.lock.v002.json',{'sha256':sha((DEST/'credit.records.v002.json').read_bytes()),
        'previous_sha256':sha(original.read_bytes()),'code_sha256':sha(Path(__file__).read_bytes()),
        'summary':obj['summary'],'normalization':obj['normalization']})
    write_once(DEST/'normalization_comparison.v002.json',{'records':audit,'all_values_unchanged':all(x['value_unchanged'] for x in audit),
        'all_available_at_unchanged':all(x['available_at_unchanged'] for x in audit),
        'raw_observations':len(audit),'effective_sample_assessment':obj['summary']['effective_sample_assessment']})
    print(json.dumps({'path':relative(DEST/'credit.records.v002.json'),'sha256':sha((DEST/'credit.records.v002.json').read_bytes()),
        'raw_observations':len(audit),'usable_original_releases':obj['summary']['usable_original_releases'],
        'values_and_available_at_unchanged':True}),flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['discover','collect','date_probe','calendar_probe','date_papers','calendars','extract','normalize'])
    args=parser.parse_args()
    print(json.dumps({'registration':register(args.mode)}),flush=True)
    if args.mode=='discover':
        discover()
    elif args.mode=='collect':
        collect()
    elif args.mode=='date_papers':
        date_papers()
    elif args.mode=='calendars':
        calendars()
    elif args.mode=='extract':
        extract()
    elif args.mode=='normalize':
        normalize()
    elif args.mode=='date_probe':
        for url in [BASE+'/feeds/sloos.html',BASE+'/feeds/sloos.xml',BASE+'/boarddocs/SnLoanSurvey/200001/summary.pdf',BASE+'/boarddocs/SnLoanSurvey/default.htm',
                    'https://alfred.stlouisfed.org/release/dates?rid=191',
                    'https://fred.stlouisfed.org/release/dates?rid=191']:
            raw,meta=get(url,'publication_date_probe')
            if raw is not None:
                print(json.dumps({'url':url,'status':meta['http_status'],'path':meta['source_path'],'sha':meta['source_sha256']}),flush=True)
    else:
        for url in [BASE+'/newsevents/2023-may.htm',BASE+'/newsevents/2008-august.htm',BASE+'/newsevents/2008august.htm',
                    BASE+'/newsevents/2000-february.htm',BASE+'/newsevents/2000february.htm']:
            raw,meta=get(url,'historical_release_calendar')
            if raw is not None:
                print(json.dumps({'url':url,'status':meta['http_status'],'path':meta['source_path'],'sha':meta['source_sha256']}),flush=True)

if __name__=='__main__':
    main()
