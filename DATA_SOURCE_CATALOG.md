# DATA_SOURCE_CATALOG

ROUND_002；公开来源小规模测试，不把“HTTP 200”当成历史时间可得性证明。用户本轮明确授权公开互联网资料，优先级高于 ROUND_001 的不联网边界。环境状态显示 HTTP 规则 `unrestricted / enforced`，没有已配置数据 API 密钥。联网执行通过继承的代理与 TLS 验证；旧子代理的 socket 沙箱仍被限制，下载由当前可联网主线程运行。

下载和可得性分别记录在 [官方访问审计](research/audit/ROUND_002_OFFICIAL_ACCESS.json)、[官方来源清单](data/manifests/ROUND_002_OFFICIAL_SOURCES.json)；每个源保留 URL、抓取时间、源文件哈希、原始正文、真实发布时间、`available_at` 与 vintage。原始 HTML 的今天导航和页脚不属于当时信息集。保留的档案正文是官方原始发布版本，但没有额外 Wayback 时间见证；不宣称具有不可变外部历史快照。

## 来源、适用性与局限

| Source | Data Type | Markets | History | Frequency | Point-in-Time Quality | Revision Risk | Survivorship Risk | Access Method | Reliability | Known Limitations |
|---|---|---|---|---|---|---|---|---|---|---|
| Federal Reserve 原始 FOMC statements | 货币政策、目标利率区间、原始经济评述 | 美国；海外只作美国外部环境 | 官方年度档案；本包 2016–2023 每年 9 月一份 | 每次会议／特别公告 | 原文日期＋`For release at 2 p.m. EDT` 验证后为 VERIFIED；按实际时区转 UTC | 原声明低；页面导航可更新，政策评述不能冒充后来量化数据 | 不涉及个股存续；会议选择按固定日历，不按政策结果 | 免费原 HTML：`federalreserve.gov/newsevents/pressreleases/monetaryYYYYMMDDa.htm` | 官方一手；原文可追溯 | 政策意图不等于实现；不补不存在的市场预期、政策 surprise 或日本／香港本地政策 |
| BLS CPI 原始 archived release | 初次发布 CPI 同比、季调环比与原文 | 美国 | 官方 archive；本包 2016–2023 八份 8 月数据在 9 月发布 | 月度 | 原文 embargo 日期＋8:30 a.m. EDT／ET 核验后 VERIFIED；ET 用 America/New_York 实际 DST 转换；观察月与发布日明确分开 | 当前 SA 历史序列会年修；本包只取该次原 release，不取今天修订列 | 不涉及证券存续；统计方法及样本有演变 | 免费原 HTML：`bls.gov/news.release/archives/cpi_MMDDYYYY.htm` | 官方一手；高 | 同一 release 中更早月份可能已修订；不能把它们标为最初 vintage；CPI-U 不等于 PCE |
| FRED market series（DGS2／DGS10／DFII10／信用 OAS／广义美元） | 收益率、信用、美元指数 | 美国／全球美元环境 | 各系列起点不同；本次拟取 2015–2023 小窗 | 日频为主 | 今天下载的历史值未验证历史 vintage，统一 POINT_IN_TIME_UNCERTAIN，隔离 Stage A | 收益率可校正，指数方法／权重可变，信用供应商也可能更正 | 不涉及个股；债券篮子规则和存续变化仍须注意 | FRED graph CSV，免费、无需 key；API 通常需要 key | 汇集官方／供应商资料；高 provenance，接口可用性逐次验 | 日值不是当日即时公开；H.15 存在发布时点；延期一天不能修复未验证 vintage；收益率变化不是债券总回报 |
| ALFRED | 宏观首次发布与修订 vintage | 以美国为主 | 随系列而异；vintage 覆盖并非从 observation 起点完整 | 月／季等 | 正确 `realtime_start/end` 及 vintage 有潜力满足 PIT；本轮没有把未经核验值导入 | 其用途是显式管理修订，仍须核对 exact release time | 不涉及个股 | 官方网页／CSV；API 测试无 key 请求，错误即记访问限制 | FRED 历史版本服务；高 | URL 参数写 vintage 不等于真正返回该 vintage；API key 不存在时不杜撰；日级 vintage 仍不足以说明当天开盘可得 |
| US Treasury 原始 daily rates | 国债名义／实际 par 曲线 | 美国 | 官网年度表，年范围依产品 | 日频 | 今日历史表无历史版本时间见证：隔离；原当日发布文档另核验 | 历史更正、曲线方法变化 | 不涉及个股 | 免费 Treasury 年表／XML | 官方一手；高 | Par／constant maturity 不是证券持有回报；发布时间和交易执行仍须独立定义 |
| Yahoo Finance chart | ETF／指数 OHLC、分红、拆股；辅助 FX | 美／港／中／欧／日，依代码实际覆盖 | 每代码不同；本包只取已固定样本窗口 | 日／周频 | raw OHLC 可作历史价格有限研究；今天复权值不得进入事前特征；报价公开时点使用市场会话保守规则 | 历史修正、拆股呈现、复权算法／数据商更新 | 选现存 ticker 有存续和可得性偏差；指数也存在当前成分污染 | chart JSON，免费接口但无永久服务保证 | 二手；需 action、OHLC 和来源交叉核对 | 不保证所有市场／代码长期可用；禁止称全市场或退市覆盖；`Adj Close` 不能与拆股分红重复计算；指数非可执行证券 |
| Stooq | OHLC／指数／ETF；价格交叉核验 | 多市场，依实际代码 | 依代码 | 日频／周频 | 没有独立历史快照；未明确 action／调整口径的价格不可直接当未复权 PIT | 历史校正与调整规则需确认 | 当前代码历史幸存者覆盖不完整 | 免费 CSV，经实际 probe；不使用验证码绕过 | 二手；适合交叉核验 | 分红和拆股口径可能未充分公开；无 action 不能声称真实总回报；接口可访问不代表价格 basis 已证明 |
| Nasdaq／exchange public pages | 指数／证券历史价格、公告 | 依交易所 | 依接口／网页保留范围 | 日频／事件 | 公告原发布时间有潜力；当前历史价格和 constituents 仍需版本核验 | 价格更正、接口 schema、指数重算 | 当前上市公司／成分有存续偏差 | 免费网页／API；本轮未导入也不把未测试写成失败 | 交易所公告为一手；聚合行情依产品 | 历史深度和批量访问受限制；本轮无需扩大全市场数据 |
| SEC EDGAR 原 filings | 财务报告、事件、内部人、资本行动 | 美国上市发行人 | 历史 filings，submissions 的主表不等于完整历史 | 事件／季／年 | 原 accession＋accepted timestamp 可用；period end 不可用作 available_at | Amendments／restatements；today companyfacts 必须按 accession／filed 过滤 | 覆盖退市发行人但需要历史 universe；从今天公司列表选样仍偏 | 免费 data.sec.gov／EDGAR，遵守公开合理频率 | 官方监管一手；高 | 本轮只测试可达性，未导入个股财务；财报实际 earliest 可用时点可能更早 earnings release，不能反过来补录 |
| 公司 IR | 财报、订单、CapEx、guidance、回购／增持计划 | 多市场 | 公司自行保留，旧文件可能下线 | 事件／季 | 有原公告时间及版本才可用；只有今日网页则 uncertain | 更新、重述、旧页覆盖 | 仅存续／资料齐全公司有选择风险 | 免费原公告 PDF／网页；本轮未导入 | 一手管理层披露，但有陈述动机 | 没有 historical consensus 不能标盈利 surprise；计划与实施、报告期与公告日必须分开 |
| HKMA 原政策公告 | Base rate、联系汇率政策 | 香港 | 新闻档案依日期 | 事件 | 原 dated release 可核发布日期，缺时刻按既定次日保守规则且保留精度；本轮未喂当地宏观 | 原公告低；网页迁移／订正 | 不涉及证券 | 官方 archive HTML；本轮 probe 不等于导入 | 官方一手；高 | Fed policy 不等于 HKMA 当时实施，也不等于港股上市公司经营环境；候选 URL 404 不能说全站不可用 |
| BOJ 原声明／outlook | 日本政策、原始经济展望 | 日本 | 官方 archives | 会议／季度 | 原 PDF 的日期可核；时刻需要另证，不能用 PDF mtime／下载时点 | 原稿低，摘要翻译有时晚于日本原稿 | 不涉及证券 | 官方 HTML／PDF；本轮 probe 不等于导入 | 官方一手；高 | Outlook 对未来是当时预测；不能拿后来实现数据替换；美联储资料不足以定义日本本地 regime |
| ECB 原政策 release | 欧洲政策／利率 | 欧元区 | 官方 dated archives | 会议／事件 | 日期和发布时刻原文验证后可用；本轮只有 access test | 原声明低；序列会修订 | 不涉及证券 | 免费原 HTML | 官方一手；高 | 未导入欧洲政策解释，更没有完整欧洲发行人 PIT 财务 |
| BEA 原 news releases | GDP／PCE first estimates、修订 | 美国 | 原年度 release archives | 月／季 | 原 release vintage＋发布时间可用；本轮 landing page probe 不证明 archive 已准入 | GDP／PCE 修订显著 | 不涉及证券 | 免费 release HTML／PDF；API 使用边界另核验 | 官方一手；高 | 今日数据表不能替代 advance／second／third vintage；本轮没有导入 GDP／PCE |
| 中国国家统计局 NBS／人民银行 PBOC | 中国增长／通胀／政策 | 中国内地 | 历史公告深度随栏目，网页迁移 | 月／季／政策事件 | 原公告发布时间与当时版本需逐条核验；本轮首页可达不等于历史数据可用 | 宏观修订、定义变化；政策宣布／执行分开 | 不涉及证券，指数证券池仍另需核验 | 免费官方公开网页；不强行导入 | 官方一手；高 | 没有可用原 release 不用模型记忆补中国宏观；不能套美国 CPI 推断中国通胀 |

## 访问测试与准入

| 已测试来源／请求 | Tested Date（UTC） | Access Status | 本轮准入结果 |
|---|---|---|---|
| Fed 2016–2023 原始 9 月 FOMC statements，8 个原 HTML | 2026-10-08；每请求时刻见官方访问审计 | 8／8 HTTP 200，源字节及 SHA-256 已保存 | 8／8 原文日期＋18:00 UTC 可核；原目标利率区间有逐条原文证据 |
| BLS 2016–2023 8 月 CPI 初次 release，9 月发布的8个原 HTML | 2026-10-08；每请求时刻见官方访问审计 | 8／8 HTTP 200，源字节及 SHA-256 已保存 | 8／8 发布日期＋12:30 UTC 可核；headline／core 同比、headline 季调环比均从当次原稿提取 |
| Yahoo chart：SPY／恒生指数／日经225 | 2026-10-08 16:06 UTC；市场 manifest 保留精确请求时刻 | 3／3 HTTP 200；三份真实原 JSON 已保存 | 原始供应商 vintage 未证；只作带明确限制的历史价格回放；当时 open／close 时间是交易会话时间，非网站发布快照 |
| Stooq `spy.us` CSV 最小请求 | 2026-10-08；主线程实际初始探测报告 | HTTP 200（该次探测），本目录无独立保存响应 | 可达；调整／行动口径尚未核验，不导入主标签或主特征 |
| FRED `DGS10` graph CSV 最小请求 | 2026-10-08；主线程实际初始探测报告 | HTTP 503（该次请求），本目录无独立保存响应 | 请求失败，不泛化成全来源失效；即使重试成功也因未核历史 vintage 隔离 |
| ALFRED／SEC／BOJ／HKMA／NBS／PBOC／ECB／BEA／Treasury 的具体最小请求 | 若访问审计 `source_probes` 没有记录则未完成实际请求 | `NOT_TESTED_IN_CURRENT_DOWNLOAD_PACK`，脚本已给出请求 | 无已导入观测，不以潜在优质来源冒充数据已可用 |
| Nasdaq／交易所完整历史、公司 IR／FRED 其他 series | 本包未实际请求 | `NOT_TESTED` | 非本包必需，作为下一轮推荐来源；不把“没试”写作不可访问 |

官方数据检查见 [ROUND_002_OFFICIAL_METADATA_QA.json](research/audit/ROUND_002_OFFICIAL_METADATA_QA.json)：16 条均通过源哈希、公布时刻、截止前可得、CPI reference period、正文与当前导航隔离及数字原文证据检查。原数据不会因宏观看起来合理就自动覆盖香港／日本本地环境。

实际测试时间、HTTP 状态、字节数、错误以及源哈希以 JSON 审计为准。网站返回 403／404／429／503 分别表示该请求失败，不能泛化成整个来源不可用；出现错误后不会悄悄以模型记忆、未注明镜像或修订后数值替换。成功下载也不会自动获得 PIT 准入。

本轮核心准入仅为官方 archived FOMC 与 CPI 的原始发布记录、已核验价格／行动资料，以及明确的缺失字段。FRED 当前历史下载即使成功也置于 `data/quarantine/round_002/fred_current_history/`，`eligibility=EXCLUDED_STAGE_A`。宏观同比只使用该次原 release，而不是观察月末或今日历史序列。

免费公开不等于长期 API 合约。保留最小引用与研究原文件，记录原网址和版本；若以后复用服务、公开分发完整行情或大批量下载，应核对该来源当时使用条件。本轮没有购买数据、没有全市场采集、没有新闻大爬虫。

## 本包没有回答的问题

估值、盈利一致预期／修正、信用原 vintage、资金流、市场宽度、订单、资本支出、资本行动、内部人、政策实施、新闻连续性和情绪资料均未完整覆盖。缺失须在每个 episode 写 `UNAVAILABLE`，不能从价格趋势或后来故事反推。

只研究固定几个当时已上市 ETF／指数代理不需要全市场个股数据库，但仍是局部、偏存续的样本，不支持“所有股票”或所有行业的结论。原官方 timestamp 与分阶段文件隔离可以约束数据泄漏，却不能消除语言模型训练中的历史记忆，也不能把回放改称真正未见未来的前瞻实验。

## Phase2新增来源实测

SEC companyfacts/submissions MSFT均HTTP200；两2016/2023原filing package的8source字节与8facts通过离线独立核验。原SEC可以提供filing accepted时间，保守次日可用；今日companyfacts仅locator，按财期取最新值不准入。原始filing单位/报表范围/上下文与revision另核，不能将2份文件当盈利预期样本。19个市场source中CSI300/CHINEXT仅当前1行（HTTP200但无历史），SSE历史可用；XLF隔离、BIL含真实普通reverse split。ALFRED一个vintage请求503，Treasury一个URL404，未将其写成来源整体不可用。所有数据免费公开取得，本轮没有新增海量数据。


## Phase3来源实测与新增限制

|Source|Data Type|Markets|History|Frequency|Point-in-Time Quality|Revision Risk|Survivorship Risk|Access Method|Reliability|Known Limitations|
|---|---|---|---|---|---|---|---|---|---|---|
|Fed archived regular SLOOS Table1+original report PDF|All Domestic Respondents大型/中型C&I标准net收紧|US only|104季度2000–2025；85时间可用2004–2025|quarterly|78原cover release minute、7官方calendar date保守次日；19UNKNOWN不喂A|今天托管archive静默更正风险；整数counts口径保留|银行响应样本构成演变，不等借款人余额加权|免费原HTML/PDF，293源字节+98derived留存|一手原发布；逐表人数/时间独立核验|不是overall信用安全、spread/default；firstyears timestamp缺，不移植海外|
|Yahoo chart Phase3 fixed26asset requests|dailyOHLC/actions|US/CN/HK/JP/EU/DE/UK|固定2000–2026来源请求，实际工具inception不同|daily|RECONSTRUCTED_NOT_ARCHIVED；逐T只取当时已发生行情/行动|供应商历史校正与分红金额未逐笔独立证|现存ETF选择、历史closed funds缺|免费接口原字节保留、24success/23admitted|二手，时间/价格/行动核验后有限使用|CSI300/CHINEXT缺，XLF隔离；STOXX从2007；DAXperformance；指数非可交易|
|Nasdaq issuer-authored release republished by MondoVisione|QQQ2000 ordinary2:1 action unit proof|US|effective2000-03-20，原作者说明firstyear|event|只admin单位证明，不当T时news predictor|当前镜像/重新托管，非当年byte见证|不解决全市场survivorship|免费完整正文+SHA|作者是一手issuer、托管是republication，双重边界说明|只解决普通action资格，不放行XLFspinoff，不创造历史经营数据|

代码、源清单与正式准入锁先于新标签。FRED今日修订历史未因网络可用就突然准入；旧其他数据缺口保留。
