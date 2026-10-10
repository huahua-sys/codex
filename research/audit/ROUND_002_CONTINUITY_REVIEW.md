# ROUND_002 连续性与 PIT 独立复核

复核日期：2026-10-08 UTC。初始状态：`CONTINUITY_REVIEW_COMPLETE / EXECUTION_REVIEW_PENDING`。

## 已读取的既有研究

完整核读 ROUND_001 **64 个有实质内容的文件**：17 个根 / 状态入口、首轮案例方案和阻塞记录、5 个协议、4 个模板、15 个 CP、15 个 EXP、3 个审计资料、来源 manifest、主提示词保存副本及初始化验收脚本。另 5 个零字节 `.gitkeep` 只是占位，不是研究文件或历史证据。根入口中的 JSON 与索引均按首轮零实证状态理解，未以“没有反例”推断正确。

本复核者在 Stage A 锁定前没有读取 ROUND_002 新下载的未来价格数据，没有计算 outcome，也没有编写依赖未来结果的历史故事。执行代码、冻结协议与输入 / 锁定元数据可以读取；标签须在锁定后才进入评分复核。

## 连续性结论

| 事项 | 结论 |
|---|---|
| 上轮完成范围 | 审计、协议、长期档案、15 个理论 CP 和 15 个未运行 EXP；0 真实 replay、0 已锁预测、0 验证原则 |
| 本轮授权 | 最新用户明确要求测试公开来源、下载 / 导入小型真实数据集并执行案例；覆盖上轮“仅已有资料 / 不联网 / 首轮停止”边界，无须再次索取同一授权 |
| 不重复初始化 | 保留原协议、CP、EXP、审计与来源；本轮新增数据和具体执行，不重复创建初始框架 |
| 出处保留 | CP-001—CP-015 原始 `MASTER_PROMPT_DERIVED_UNTESTED` 不能改为本轮发现；未检验的 CP / EXP 仍未检验 |
| 新候选上限 | 本轮新候选最多 10 条，置信度只能 D / C；历史档案的 15 条不应删除以满足新上限 |
| 正式原则 | 继续为 0；治理改善、代码通过、历史方向命中均不是原则晋升证据 |
| 行业报告 | [INDUSTRY_SIGNAL_DIFFERENCES.md](../../INDUSTRY_SIGNAL_DIFFERENCES.md) 只给 prior economic mechanisms 和字段门槛；宽基案例不构成跨行业检验 |

## 执行前必须披露的局限

1. **历史遮蔽不能证明真正不知道未来。** LLM 训练记忆不可删除；日期 / 资产匿名化与文件过滤只约束新输入。固定规则本身也来自今天的研究设计，不能宣称在历史 T 已预登记。采用 `MASKED_HISTORICAL_REPLAY`，说明 `SEPARATION_LOGICAL_ONLY`；事后锁定时间不得写成历史时点。
2. **历史记录日期不等于原始发布时间 / 版本证据。** 当前价格档案可能修正历史错误；收盘已公开是合理的市场观察时点，不能据此证明当前数值就是当时原始快照。须区分“价格观测可用时间规则”和“原始报价版本未被修订”的证据，并保留 `POINT_IN_TIME_UNCERTAIN` / reconstruction 限制。未证实的宏观 vintage 或发布日期字段必须排除 Stage A。
3. **价格指数不是可交易净总回报。** 不含分红的指数点位变化只能报告本币 gross price return。实际投资工具、股息、FX、费用、执行价与现金收益缺失时，不宣称可实现 EV、净超额回报或 WAIT 的现金收益优势。收益率变化不能代替债券回报。
4. **固定宽基样本范围很窄。** 只研究若干存续的大型指数，不回填当前成分；但仍不能称无幸存者偏差或代表全市场。研究范围不支持个股、退市、行业或全部中国市场推断。
5. **概率是未校准设计先验。** 宽区间或简单规则不提供历史统计依据；预测必须声明 prior 来源、事件和计分值。校准只在已锁样本上描述，不能因小样本高命中就给“70% 可靠”等结论。
6. **多期 / 跨市场并非独立观察。** 同一截止年份的市场相关、多个 horizon 重复使用同一价格路径；年度 cutoff 的 24 月标签还互相重叠。预测条数不能当独立样本数。不给没有足够独立簇的显著性结论。
7. **中性选样不保证类别配额。** 日历规则能减少事后手挑，不能事先保证危机 / 产业泡沫 / 政策成功失败等全部出现。应如实记录结果覆盖与无法判定类别；不能读标签后增补经典案例来补齐配额。
8. **没有故事记录不等于没有故事。** 可靠新闻 / 情绪 / 估值 / 预期缺失时只能 `DATA_REQUIRED`；不能贴“无明显故事赢家”“政策失败”或 forced selling 标签。后来的宏观 / 新闻资料若使用，仅作为 `KNOWN_ONLY_AFTER_T`；不得成为事前理由。

## 待执行复核清单

待冻结协议、具体 schema 与引擎完成后复核：来源分层、uncertain 严格排除、所有 cutoff 过滤、当时版本选择、价格特征只读 T 前、未知字段不补值、事件 / 概率定义、锁定后不可覆盖、全体锁定后标签读取、时间 / 哈希链、entry / horizon 对齐、MAE / MFE / calibration 公式、普通 / 失败案例保留、结果与叙事边界。

此时未作执行 PASS；本文件后续追加执行复核，引用实际文件、结果及未解风险。文件一致性 PASS 只能证明限定范围的检查，不能证明投资有效性或真实认知盲性。

## 追加：Stage A 前的引擎复核

状态：`PRELOCK_ENGINEERING_QA_PASS`。此复核在真实标签揭晓前完成；尚未审计真实价格覆盖或生成任何市场结论。

独立重新运行 `python -m unittest discover -s tests -v`，仓库 [13 个工程测试](../../tests/test_round_002.py) 全部通过。实现者的独立执行证据见 [ENGINEERING_VERIFICATION.v003.json](../engineering/ROUND_002/ENGINEERING_VERIFICATION.v003.json)，旧 v001 / v002 保留。另一个只读复核者用 synthetic fixtures 复核 13 项金融计算、8 项拒绝门槛、2 项报告 / 状态检查，全部通过；没有读取真实市场数据或未来标签。

复核过程中发现并在正式锁定前修复：

- 强制非价格 context 的 `published_at <= available_at <= T` 和时间证据；不能用伪造 availability 将未来公告放入事前输入。
- 强制完整 OHLC 在真实带时区 session close 后才可用；执行必须有真实 session open，不以 UTC 零点替代。
- 隔离 uncertain 字段；拒绝未来复权输入与不一致标签基准，显式保留当前报价 / 公司行动 reconstruction 的原始 vintage 限制。
- context 按发布时间 / 可用时间取最近记录；指数事前证据按价格回报表述，不能称总回报。
- 验证公司行动来源、资产、重复事件与有限正 split ratio；同日先处理拆股，再处理现金股息。
- Stage A 输入审计只传未来 context 的拒绝数量，不传可含事件信息的未来 record ID；应用层读 guard 拒绝原始数据、标签、复盘与评分摘要。
- 锁定判断包含规则内容 / 哈希和 schema、replay、evaluator、selector、runner 的实现哈希；Stage B 在打开标签包前核对所有锁定。
- 预先保存固定 0.5 / 0.6 概率基线；成熟度、未成熟空值、概率计分分母、方向 abstention 和情景 Brier 分别记录。

独立 synthetic 脚本当时位于 `/tmp/synthetic_engine_qa.py`，SHA-256 为 `f5c9047d29628e721be312dd09d4b35d0884ae7956de3bb121183cd460be23cd`；它只验证工程，不能用于形成投资原则。可持续重跑的关键拒绝门槛已覆盖在仓库测试中。

剩余的可计算边界：daily OHLC 不能确定日内高低发生顺序，因此最大回撤使用收盘路径并标明；股息使用 ex-date 权利在 ex-date close 再投资的经济总回报约定，并非到账日可执行交易。通过测试不证明供应商历史记录完整、不证明原始 vintage、也不证明模型认知盲性。

## 追加：官方原始发布记录独立复核

`OFFICIAL_RELEASE_METADATA_QA_PASS`：只读检查 [16 条记录](../../data/raw/round_002/official/release_records.json)、[官方来源 manifest](../../data/manifests/ROUND_002_OFFICIAL_SOURCES.json)、16 份原 HTML 与提取正文。每年 2016—2023 的九月 FOMC 声明和八月 CPI 首次发布各一份。发布日期及明确时刻均能回到原 HTML，使用 `America/New_York` 转换后，FOMC 为 18:00 UTC、CPI 为 12:30 UTC；全部在各年九月 30 日 cutoff 之前。CPI 的八月 reference period / 月末没有冒充九月实际发布日期。

检查了 16 份原始 HTML SHA、数值证据在原文及提取正文中的位置、`value == fields`，无不一致。利率范围、CPI headline YoY / seasonally adjusted MoM / core YoY 保留原发布值及证据，而不是今天的修订时间序列。记录 SHA 为 `c4cb850b6b2450015303cfe0350c2e811315bd6eaa3b2da06c43d595ab35ae93`；manifest SHA 为 `a316308cd5fa95309c9547762783372d6d7af90bcdfb25ce6465bf42395d9b5b`。

此 PASS 仅证明当前官方历史 release 页面内部证据一致；它不是 immutable Wayback 快照认证，也不能证明网站从未修订。原文提取排除今天导航。US 官方背景不替代 HK / JP 本地政策、信用、估值或盈利数据。FOMC 在输入中的 Policy 与 Rates 是同一个 release 的两个视图，不能当两条独立信息证据。

## 追加：v001 首次实际输入复核与停止揭晓

状态：`PIT_METADATA_LEAK_PILOT_INVALID`。24 个输入的 prices / actions / context 数据行均通过 `available_at <= T`、schema 和出处检查；selection / design / preregistration / protocol / code / input / prediction / markdown / lock 哈希全部一致。24 个锁的本地时间范围为 2026-10-08 16:12:08.833411—16:12:09.770894 UTC。检查没有读取 admin bundle 或未来标签。

但完整 canonical 的 `metadata` 被原样复制进 Stage A，泄露 `last_date=2026-10-07`、全区间 `row_count` / dividend / split 数量、含 T 后日期的 `rejected_rows` 与完整下载区间。固定数值规则没有使用这些字段，但输入整体不能称 `KNOWN_AT_T_ONLY`。此问题在 Stage B 前发现，要求保持 v001 原件并标记无效；不能覆盖已锁判断。修复使用相同日期、同一规则 / 参数，生成另一个清理 metadata 的批次再锁定，并单独复核。工程测试 PASS 没有覆盖这项真实数据集 metadata 泄漏。

待新批次复核通过后才可开启 Stage B；v001 不进入投资结论与评分分母。

## 追加：v002 拒绝计数与 v003 实际准入

v002 已移除完整行情 metadata，但 `filter_audit.excluded_context_reason_counts` 仍向 Stage A 传入 T 后 context 数量，例如 2016 SPY 为 21、跨时段控制 SPY 为 24。它没有传入未来收益或公告内容、没有影响固定规则，但本轮要求输入只暴露 T 前资料，因此拒绝数量也移到管理审计侧，原 v002 锁保留且不揭晓、不评分。纯出处的当前 source SHA / ingestion timestamp 和明确的报价 vintage 局限不作为投资特征；它们用于审计当前数据的来源，不是当时投资证据。

`ACTUAL_INPUT_CUTOFF_AND_LOCK_QA_PASS`：只读复核 [ROUND_002_V003](../replays/ROUND_002_V003/selection.v001.json) 的 24 行、8 日期簇，以及 [NIGHT_XTIME_V003](../replays/NIGHT_XTIME_V003/selection.v001.json) 的 36 行、12 日期簇。metadata 限制为 6 个静态 basis / quality / tradability / observability 字段，没有全区间数值、未来日期、未来拒绝计数。全部价格 / 行动 / context 行在 cutoff 前可用，context 逐字段与官方记录吻合。设计、协议、抽样、预登记、代码、规则、输入、预测 JSON / Markdown、外置锁和 all-lock sentinel 哈希均一致。复核没有打开 admin bundle、未来价格或 Stage B。

|批次|本地锁定时间范围 UTC|all_locks SHA-256|
|---|---|---|
|ROUND_002_V003|2026-10-08 16:17:06.355054—16:17:07.295056|`8653e8b30252e26672e573bd0f8058c67aac32bfd7106ec68d1406fe615b55af`|
|NIGHT_XTIME_V003|2026-10-08 16:17:09.417889—16:17:10.175244|`6a92f755b3facddbea77116605cc926d170cafdc07f13399dd2dc536f3411f08`|

这两批准入 Stage B。跨时段批次沿用同一先验规则，2005—2015 及 2024 年固定九月起点，称 computational holdout 而非真实前瞻认知盲测。与探索批次分开评分；年度 24 月标签在跨批边界也可能重叠。此准入仅证明被检查文件的 cutoff 与锁一致，保留所有原始报价 vintage / 原始发布页面可修订 / 同团队管理员 / 今日规则设计限制。

新行业、跨资产和 A 股批次另行审计，尚不能沿用本项 PASS。

## 追加：三个扩展批次 Stage A 准入

下列实际输入独立通过同样的 cutoff、metadata、context 原始字段、schema、代码 / 规则及全部锁定哈希检查；复核未读取未来价格或 outcome。规则与前两批完全一致，不是按新资产另拟参数。未解决的数据行仍锁定并标记 `INSUFFICIENT_HISTORY`，不得作为有效预测进入评分分母。

|批次|预选格点 / 有足够事前特征|日期簇|本地锁定时间范围 UTC|all_locks SHA-256|
|---|---|---|---|---|
|NIGHT_SECTOR_V002|160 / 140；20 行 XLF 未解决|20|2026-10-08 16:18:56.027237—16:19:00.853011|`aae1d62cda0403493bde0433626a8fcf72c5440110e4a0ea1e29ab7d43a62612`|
|NIGHT_XASSET|68 / 68|17|2026-10-08 16:19:05.321004—16:19:07.472058|`87e7a9cf1d47c6c1c9313e9296176c64524334ecaa8da092fe6b462fd3b031a8`|
|NIGHT_ASHARE|42 / 14；CSI300 / CHINEXT 共 28 行未解决|14|2026-10-08 16:19:08.096294—16:19:08.376750|`264042a0b54d5f519287ebebc7788c200f261084fdfcc5927f124ecca537b667`|

原 `NIGHT_SECTOR` 只有失败的管理导入，没有完成全 A 锁定；不计为执行批次。这三批通过准入，仍不是认知盲性或原始报价 vintage 认证。五批共 330 个预选格点、282 行有足够事前特征，不是 330 次独立实验；成熟 outcome 数还须由 Stage B 判定。

行业新增覆盖只有七个 ETF 代理的同一趋势规则：XLK、SOXX、XLE、XLI、XLY、XLV、XLU。XLV 不是纯医药、XLY 不是全部消费、XLE 不是全部资源；缺历史 holdings / mandate 审计，不能认为 ETF 产业组成从 2005 年起不变。金融 XLF 无实证。CapEx、盈利修正、订单、政策落实等产业机制仍未检验。

## 追加：前五批锁后评分与旧文件保留复核

`FIRST_FIVE_BATCHES_POST_REVEAL_INTEGRITY_QA_PASS`：在获准并完成 Stage B 后，复核 330 格点的判断仍与原锁一致、label 绑定 prediction / lock SHA、已揭晓时间不早于各批最后一个 A 锁。逐成熟标签核对 `actual_up == (net_return > 0)` 和二元 Brier 公式；未解决行不当零收益。12m 成熟分母分别为 24 / 36 / 140 / 68 / 14，共 282。NIGHT_XTIME 的 2 行和 A 股的 1 行还有次要期限 pending，不能误称所有六期限都揭晓。

五批的 12m mean Brier 分别为 0.25375 / 0.22750 / 0.231857 / 0.235735 / 0.23500，各自恒定 0.60 基线为 0.218333 / 0.221111 / 0.204286 / 0.233529 / 0.231429。全部在此主终点比该固定先验更差。这是针对当前冻结规则、概率设定和取样范围的反证，不是“所有趋势都无效”的普遍命题；避开部分下行与漏掉上涨同时发生，不能只选其中一项宣传。行业文件追加了七个代理的真实描述，不据此晋升经济机制。

使用 [08:23 捕获的原状态](ROUND_002_PRIOR_STATE.json) 验证 **15 个旧 CP 和 15 个旧 EXP 的当前 SHA 均保持不变**，14 个根 / 状态旧版归档 SHA 也一致。旧15个假设没有因本轮趋势试验被标为已检验。

分析器的独立 synthetic 检查先为 7 项 PASS，后补充同一 rule ID 必须拥有相同 frozen rule 内容 / SHA 的门槛，以及 nearest reference 的未来日期标记；修改仅限分析器，没有触碰已锁核心代码。更新后自行运行 `python scripts/analyze_night_research.py --self-test`，10 项 PASS。这些仍是工程验证，不计为投资案例。nearest comparison 只作锁后探索，可能包含目标 T 之后的参考 episode，不是当时可用类比库，更不能回写 A。

## 追加：第三次反证批次准入

`THIRD_CYCLE_INPUT_CUTOFF_AND_LOCK_QA_PASS`：以下三个新批次同规则 / 同参数、完整格点预选、全部 A 锁后才获准开启 B。独立核对 T 前行、六字段 metadata、无未来拒绝计数、context 原始字段、schema 及全部出处 / 预测 / 代码 / 锁哈希；准入时未读取这三批未来价格或 outcome。

|批次|预选格点 / 日期簇|本地 A 锁时间范围 UTC|all_locks SHA-256|
|---|---|---|---|
|NIGHT_EARLY|22 / 2；2003—2004 年九月|2026-10-08 16:24:37.138572—16:24:37.257852|`055caa42bba7a9fbdbfe689aa4fa9b9048ea6cec665a236dd5c2eecdbafecdb9`|
|NIGHT_RECENT|18 / 1；2025 年九月|2026-10-08 16:24:41.513243—16:24:42.368088|`4baaf5f14a0fec55bafef3a852cc487d57a4e0b63bac6802eb17e7723ede4a27`|
|NIGHT_CALENDAR_CONTROL|60 / 20；2005—2024 年三月|2026-10-08 16:24:46.015158—16:24:47.625524|`07dae04ebb56d6a3a52f489ef460c77d2a704f07bfe5ae82711ade5c7e76c911`|

这些扩展设计于早先标签揭晓后，只能称新的 computational holdout / exploratory falsification；锁前未读取自身标签不等于研究团队从未知道相关历史。官方背景来源只覆盖 2016—2023，“最新”仅是所提供记录中的最新；2024 / 2025 的真实最新宏观 / 政策仍缺失。三月与九月 12m 标签大量重叠；新增 cutoff 日期数不能等量增加独立样本。合并报告需要 year clusters 与 overlap caveat，日期 bootstrap 的区间不能当已解决依赖。

锁后追加：三个新批次的原预测 SHA、label 绑定、揭晓时刻与二元 Brier 公式全部 PASS。EARLY 的 22 格中 20 行有事前特征且 12m 成熟、2 行未解决；RECENT 的 18 格中 15 行有事前特征、12 行 12m 成熟，15 行为部分揭晓、3 行未解决；CALENDAR 的 60 行全部 12m 成熟。三个新批次 12m Brier / 恒定 0.60 为 `0.217 / 0.170`、`0.2175 / 0.210`、`0.254 / 0.223333`。

截至这八个批次共 **430 预选格点、377 行有足够事前特征、374 个成熟 12m 标签、53 行未解决**；有特征但 12m 未成熟的 3 行不能当失败、零回报或方向错误。全部八个批次主终点均比固定 0.60 更差，但范围共享时点 / 市场 / 价格路径，不是八次独立确认，也不证明任何普遍反趋势规律。当前仍为 `NO ROBUST PATTERN YET`。

## 追加：现金与每周卖出机制的工程复核

独立检查 [analyze_cash_and_sell.py](../../scripts/analyze_cash_and_sell.py)，不读取真实 SPY / BIL 数据、预登记或结果。内置 12 个 synthetic 检查和额外 5 个 synthetic 检查全部 PASS：相同执行 open / 不匹配拒绝、Friday 完整 close 直到 Saturday 才准入、未来价格和行动不改变已知 signal、买卖及每次切换全部 leg 费用、ex-date 前持有者卖出后仍保留应收股息、新买入不享当日除息分配、BIL reverse split `0.5` 财富中性、退出 open 应收计入终值、50/50 的回撤从逐日组合财富重新算。

脚本必须先核对独立 preregistration / code hash 和 completed Stage B witness 才可打开真实市场文件；该工程准入不等于现金 / 卖出规律成立。此新 cycle 属回顾性 walk-forward mechanics，与原 24 个不可改预测及零现金假设评分分开。BIL 是短国债 ETF，不是无风险现金；ex-date 应收再投资是经济约定，未核验实际支付日可用现金 / 交易。额外工程 fixture 位于 `/tmp/cash_sell_synthetic_qa.py`，没有真实案例支持含义。
