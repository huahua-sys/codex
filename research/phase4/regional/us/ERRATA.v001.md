# US Phase4 追加文字范围更正（v002 documentary overlay）

原`events.json`及`events.lock.v001.json`保留，SHA未变。Root已锁全市场v001并揭晓结果，因此**不得用US events.v002替换全市场v001，不重跑结果，不修改预测或收益**。v002只是可读事实旁注；日期、金额、选样、action_type、action_status和任何结果均守恒。

独立source QA发现：9个公司记录的模板observed_action全部带了“2009原文另明确该季度无常规回购”，这是跨年注释，容易误读成每年均无回购。现追加v002把该句只限定到2009原源事件US-P4-010。所有公司记录均明确cash-flow row不能识别公开市场回购执行量。

2009原文：`While we did not repurchase any shares during the three months ended June 30, 2009, we repurchased 318 million shares during the first nine months of fiscal year 2009.` 同页现金流表`Common stock repurchased`本季度为$(22) million。这两类口径不能混为同一普通公开市场买盘。原事件已说明可能包括股票税款代扣；本轮没有独立识别2200万美元的执行分类。v002不把该金额置零，也不把它重新判为看涨/forcedflow。

`events.lock.v002.json`的`price_outcome_accessed_before_lock=false`仅说明美国来源采集agent未读未来价格。Root已在v002之前揭晓全市场结果，因此v002不能叫全团队的pre-reveal新样本锁。应按**post-global-reveal source-wording QA correction**解释，并连同原v001及其哈希使用。该更正不构成新的投资证据。

复核方式：`python research/phase4/regional/us/qa_us_sources.py`，检查v001/v002 SHA、关键日期金额和选择字段守恒。对照统计仍只使用Root全市场v001冻结字节。
