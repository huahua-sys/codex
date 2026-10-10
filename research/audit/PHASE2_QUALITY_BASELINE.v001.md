# Phase2 来源和冻结状态独立核验

状态：`PASS_WITH_SCIENTIFIC_LIMITATIONS`。这是既有样本的read-only复核；未重跑Stage A、未修改预测、规则、旧锁或原始来源。

| cohort | design/锁工件 | 有效预测 | 不足历史 | 成熟12m | 12m待成熟 |
|---|---:|---:|---:|---:|---:|
| NIGHT_ASHARE | 42 | 14 | 28 | 14 | 0 |
| NIGHT_CALENDAR_CONTROL | 60 | 60 | 0 | 60 | 0 |
| NIGHT_EARLY | 22 | 20 | 2 | 20 | 0 |
| NIGHT_RECENT | 18 | 15 | 3 | 12 | 3 |
| NIGHT_SECTOR_V002 | 160 | 140 | 20 | 140 | 0 |
| NIGHT_XASSET | 68 | 68 | 0 | 68 | 0 |
| NIGHT_XTIME_V003 | 36 | 36 | 0 | 36 | 0 |
| ROUND_002_V003 | 24 | 24 | 0 | 24 | 0 |
| 合计 | 430 | 377 | 53 | 374 | 3 |

全部430行的selection、preregistration、input manifest、input、prediction JSON/Markdown、单例lock和标签引用哈希一致；五个冻结engine文件哈希一致。所有输入再次通过原schema/PIT门控，metadata只包含白名单，filter_audit只含T前保留价格行数。不存在将未来context数量带入新版输入的旧漏洞。53不足历史行只有锁定工件，没有有效预测；不能把430称为430次有效Historical Replay。

原15份CP和15份EXP共30文件与ROUND_002_PRIOR_STATE哈希完全一致。四批120行metadata泄漏pilot全部留档，无标签或Stage B summary，永久排除。旧verify_artifacts.py是ROUND_001快照工具，未用作当前验收。

43个共享cutoff日期、23个日历年；真实独立N保持null。跨市场/行业共享冲击、March与September及跨年12m/24m结果重叠，标签数不能当作独立下注数。日期/年分组重抽样只提供描述性敏感性；序列相关、样本自适应扩充和固定幸存代理池仍限制外推。

历史OHLC和公司行动来自今天供应商的历史重构，有保守session availability；并非T时vendor archive。逻辑读取门控不能消除模型或研究者已知历史结局。native index仅价格回报、不可直接交易；local currency标签算术均值也不是执行组合CAGR。

原replay的0%现金是未观测假设。BIL仅作为USD短国债ETF代理，必须匹配币种/日期/收益口径/成本，不能直接移植到HKD、JPY或CNY案例。

SEC pilot另有独立核验：[SEC_PILOT_PIT_REVIEW_INDEPENDENT.v001.md](SEC_PILOT_PIT_REVIEW_INDEPENDENT.v001.md)。八条原始财务fact达到窄范围数据门槛，不增加投资检验样本，不证明任何金融规律。

本核验没有把PIT过滤通过等同于发现投资优势。新增Phase2条件表、分类、residual、placebo及报告的科学核验将另存版本。机器审计见[PHASE2_QUALITY_BASELINE.v001.json](PHASE2_QUALITY_BASELINE.v001.json)。
