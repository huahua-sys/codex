# Forward v002：只追加工程更正

2026-10-09。父版本 `scripts/phase3_forward.py` SHA256 `de3f6363514a1c1fd09f0e4b051e74c26d07757befe2fd73657f1834438d60b3`、父登记及所有结果不修改。父版本没有真实capture，保留为未启用工程beta。此版本仍是同7资产、2026-10至2028-09的24个月日程，168予定槽位不是168真实样本；当前capture、概率、成熟标签均为0，无cron、无下单。

独立QA识别三项真实工程差异：v001现金比较只检验首尾日期，却标记完整会话相同；v001 vol252使用log returns，主面板使用simple wealth returns；v001 drawdown峰值包含253点，主面板只取最后252点。v002使用完整ordered entry-through-exit session dates、SHA、正sessions数和同币种的fail-closed匹配；保持r252跨252收益期，波动改成252 simple wealth returns样本标准差；峰值只取wealth[-252:]；相对波动中位数严格取252个不含当前的先前252-return窗口，需要505prices，504prices保留其他特征且relativevol=UNKNOWN。

没有根据未来结果选择任何参数，也没有改历史抽样、旧A/B、主面板公式、冻结结果或9个操作性framework字段。capture前检查当前9字段与父框架一致，若改变须另建版本；当前仍NO_RESEARCH_TRADE、benchmark-only、概率null。拆股未核验时隔离，不给ordinary split无证据豁免；Yahoo分红与OHLC仍是provider-conditional当前快照，非完整独立公司行动核验。snapshot symbol必须匹配注册资产，actual source留存时间不得晚于真实decision。

所有工程检查只用synthetic数据，不形成投资证据。真实月份capture使用机器真实UTC；当前10月9日调用10月capture在network与decision目录写入之前拒绝。first appointment 2026-10-30美国16:00收盘以后，正常session钟、来源历史修订、外部可信时间见证不足等限制仍保留。此版本是后续应运行的版本；旧版本与锁作为证据保留。
