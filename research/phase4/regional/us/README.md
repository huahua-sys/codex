# Phase 4 美国原源与复核

先读根目录`MARKET_ECOLOGY_US.md`和`MARGINAL_PLAYER_MAP_US.md`，再看events、原excerpt与正式publication-date proof。数据不是净资金数据库；29条报告已发生的行动、12条规则变更、1条提案。42记录、42日期、14年、23parent；独立N未知。五族按冻结source universe/分类/equisequence规则选，未依据未来价格。

1. `acquisition_design.v001.json`固定官方目录、2008–2025年、标题/route识别及公司端点；`catalogs.v001.json`保留候选与覆盖缺口；`selected_source_slots.v001.json`固定取样。银行额外`bank_catalog.v001.json`固定72份regular报告抽10。
2. `events.json`/`events.lock.v001.json`是Root全市场v001用到的原42记录。原字节和收益结果不能替换。日期、已知/未知、金额scope、原来源SHA可逐项核验。
3. `events.v002.json`/lock及`ERRATA.v001.md`只是揭晓后source文字scope旁注，修正跨年模板对2009的表述；日期/金额/selection/分类均守恒。不能把该版本称新独立证据或重新计收益。
4. 原字节在`research/phase4/sources/us/`，每个`.source.json`列URL、SHA、内容类型、获取时间、revision risk；PDF可能按通用fetch的`.html`名保存，但以Content-Type和字节magic识别，SHA不变。未来重新下载如果SHA不同，不覆盖原字节，不当作原vintage。
5. `participants.v001.json`含22类×20约束字段；`institutional_references.v004.json`将当前制度/2025报告与历史事件来源区分，不能把后来的监管调查/FSR解释回填早年的KNOWN_AT_T。

复核：

```bash
python research/phase4/regional/us/qa_us_sources.py
```

这只检查源字节、锁、schema和v002守恒，不获取/重算任何价格，不将原研究重复运行。最后一次源QA见`qa.v002.json`。`acquire_us_sources.py`和`build_us_events.py`保留完整构建代码，但有冻结目录时拒绝重跑覆盖；新增取样须新协议/新输出版本。

覆盖缺口：2008 MSFT端点404，未替换；SEC first filtered page及3个旧slug route未normalize，见`catalog_route_gaps.v001.json`，旧目录字节保留，未在揭晓后补入；DOL/部分旧SEC/ICI参考页403/404也在source metadata保留。单发行人/现存档案/国内SLOOS构成与机制类别不能做跨市场因果证明。尚缺真实point-in-time基金赎回、AP篮子交割、forced collateral calls、养老金责任负债、以及同issuer资产偿付/市场预期的联立资料。

Source SHA证明今天保存的字节不再变，不证明当年独立archive snapshot。现存原官方文档的发布时间已校验；possible silent site correction继续保留。只用日期的发布按当地23:59:59；下一首次有效交易日open才是Root预定入场，不含披露当日gap。SPY/TLT只是广资产描述反应，不能隔离MSFT回购alpha或holder-only错价。
