# Investment Research Lab

长期投资研究档案；首轮日期：2026-10-08 UTC。执行依据：[用户主提示词](sources/Codex_Investment_Research_Lab_Master_Prompt_v3.md)。

**Phase2已完成：真实资料小包、430个选择记录、377有效锁定预测、374成熟12m结果；已验证投资原则仍为0。** 结果属于有限历史重构，不是前瞻盲测。简单择时没有可靠增量，新宏观组合脆弱或样本不足；原15理论候选仍未测，没有晋升或操作框架变更。

优先阅读[条件性研究报告](CONDITIONAL_EDGE_REPORT.md)、[错误分类](ERROR_TAXONOMY.md)、[存活候选](SURVIVING_CANDIDATES.md)与[夜间总结](NIGHT_RESEARCH_REPORT.md)。Phase2可审查包见 `/workspace/outputs/investment_research_phase2/` 与 `Investment_Research_Lab_Phase2.zip`；最新来源、锁、结果、失败保存在本库。

## 阅读入口

- [首轮状态](research/status/LATEST.md)：完成内容、阻塞和下一步。
- [资料清单](DATA_INVENTORY.md) / [项目审计](PROJECT_AUDIT.md)：现有资料、PIT 可行性及逐项任务结果。
- [研究路线图](RESEARCH_ROADMAP.md)：数据门槛、候选排序与轻量验证步骤。
- [研究宪章](RESEARCH_CONSTITUTION.md) / [未来执行指令](AGENTS.md)：禁止后见之明、证据及留档规则。
- [假设登记](HYPOTHESIS_REGISTRY.md) / [候选索引](CANDIDATE_PRINCIPLES.md)：未测试方向及实验，不是推荐或经验发现。
- [首轮案例方案](research/episode_library/ROUND_001_PLAN.md) / [阻塞记录](research/replays/ROUND_001_BLOCKED.md)：未填真实资产、概率或结果。
- [正式投资哲学](INVESTMENT_PHILOSOPHY.md)：仅保留晋升标准，正式原则为空。
- [机器可读框架](CURRENT_FRAMEWORK.json)：供后续研究 / 监控读取；任何候选均不能自动当作已验证信号。

## 目录

`sources/` 保留指令来源；`data/raw/` 等待原始资料；`data/manifests/` 登记来源；`data/labels/` 隔离事后结果；`research/episode_library/` 保存案例；`research/candidate_principles/` 保存候选；`research/experiments/` 保存验证方案；`research/failed_hypotheses/` 永久保存失败；`research/protocols/` 定义流程；`research/templates/` 提供未填写模板；`research/status/` 保存状态；`research/audit/` 保存核验依据。

空目录的 `.gitkeep` 是占位文件，不是数据。该文件夹是本地长期记忆；本轮未配置远端仓库、自动执行或数据采集。

资料到位后的第一步：按 [数据合同](research/protocols/DATA_CONTRACT.md) 核验来源、公开时点、版本、证券池和可交易性，然后冻结样本、实验及结果定义，再开始回放。禁止用模型记忆补齐缺失来源。

本轮档案核验见 [独立复核](research/audit/INDEPENDENT_REVIEW.md) 和 [验收结果](research/audit/ARTIFACT_VERIFICATION.json)。[验收脚本](scripts/verify_artifacts.py) 仅针对 ROUND_001 初始化状态；未来研究新增实证后需按新轮次修订规则。
