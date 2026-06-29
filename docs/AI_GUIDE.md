# AI_GUIDE.md — AI Agent 系统

## Agent 分工

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| **Scientist** | 解释进化树、回答科学问题 | treefile + annotation | 自然语言解释 |
| **Reviewer** | 检查分析流程、挑 Bug | 分析日志 | Bug 报告 |
| **Evolution Analyst** | 分析进化模式、选择压力 | treefile + dN/dS | 进化解释 |
| **Mutation Analyst** | 解释突变位置与效应 | mutation_matrix | 突变报告 |
| **Visualization Expert** | 生成论文级图表 | treefile + annotation | PNG/SVG |
| **Paper Writer** | 撰写论文方法/结果部分 | 全部输出 | Markdown 论文 |

---

## Prompt Library

所有 Prompt 集中管理，不散落各处：

```
prompts/
├── analysis/          # 分析类 Prompt
│   ├── tree_interpretation.md
│   ├── mutation_analysis.md
│   └── evolution_pattern.md
├── review/            # 审查类 Prompt
│   ├── qc_check.md
│   └── pipeline_audit.md
├── coding/            # 代码类 Prompt
│   ├── plugin_template.md
│   └── test_generation.md
├── tree/              # 建树相关 Prompt
│   ├── model_selection.md
│   └── outgroup_selection.md
├── mutation/          # 突变相关 Prompt
│   ├── antigenic_site_mapping.md
│   └── glycan_analysis.md
├── paper/             # 论文相关 Prompt
│   ├── method_writing.md
│   ├── result_writing.md
│   └── figure_caption.md
├── discussion/        # 讨论类 Prompt
│   └── biological_interpretation.md
├── figure/            # 图表类 Prompt
│   ├── phylogenetic_tree.md
│   └── mutation_heatmap.md
└── report/            # 报告类 Prompt
    ├── weekly_report.md
    └── vaccine_monitoring.md
```

### Prompt 格式规范

```markdown
# Prompt Name

**Agent**: Scientist / Reviewer / ...
**Context Needed**: treefile, annotation.json
**Output Format**: Markdown / JSON / Plain Text

---

[Prompt 正文]
```

---

## Knowledge Base 索引

```
knowledge/
├── influenza/
│   ├── H3/
│   │   ├── antigenic_sites.md
│   │   ├── vaccine_history.md
│   │   └── key_mutations.md
│   ├── H1/
│   ├── H5/
│   └── WHO/
│       ├── recommendations_2024.md
│       └── vaccine_strain_history.md
├── Mutation/
│   ├── substitution_models.md
│   └── antigenic_drift_metrics.md
├── Epitope/
│   └── HA_epitope_mapping.md
├── Review/
│   └── influenza_evolution_review.md
└── Guideline/
    └── phylodynamics_best_practices.md
```

---

## GitHub Issue 体系

Issue 类型：

| 类型 | 示例 |
|------|------|
| **Feature** | `Add automatic vaccine strain annotation` |
| **Enhancement** | `Support Nextclade v4 input format` |
| **Research Spec** | `Define outgroup selection policy for H5 trees` |
| **Knowledge** | `Add 2024 WHO vaccine recommendation to DB` |
| **Bug** | `IQ-TREE crash with >1000 sequences` |

### 示例 Issue

```
Issue #21: Add automatic vaccine strain annotation
Type: Feature
Milestone: M5 - Annotation
Priority: High

Description:
Automatically annotate current and historical WHO vaccine strains
on the phylogenetic tree. Pull data from WHO GISRS database.

Acceptance Criteria:
- [ ] Vaccine strains highlighted on tree
- [ ] Strain name + year + recommendation period displayed
- [ ] Support H3N2, H1N1, B/Victoria, B/Yamagata
```

---

## Milestone 体系

| Milestone | 版本 | 核心交付 |
|-----------|------|----------|
| M1: Framework | v0.1 | 插件加载 + CLI |
| M2: QC | v0.2 | 序列质控 |
| M3: Alignment | v0.3 | MAFFT 封装 |
| M4: Tree | v0.4 | IQ-TREE 封装 |
| M5: Annotation | v0.5 | 抗原位点注释 |
| M6: Visualization | v0.6 | 树图 + 热力图 |
| M7: Mutation | v0.7 | 突变追踪 |
| M8: Evolution | v0.8 | dN/dS + 时间树 |
| M9: Report | v0.9 | 自动报告 |
| M10: AI | v1.0 | Agent 系统 |
