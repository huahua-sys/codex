# Phase3 前瞻留存 — 当前应运行 v002

截至2026-10-09：RAW OBSERVATIONS=0；真实capture=0；真实锁定决策=0；概率预测=0；成熟未来标签=0。EFFECTIVE SAMPLE ASSESSMENT：完成月度簇0，独立N不可估计。24个月×7资产=168个计划槽位，不是168个实验。每月12/24个月收益重叠，多个资产共享全球冲击。

7个固定对象为SPY、SSE、HSI、N225、STOXX50E、GLD、BIL；2026-10至2028-09共24个月，第一计划锚点2026-10-30。v002只更正未启用v001的工程语义，父代码、登记、历史结果和所有锁均保留；更正原因见[CORRECTION.md](CORRECTION.md)。当前9个操作性框架字段守恒，validated=[]、live=false。脚本记录NO_RESEARCH_TRADE、benchmark-only上下文，无下单、无新概率、无cron部署。

## 可运行命令

在项目根目录运行：

```bash
python3 scripts/phase3_forward_v002.py register
python3 scripts/phase3_forward_v002.py status
python3 scripts/phase3_forward_v002.py selftest
python3 scripts/phase3_forward_v002.py capture --month 2026-10
python3 scripts/phase3_forward_v002.py evaluate --month 2026-10
```

register已执行；重复调用只核验原锁。capture现在会拒绝；只有真实2026-10-30美国16:00正常收盘以后（夏令时20:00UTC；冬令时21:00UTC）至随后3个日历日内允许运行。月末是日程最后工作日，尚无完整交易所节假日/停牌日历；每市场月末会话是当月最后完整来源观察日。没有--now、--as-of或历史导入通道。capture会在联网与创建decision目录前拒绝提前/过期时间、未经登记月份、已尝试月份，且在联网前检查当前9框架字段仍与冻结基线一致。漏失月份不得后来补造LIVE。若框架变动、需要重试或修改资产/规则，须新追加版本。

真实抓取保存原HTTP字节、实际request/received/retained时点、响应Date/ETag等头和SHA；响应symbol必须匹配注册资产，尚未收盘或无效OHLC排除。cutoff是本次全部来源留存之后的真实机器UTC；available_at必须不晚于它。源中已完成的后月会话不进入月末特征，任何假设成交严格在真实cutoff之后下一个已观察开盘。延迟捕获明确ACTUAL_DELAYED_CAPTURE_NOT_BACKDATED。正常会话钟与本机时间不构成完整交易日历或外部可信时间见证。

## 与主面板一致的冻结语义

r252=wealth[-1]/wealth[-253]-1；vol252=最后252个simple daily known-action wealth return的样本标准差×sqrt252；drawdown252=wealth[-1]/max(wealth[-252:])-1；相对vol参考严格采用不含当前的252个此前252-return rolling估计中位数，需要505个prices，504时保留其他变量并保持relativevol=UNKNOWN。14项合成安全检查包含与已冻结主面板精确数值一致，以及253rd-old peak排除与505端点；synthetic仅工程测试，不是投资证据。

价格只用provider AS_REPORTED OHLC，AdjClose禁止。任何未核验split都隔离，不无证据放行ordinary split。ETF经济回报仍是provider-reported分红除息日再投资、固定50bp双边成本假设；无独立逐笔公司行动验证、付款日可执行分红策略或真实bid/ask。海外宽基为本币不可直接交易指数，local cash/FX/可交易代理缺失时超额保持UNKNOWN。估值、盈利修正、信用、资本周期等不得用价格涨幅或伪数据填补。

## 追加未来标签与基准

evaluate仅在真实锁定之后可运行，先验证原DECISION及sources的锁，再实际下载后续源，另建带评估时间的标签目录，不回写判断。5/21/63/126/252/504完整观察sessions未成熟为PENDING_HORIZON；更新标签不增加决策N。

BIL比较仅在资产与BIL均USD、双方REVEALED、positive integer sessions_held相等、entry/exit相等、完整ordered entry-through-exit日期列表及其SHA相等且有效时开放。只有首尾日期相同、内部日期不同，或缺hash/列表/有效n，一律UNKNOWN；不能声称IDENTICAL_SESSIONS。全部完整session列表也保存在标签中便于复核。没有投资组合或概率预测，因此benchmark收益不计主动决策收益、不计算不存在的Calibration。

## 已实际完成的工程校验

REGISTRATION.v002.json及REGISTRATION.lock.v002.json为新独立登记；ENGINEERING_SAFETY.v002.json及其lock记录14个synthetic检查与真实当前时点的提前capture拒绝。检查证明2026-10-09的10月capture未进入network、未创建decisions/2026-10。旧v001 code与旧registration完整核验不变。后续应调用本v002脚本，父v001仅保留审计，未启用。
