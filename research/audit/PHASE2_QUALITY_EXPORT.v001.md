# Phase2 最终导出独立验收

状态：`PASS`。本记录核验重导出纳入本QA之前的v001包；最终交付包SHA由包外 `/workspace/outputs/Investment_Research_Lab_Phase2.export_verification.json` 保存，避免要求ZIP包含自身最终哈希的循环。

已独立检查：ZIP非空、CRC全通过、路径无越界/重复；2,871个manifest文件的字节大小与SHA256全部匹配；所有复制项目文件与原仓库字节相同；八份必需Phase2报告、night报告、README、最终checkpoint与恢复工具都在包中。CURRENT_FRAMEWORK是当前计数、live=false、validated=[]，原操作性字段没有晋升。

独立离线运行恢复程序 `--verify-only` 完成565个原文件精确SHA验证，退出0；没有网络请求，没有写入1.67GB重复数据，也没有重跑研究。蓝图包含430有效cohort输入、120永久排除的旧锁pilot输入和2个未完成/未锁行业尝试输入，共552输入，再加13行政bundle。保留这些工件不增加有效预测或案例数量；未揭晓的污染pilot不参加统计。

README给出审查优先级、最重要失败/候选结论、下一数据需求、原布局与精确恢复方法。canonical源字节、原预测/锁/标签、来源及脚本均保留。lossless dedup仅消除重复价格行存储，全部原SHA保持不变；它不提高历史vintage、盲性或经济证据等级。

科学核验见[PHASE2_QUALITY_SCIENTIFIC_REVIEW.v001.md](PHASE2_QUALITY_SCIENTIFIC_REVIEW.v001.md)，最终记忆核验见[PHASE2_QUALITY_MEMORY.v001.json](PHASE2_QUALITY_MEMORY.v001.json)，机器导出核验见[PHASE2_QUALITY_EXPORT.v001.json](PHASE2_QUALITY_EXPORT.v001.json)。
