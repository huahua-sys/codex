# 预测与校准台账

截至 2026-10-08 UTC，真实预测 0；锁定预测 0；成熟可评分结果 0；校准实验 0。状态 `BLOCKED_DATA_REQUIRED`。没有真实资产、方向、概率区间、预期收益或实际结果；校准结论为 `INSUFFICIENT EVIDENCE`。

## 真实预测记录

暂无记录，禁止用占位案例或模板字段假装预测。真实记录需包含 Prediction ID、日期/T与时区、资产、horizon、可评分事件、方向、宽概率区间、预期收益范围、主要理由、kill condition、动作（含 `NO-TRADE / WAIT`）、源/预登记/判断哈希、锁定/揭晓时间、actual outcome 和 calibration result。

锁定之前无法获得未来结果；揭晓之后不修改原概率。单次命中不是校准，缺失不等于零收益，尚未成熟不等于失败。LLM 历史记忆污染与重复测试单列，不能计入独立确认成绩。

模板：[PREDICTION_TEMPLATE.md](research/templates/PREDICTION_TEMPLATE.md)。首轮状态：[ROUND_001_BLOCKED.md](research/replays/ROUND_001_BLOCKED.md)。
