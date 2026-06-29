# ROADMAP.md — 开发路线图

## Phase 0: 项目模板（Current）

- [x] GitHub 仓库创建
- [x] 目录结构
- [x] 文档体系（12 份核心文档）
- [ ] GitHub Issue 体系搭建
- [ ] Milestone 创建

## Phase 1: 基础框架（v0.1–v0.3）

| 版本 | 模块 | 核心功能 |
|------|------|----------|
| v0.1 | Framework | 插件加载器、配置系统、CLI 入口 |
| v0.2 | QC | FastQC 适配、序列去冗余、异常检出 |
| v0.3 | Alignment | MAFFT 封装、格式转换、比对质量报告 |

## Phase 2: 树与注释（v0.4–v0.6）

| 版本 | 模块 | 核心功能 |
|------|------|----------|
| v0.4 | Tree | IQ-TREE 封装、模型自动选择、Bootstrap |
| v0.5 | Annotation | HA 抗原位点、糖基化位点、RBS 自动注释 |
| v0.6 | Visualization | ggtree/ggtreeExtra 封装、突变热力图 |

## Phase 3: 进化分析（v0.7–v0.9）

| 版本 | 模块 | 核心功能 |
|------|------|----------|
| v0.7 | Mutation | 突变追踪矩阵、抗原漂移量化 |
| v0.8 | Evolution | 选择压力分析（dN/dS）、时间树集成 |
| v0.9 | Report | 自动科研报告生成、论文图输出 |

## Phase 4: AI 集成（v1.0）

| 版本 | 模块 | 核心功能 |
|------|------|----------|
| v1.0 | AI | 多 Agent 系统、自然语言接口、知识库 |

## Phase 5: 平台化（v1.1+）

| 版本 | 模块 | 核心功能 |
|------|------|----------|
| v1.1 | IHNV | 鱼类弹状病毒模块 |
| v1.2 | Web | Web 可视化面板 |
| v2.0 | Platform | 多病毒通用平台 |

---

## Milestone 体系

| Milestone | 版本 | 目标 |
|-----------|------|------|
| M1: Framework | v0.1 | 插件加载 + CLI |
| M2: QC | v0.2 | 序列质控 |
| M3: Alignment | v0.3 | 多序列比对 |
| M4: Tree | v0.4 | 系统发育树 |
| M5: Annotation | v0.5 | 自动注释 |
| M6: Visualization | v0.6 | 可视化 |
| M7: Mutation | v0.7 | 突变分析 |
| M8: Evolution | v0.8 | 进化分析 |
| M9: Report | v0.9 | 报告生成 |
| M10: AI | v1.0 | AI Agent 系统 |
| M11: Platform | v2.0 | 多病毒平台 |
