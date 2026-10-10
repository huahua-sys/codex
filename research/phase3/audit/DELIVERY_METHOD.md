# 文件交付路径与验收边界

本轮采用原生共享文件路径，不创建外部下载站点。

依据：`/opt/codex/cua_node/lib/node_modules/@oai/browser-desktop/environment-docs/cloud/cloud-shared-files.md`，章节 **Cloud Shared Files** 与 **Return files to the user**。

原文明确主容器 `/workspace/scratch` 对应浏览器容器 `/home/oai/share`，并要求文件输出使用真实 `sandbox:/workspace/scratch/...` Markdown 链接。原文涵盖 download、PDF、export 或 other file，没有将交付限制在 `/mnt/data` 或特定扩展名。

计划交付目录：`/workspace/scratch/investment_research_delivery_20261009/`。最终答复只引用实际存在、非空且已读回验证的文件。完整 Phase 3 ZIP、原 Phase 2 ZIP 与较小的报告包提供直接下载链接；保留完整 ZIP 的 SHA-256 和 ZIP CRC 验证结果。

## 必须完成的文件验收

1. 完整 ZIP 保存在 `/workspace/outputs/`，不覆盖原 Phase 2 ZIP。
2. 复制到上述共享交付目录。
3. 对原文件及复制件分别计算 SHA-256，确认相同，并检查复制件大小大于零。
4. 通过 `zipfile.ZipFile(...).testzip()` 检查每个交付 ZIP，确认没有损坏成员。
5. 记录完整包的文件清单与每个成员的内容校验值，确认拆包或较小报告包不会被误认为完整研究资料。
6. 最终答复用精确存在路径，例如 `[下载研究包](sandbox:/workspace/scratch/investment_research_delivery_20261009/Investment_Research_Lab_Phase3.zip)`。不得臆造 Sediment ID、上传成功或外部 URL。

## 当前确认与限制

已确认本机存在 `/workspace/scratch` 且当前执行身份可写，已读到上述原生共享路径的本机文档。具体交付文件是否存在、其大小和校验结果由最终 transfer receipt 记录。

这里没有完成浏览器端点击验证，没有收到用户确认下载完成，也没有取得独立的文件上传回执。因此只能报告“文件已复制并校验，可通过文档规定的原生下载路径获取”，不能报告“用户已经收到文件”。

本机内置 Documents/Spreadsheets/PDF 技能另外示范独立段落的 `:codex-file-citation{path="sandbox:/workspace/..." purpose="output"}`。其通用 ZIP 支持无法从工具端单独验证；本轮优先保留上述明确文档化的共享路径 Markdown 下载链接。`mark_artifact_operation_started.mjs` 只做参数校验，不会上传 ZIP，未调用不相关的 authoring marker。
