# 机制反证审查的复现说明

本目录不是事件收益实验。它不导入价格模块、不读取标签、不生成预测、不改变旧实验。15个目的性审查问题保存在仓库根 `FAILED_MECHANISM_CASES.md`，与主事件抽样框分开。

先检查 `SOURCE_MANIFEST.v001.json` 和 `VERIFIED_EXCERPTS.v001.json`；前者列出17份原字节、SHA、URL、发布日期证据及版本局限，后者保存31条可直接检查的原文。`QA_CHECKPOINT.v001.json` 保存71项PASS，未识别收益优势和因果反事实均为0。

在包含原源的完整仓库，运行：

```bash
python3 research/phase4/audit/counterexamples/build_counterexample_audit.py
```

它验证17份源的SHA和31条摘录，并重建两个派生索引，不重新下载、不重算收益。Python仅用标准库。首次获取所用 `fetch_official_sources.py` 还需要网络和 `pdftotext`，现在不必重新运行；已保存原源优先，网站变化时保留旧文件并新建版本，不能覆盖源字节。

原始文件位于 `sources/counterexamples/`，合计19,093,938字节。若核心包为了<10MB省略较大的原始PDF，核心包仍有索引和逐字摘录，但完整的SHA/原字节验证需使用完整仓库。不要把只有摘要的核心包称为完全独立复现了原源验证。

`FAILED_ACCESS_PROBES.v001.json`保留最初两个404网址，不作证据。`cross_region_review.v001.json`记录对三个区域事件的只读审查；其他agent的文件未修改。

所有摘录和病例均为 `RETROSPECTIVE_SOURCE_AUDIT_ONLY`，`signal_use_permitted=false`。尤其FCIC勘误版本、FSB11月2020报告、Berkshire2009信和GE年报，不能成为更早T的已知输入。日期的明确和字节哈希均不证明模型真正历史盲性。
