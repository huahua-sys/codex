# Phase3开始前的独立完整性与既有暴露审计

本审计只读已有旧资料，没有访问任何新增历史标签，未改旧判断、旧结果、旧锁、原15CP或15EXP。全量内容基线见 `PRIOR_STATE.v001.json`；锁见同名外置lock。操作字段补充见 `PRIOR_OPERATIVE_FRAMEWORK.v001.json`。

## RAW OBSERVATIONS

全量基线覆盖 3,366 份文件 / 1,868,449,815 字节；包括旧输入、Stage A、Stage B、锁、预登记、抽样、行政bundle、分析、原始报价、源资料、原15CP/15EXP、lab及旧scripts。根目录永久记忆单独保存可变基线哈希，不要求Phase3停止更新它们。

有效旧批次430选择记录 / 377预测 / 374成熟12m；Phase2用户关注的原五批为282成熟12m，不能把282等同于全项目。

|历史段|旧选择记录|旧有效预测|旧成熟12m|
|---|---:|---:|---:|
|2000–2015|223|200|200|
|2016–2023|168|144|144|
|2024–2025|39|33|30|

2003/2004旧起点为9月30日；2005–2024已经使用每年3月31日和9月30日（行业等主要为9月）；2025使用9月30日。原选择日期未必当日为交易日，Phase3改为季末有效交易日会产生新决策定义，但不是自动产生未接触历史世界。全量asset×cutoff登记以及已揭晓的入/退场日期窗口保存在JSON中。

## EFFECTIVE SAMPLE ASSESSMENT

旧样本43截止日期、23年份簇；有效独立N未知。同期美国行业、跨市场全球冲击、12/24m重叠与已经归档的连续价格路径均限制独立性。按日期或年份簇处理可以避免部分伪重复，不能制造新独立世界。

## 可接受的验证隔离命名

- 2016–2023：`PREVIOUSLY_EXPOSED_DISCOVERY_DEVELOPMENT`。
- 2000–2015：`PREREGISTERED_CROSS_TIME_RECONSTRUCTION`；必须区分200已揭晓旧预测与新季度决策，不得统一宣称未接触external OOS。
- 2024–2025：`PREVIOUSLY_EXPOSED_LATE_PERIOD_RECONSTRUCTION`，已有30成熟12m及全价格路径；禁止当作全新holdout。
- 既有原始数据上的新增季度日期：`NEW_DECISION_POINTS_WITH_PRIOR_PATH_EXPOSURE`。
- 规则与协议锁定后才获取的新历史市场：可标`COMPUTATIONAL_HOLDOUT_RECONSTRUCTION_NOT_PROSPECTIVE`，但保留模型知识与市场选择限制。
- 冻结之后真实作出的未来决策及尚未发生的结果：`LIVE_FORWARD_PREREGISTERED_DECISIONS`；这是建立真正前瞻OOS的路径。

哈希证明现有内容保留，不证明真正历史盲性、可信外部时间戳或原始数据vintage。所有旧价格仍为今天供应商重建资料，现金股息未逐笔交叉核对，XLF与A股不可用历史继续按原原因隔离，不因扩样目标解除。
