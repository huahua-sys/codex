# Phase4 阅读与复现入口

建议先读五份：

1. PHASE4_MARKET_ECOLOGY_REPORT.md — 115记录、结果与15个回答。
2. HUMAN_DECISION_ARCHITECTURE.md — 人类问题树、WAIT/退出边界。
3. MARGINAL_PLAYER_MAP_US.md — 美国边际玩家与约束。
4. MARGINAL_PLAYER_MAP_CHINA.md — 中国边际玩家与约束。
5. MARGINAL_PLAYER_MAP_JAPAN.md — 日本边际玩家与约束。

详细事件在BEHAVIORAL_EVENT_LIBRARY/INDEX.md；每例A原证据与B未来价格分开。
JSON原卡在research/behavioral_events与research/evidence_cards；锁/标签/统计在research/phase4。
原文件与source bytes全仓库保留；核心ZIP只省略较大的原始下载文件，不省略核心文档/事件/代码/标签/统计/原源索引与失败记录。

## 研究结论

NO ROBUST BEHAVIORAL PROBABILITY EDGE ESTABLISHED。115 raw不是独立N，67parent、114公开日、18年；71已观察行动不等于71笔股票净流。新增概率0、可操作原则0、已验证原则0；旧失败择时不重跑。

## 复现（在完整既有项目根目录）

依赖：Python、numpy；官方PDF检验还需pdftotext。不要覆盖旧结果。

- `python3 scripts/phase4_event_study.py check`：6个合成工程守卫，无投资结论。
- `python3 scripts/phase4_independent_qa.py --help`：独立审计参数。
- `phase4_collect_events.py` 读取已有原source和地区卡，不读价格；写一次全事件锁。
- `phase4_event_study.py reveal/summarize` 仅新Phase4描述性事件统计，不改Phase3；已有输出会拒绝覆盖。
- `phase4_render_events.py` 生成原卡/结果分层的人类dossier；不要用于改冻结A。
- 三地区获取/解析代码在research/phase4/regional/。source URL与SHA在各SOURCE_MANIFEST/ledger；今天再次下载若SHA不同须新版本，不能替换冻结证据。

报价依赖旧 `research/phase3/data/market/{SPY,SSE,N225,TLT}.canonical.json`。核心包按SHA引用这些旧源，不重复放入大型旧研究数据；完整Git仓库包含原源。价格为今天供应商重构，非独立原历史quote vintage，且当前计算是PRICE_ONLY、不含分红/FX，不可宣称总回报或alpha。

## 必须保留的更正

US全115锁/统计仍指v001；US events.v002与ERRATA只是post-global-reveal文字范围更正。日本8scope键导致的QA v002错误FAIL与v003修正均保留。框架FW21旧日期hint更正保留v001/v002。源目录失败、PIT未知和对照未成熟不能删除。

## 交付

CORE_EXPORT_MANIFEST.json定义核心包每个文件hash（不含manifest自身）。原始大官方PDF/HTML的完整bytes在Git仓库research/phase4/sources，核心包内有SOURCE_FILE_INDEX及source excerpt供查看。核心ZIP为本轮独立输出；原135MB InvestmentResearchLab.zip未修改或重新压缩。


## Phase4 最终验包 checkpoint — 2026-10-10T08:27:11.526769+00:00

独立QA v005 PASS（67,415检查）；收据 `research/phase4/audit/INDEPENDENT_PHASE4_QA.v005.json`。核心ZIP 9,007,829 bytes，SHA256 `bdef7229e0c67ad0323c640c2776d4fce49df94c4d829d030a3a8b7eb7eec942`，909个manifest文件的SHA/大小与完整ZIP CRC通过。v004的唯一FAIL是QA代码只识别EXPORT_MANIFEST.json、未识别实际CORE_EXPORT_MANIFEST.json；原失败保留，v005修正验证适配并核对全部manifest，不改ZIP或研究结果。

核心包是最终QA前的冻结快照；其中metadata的PENDING_CORE_PACKAGE指该时点。最终收据在核心包之外、完整仓库内，避免验包文件引用自身的哈希循环。本次仅更新研究状态/交付metadata，原预测、收益、统计与操作规则不变。GitHub同步及用户下载是否成功另行确认；本地验包通过不代表用户收到。
