# Visual Production 研究归档 · 2026-10-05

从 `visual-search-adhoc/docs/daily_report/10.05/` 复制，归档日期为 2026-11-04。原仓库内容保留。

这份历史研究聚焦电商模特换装与专业修图的交付可靠性、可控迭代修改和验收方法。研究当时仅做资料分析，没有新建流水线或回放客户案例；文中的建议、访问限制、模型及许可状态均保留原研究时点口径，本次复制没有重新验证或更新结论。

## 阅读顺序

1. [Visual Production 摘要](VISUAL_PRODUCTION_SUMMARY.md)：从当天 `BOSS_SUMMARY.md` 的 Visual Production 部分逐字摘录，未包含无关的 ASL 内容。
2. [技术与工作流综述](VISUAL_PRODUCTION_SOTA_AND_WORKFLOW_LANDSCAPE.md)：主要发现、证据强度与建议验证实验。
3. [候选 Curify 流水线](candidate_curify_pipelines.md)：CP1–CP5，含局部锁定修改、换装、参数化修图及交付质检。
4. [学术方法表](academic_methods.csv)、[实践工作流表](practitioner_workflows.csv)、[失败—解决方案矩阵](failure_solution_matrix.csv)。
5. [来源清单](sources.md)：外部引用、访问深度与受阻来源。

## 来源与完整性

六份研究文件保持字节一致；摘要为原文件指定章节的逐字摘录。[导入清单](IMPORT_MANIFEST.json) 记录固定来源提交、每份文件的来源链接及 SHA-256。

原始目录：[10 月 5 日研究目录](https://github.com/super-inbox/visual-search-adhoc/tree/2d5559593ccdb922603dddf458018e5935f5239e/docs/daily_report/10.05/visual-production-research)。原始日报：[BOSS_SUMMARY.md](https://github.com/super-inbox/visual-search-adhoc/blob/2d5559593ccdb922603dddf458018e5935f5239e/docs/daily_report/10.05/BOSS_SUMMARY.md)。

`sources.md` 中以 `docs/daily_report/8.*` 表示的早期背景资料仍指向 **visual-search-adhoc**，不是本仓库的本地路径；这些较早、跨主题的资料未随本次专题复制。可从下列固定版本入口访问：

- [8.8](https://github.com/super-inbox/visual-search-adhoc/tree/2d5559593ccdb922603dddf458018e5935f5239e/docs/daily_report/8.8)
- [8.7](https://github.com/super-inbox/visual-search-adhoc/tree/2d5559593ccdb922603dddf458018e5935f5239e/docs/daily_report/8.7)
- [8.16](https://github.com/super-inbox/visual-search-adhoc/tree/2d5559593ccdb922603dddf458018e5935f5239e/docs/daily_report/8.16)
- [8.19](https://github.com/super-inbox/visual-search-adhoc/tree/2d5559593ccdb922603dddf458018e5935f5239e/docs/daily_report/8.19)
