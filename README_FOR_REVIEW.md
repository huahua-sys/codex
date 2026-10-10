# 完整研究文件交付 — Phase3 + 上轮资料

本包是可继续工作的完整便携项目，不只是报告列表。包含本轮全部原来源、代码、schema、特征/标签/锁、统计JSON/CSV、失败与反例、273dossier、QA、checkpoint与永久记忆；上轮源/预测/282及扩展冻结结果保留。旧Phase2 ZIP另行原样交付，不覆盖。

人工先读PHASE3_RESEARCH_REPORT.md（15个回答）、PHASE3_SURVIVING_PRINCIPLES.md、SAMPLE_EXPANSION_PROTOCOL.md、EXPANDED_PANEL_REPORT.md、EFFECTIVE_SAMPLE_REPORT.md及CROSS_TIME_VALIDATION.md；再读4机制专题、MULTIPLE_TESTING_LEDGER、DEEP_EPISODE_LIBRARY_REPORT与research/status/LATEST.md。上轮审查入口README_PHASE2_FOR_REVIEW.md。

结果：2704规则格/2113有效feature/2087成熟12m/1995成熟24m，独立N未知。原SLOOS104表/85发布准入/19隔离。US相对波动关联经两后续反证cycle暂存，C/LEVEL2非操作，alpha/underreaction/经济机制未识别；LEVEL3原则0，CURRENT_FRAMEWORK9operative字段不变。273dossier中249价格、184价格+原信用且均缺基本面；不是273个已识别机制或新概率预测。

文件哈希和分阶段隔离不证明模型从未知道未来；报价为今天供应商重构，历史vintage未证，当前存续ETF选择、相关与重叠、跨币不可交易指数、历史费用等限制见报告。2024–25仅计算标签隔离，非真正future OOS。原120不合格pilot始终禁止评分。

重复输入的无损处理：565个原input/admin bundle合计约1.6GB重复报价已用DATA_RESTORE_BLUEPRINTS.json引用同一份旧canonical压缩。此包每个原文件SHA都能重构核验，不是删证据或改样本。解压进入包根目录运行：

```bash
python3 scripts/restore_export_inputs.py --verify-only
```

不联网、也不写大重复文件即可核验全部565原SHA。需要原A/B全部目录则运行 `python3 scripts/restore_export_inputs.py`；已有文件只核验不覆盖。研究默认审查不需恢复。旧冻结程序重跑只能验证原锁，不得改旧预测、调失败策略或覆盖报告。

未来执行用 `scripts/phase3_forward_v002.py`，原v001工程beta及锁保留。第一真实capture2026-10-30，目前真实capture/decisions/probability/outcomes0；7资产×24月份=168计划，不是实验，未部署cron。新v002修正简单收益波动、252峰值端点与完整持有sessions基准匹配；实际月末下载快照、真实锁时间之后下一开盘，缺当时捕获绝不历史回填。使用说明及安全核验在research/phase3/forward_v002/README.md。

EXPORT_MANIFEST.json含每个交付文件SHA，EXPORT_RESTORE_VERIFICATION.json记录565无损恢复验收。压缩包CRC与ZIP SHA在随包外部DELIVERY_VERIFICATION.json（ZIP自身哈希不能循环写入其内容）中。无购买、账号密钥或隐藏workspace配置。
