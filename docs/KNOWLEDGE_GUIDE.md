# KNOWLEDGE_GUIDE.md — 知识体系

## 知识层级

```
Knowledge
├── Virus（病毒学基础）
│   ├── Influenza
│   │   ├── HA（血凝素）
│   │   ├── NA（神经氨酸酶）
│   │   └── NP（核蛋白）
│   ├── IHNV
│   ├── NDV
│   └── SARS-CoV-2
│
├── Evolution（进化生物学）
│   ├── Phylogeny（系统发育）
│   ├── Molecular Clock（分子钟）
│   ├── Selection（自然选择）
│   └── Phylogeography（系统地理学）
│
├── Mutation（突变科学）
│   ├── Substitution Models（替换模型）
│   ├── dN/dS（选择压力）
│   ├── Epistasis（上位效应）
│   └── Convergent Evolution（趋同进化）
│
├── Vaccine（疫苗学）
│   ├── WHO Recommendations（WHO 推荐）
│   ├── Antigenic Drift（抗原漂移）
│   ├── Egg Adaptation（鸡胚适应）
│   └── Reverse Genetics（反向遗传学）
│
├── Epitope（表位）
│   ├── B-cell Epitope
│   ├── T-cell Epitope
│   └── Antigenic Site Mapping
│
├── Structure（结构生物学）
│   ├── HA Trimer（三聚体结构）
│   ├── RBS（受体结合位点）
│   ├── Glycosylation（糖基化）
│   └── Fusion Peptide（融合肽）
│
└── Bioinformatics（生信工具）
    ├── MAFFT
    ├── IQ-TREE
    ├── BEAST
    ├── TreeTime
    └── Nextclade
```

---

## 知识条目模板

每个知识条目遵循：

```yaml
id: FACT-XXXX
category: [Virus/Evolution/Mutation/Vaccine/Epitope]
virus: [Influenza/IHNV/NDV/SARS-CoV-2]
topic: 一句话主题
summary: 2-3 句摘要
details: 详细机制解释
references:
  - DOI: 10.xxxx/xxxx
consequences:
  - 对疫苗设计的影响
  - 对进化分析的影响
last_updated: YYYY-MM-DD
```

---

## 知识来源层级

1. **权威** — WHO 推荐、FDA/EMA 指南、教科书
2. **高** — Nature/Science/Cell 原创研究
3. **中** — 专业期刊（J Virol, PLoS Pathog, Vaccine）
4. **补充** — 预印本、会议摘要（需标注）

---

## 知识更新规范

- 每季度审查一次 WHO 疫苗推荐更新
- 每半年更新关键突变知识库
- 新发表的高影响力论文 2 周内录入
