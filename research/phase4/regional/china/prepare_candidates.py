import json,re,html
from pathlib import Path
from urllib.parse import urljoin
ROOT=Path(__file__).resolve().parents[4]
S=ROOT/'research/phase4/sources/china';R=ROOT/'research/phase4/regional/china'
candidates=[];plan=[]
for f in sorted(S.glob('CN-S-PBOC-DIR-*.html')):
 s=f.read_text()
 for url,title,day in re.findall(r'<a\s+href="([^"]+)"[^>]*>(公开市场业务交易公告[^<]+)</a></font><span[^>]*>(\d{4}-\d{2}-\d{2})</span>',s):
  candidates.append(dict(family='央行执行',url=urljoin('https://www.pbc.gov.cn/',url),title=html.unescape(title),published_date=day,catalog_source=f.name,eligible='2008-01-01'<=day<='2025-12-31'))
elig=sorted({x['url']:x for x in candidates if x['eligible']}.values(),key=lambda x:(x['published_date'],x['url']))
selected=[elig[i*(len(elig)-1)//9] for i in range(10)] if len(elig)>10 else elig
for i,x in enumerate(selected,1):
 x['selected']=True;plan.append(dict(x,source_id=f'CN-S-PBOC-OMO-{i:02d}',role='EVENT_SOURCE'))
for f in S.glob('CN-S-HUIJIN-DIR*.html'):
 for u in re.findall(r'<a[^>]+href="(/huijin-inv/(?:c100074|c100077|SC20252)/\d{4}-\d{2}/[^"?]+\.shtml)"',f.read_text()):
  plan.append(dict(source_id='CN-S-HUIJIN-'+u.split('/')[-1].split('.')[0],url=urljoin('https://www.huijin-inv.cn/',u),family='政策性/国家资本',role='CANDIDATE_CONTENT',catalog_source=f.name))
extra=[
('INS-2014','保险配置','https://www.iamac.org.cn/flfg/gfxwj/201503/t20150319_298.html'),
('INS-2015','保险配置','https://www.nfra.gov.cn/cn/view/pages/ItemDetail_gdsj.html?docId=17512&docType=2'),
('INS-2020','保险配置','https://www.beijing.gov.cn/ywdt/zybwdt/202007/t20200719_1951762.html'),
('INS-2020-LAW','保险配置','https://policy.mofcom.gov.cn/claw/clawContent.shtml?id=70890'),
('INS-2025','保险配置','https://www.nfra.gov.cn/cn/view/pages/ItemDetail.html?docId=1203998&itemId=928'),
('INS-2025-MIRROR','保险配置','https://www.shanghai.gov.cn/gwk/search/content/2d9f79775c814b41b06d0f6c4bd8656e'),
('MARGIN-2015','融资融券','https://www.sse.com.cn/aboutus/mediacenter/hotandd/c/c_20151113_4012108.shtml'),
('MARGIN-2015-LAW','融资融券','https://www.csrc.gov.cn/csrc/c106256/c1654005/content.shtml'),
('MARGIN-2023','融资融券','https://www.csrc.gov.cn/csrc/c100028/c7428485/content.shtml'),
('MARGIN-2024','融资融券','https://www.csrc.gov.cn/csrc/c100028/c7461992/content.shtml'),
('MARGIN-2024-MIRROR','融资融券','https://jrj.sh.gov.cn/RDHY238/20240206/11ff6c2c3a594a8797cb6a6cab3cbf49.html'),
('CORP-2019','公司/产业资金','https://www.szse.cn/aboutus/trends/news/t20190111_564058.html'),
('CORP-2020','公司/产业资金','https://www.csrc.gov.cn/csrc/c100028/c1000767/content.shtml'),
('CORP-2023','公司/产业资金','https://www.sse.com.cn/aboutus/mediacenter/hotandd/c/c_20231031_5728276.shtml'),
('CORP-2024','公司/产业资金','https://www.csrc.gov.cn/csrc/c100029/c7457231/content.shtml'),
('CORP-2025','公司/产业资金','https://www.csrc.gov.cn/zhejiang/c100657/c7556574/content.shtml'),
('CORP-RELOAN-2024','公司/产业资金','https://www.csrc.gov.cn/csrc/c100028/c7513043/content.shtml'),
('CORP-RELOAN-2024-PBOC','公司/产业资金','https://www.pbc.gov.cn/redianzhuanti/118742/5444129/5444142/481faf4556cb42a5b444677b9673ea5c/index.html'),
('CORP-LOAN-2025-Q1','公司/产业资金','https://www.pbc.gov.cn/zhengcehuobisi/125207/125227/125957/f5c4690f2cbd40918bf24c2d39ac58af/2025091218344076234/2025081517321679368.pdf'),
('CORP-LOAN-2024-Q4','公司/产业资金','https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/5587716/2025022618190099812.pdf'),
]
for sid,f,u in extra:plan.append(dict(source_id='CN-S-'+sid,url=u,family=f,role='SEARCH_CANDIDATE',catalog_status='PARTIAL_CATALOG'))
plan=list({x['source_id']:x for x in plan}.values())
(R/'all_candidates_initial.json').write_text(json.dumps(candidates+plan,ensure_ascii=False,indent=2))
(R/'event_download_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
print('PBOC discovered',len(candidates),'eligible',len(elig),'selected',len(selected),'total downloads',len(plan))
print([(x['published_date'],x['title']) for x in selected])
