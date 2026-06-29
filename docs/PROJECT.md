# PROJECT.md — ViroScope OS

## Mission

构建一个 AI 驱动的病毒学科研操作系统，让计算病毒学分析从"手写脚本"进化为"结构化、可复现、可扩展的科研平台"。

## Vision

到 2030 年，成为病毒进化与疫苗设计领域最广泛使用的开源科研操作系统。

## Objectives

1. **标准化** — 将病毒学核心分析流程（建树、突变注释、疫苗抗原位点分析）固化为可复现的模块
2. **AI 原生** — 每个模块都有对应的 AI Agent，能解释结果、发现异常、生成论文图表
3. **可扩展** — 从流感起步，逐步支持 IHNV、NDV、SARS-CoV-2 等病毒
4. **低门槛** — 不需要生物信息学背景，用自然语言就能驱动分析

## Supported Virus (Phase 2+)

| 病毒 | 阶段 | 核心分析 |
|------|------|----------|
| Influenza A (H1/H3/H5) | Phase 2 | 进化树、抗原漂移、疫苗株匹配 |
| IHNV | Phase 3 | 系统发育、毒力相关位点 |
| NDV | Phase 3 | 基因型分类、F 蛋白裂解位点 |
| SARS-CoV-2 | Phase 4 | 谱系追踪、S 蛋白突变监测 |

## Target Users

- 病毒学研究生 / 博士后
- 疫苗研发人员
- WHO 流感疫苗参考实验室
- 水产养殖病毒监测站

## Core Features (v1.0)

1. **QC** — 序列质控、去冗余、异常检测
2. **Alignment** — 多序列比对（MAFFT）
3. **Tree** — 系统发育树构建（IQ-TREE）
4. **Annotation** — HA 抗原位点、糖基化位点、RBS 注释
5. **Mutation** — 突变追踪、抗原漂移量化
6. **Visualization** — 进化树可视化、突变热力图
7. **AI Report** — 自动生成科研报告和论文图

## Research Scope

- 流感病毒 HA 基因进化（全局 + 谱系级）
- 抗原位点突变与疫苗有效性预测
- 跨宿主传播事件的系统发育信号
- 时间树估算（BEAST / TreeTime）

## Long-term Plan

| 年份 | 里程碑 |
|------|--------|
| 2026 | ViroScope OS v0.1–v1.0（流感模块） |
| 2027 | 流感 + IHNV 双病毒支持 |
| 2028 | 病毒研究平台（多病毒通用框架） |
| 2029 | AI Research Operating System（多 Agent 协作） |
| 2030 | 社区驱动的插件生态 |

## License

MIT License — 学术与商业友好。
