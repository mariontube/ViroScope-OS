# DATABASE_GUIDE.md — 数据库设计

## 数据库体系

```
Database
├── Mutation DB（突变数据库）
│   ├── 已知 HA 突变的抗原效应
│   ├── 鸡胚适应性突变
│   └── 耐药突变
│
├── Epitope DB（表位数据库）
│   ├── B-cell 表位坐标
│   ├── T-cell 表位坐标
│   └── 中和抗体结合位点
│
├── Antigenic Site DB（抗原位点数据库）
│   ├── H3N2 抗原位点 A-E（基于 A/Aichi/2/1968）
│   ├── H1N1 抗原位点 Sa/Sb/Ca1/Ca2/Cb
│   └── H5 抗原位点
│
├── RBS DB（受体结合位点数据库）
│   ├── 130-loop
│   ├── 190-helix
│   └── 220-loop
│
├── Glycosylation DB（糖基化位点数据库）
│   ├── 已知 N-糖基化位点
│   ├── 糖基化获得/丢失对疫苗有效性的影响
│   └── 关键糖基化位点保守性
│
├── WHO Vaccine DB（WHO 疫苗株数据库）
│   ├── 历年推荐疫苗株
│   ├── 疫苗株与流行株的遗传距离
│   └── 疫苗株变更历史
│
└── Reference DB（参考序列数据库）
    ├── 各亚型参考序列
    ├── Outgroup 序列
    └── 标准命名体系映射
```

---

## 查询能力（目标）

输入一个突变，AI 立即返回：

```python
> query("H3N2", "Y159N")

# 返回:
{
  "mutation": "Y159N",
  "position": 159,
  "site": "Antigenic Site B",
  "glycosylation": "No change",
  "RBS": "No",
  "known_effect": "Antigenic drift (moderate)",
  "vaccine_relevance": "Emerging in 2024-25 season",
  "references": ["DOI:10.xxxx/xxxx"]
}
```

---

## 存储方案

| 层 | 技术 | 用途 |
|----|------|------|
| 结构化数据 | SQLite | 突变、表位、参考序列 |
| 文档 | JSON/YAML | 知识条目、元数据 |
| 序列 | FASTA 文件 | 参考序列、比对 |
| 向量 | ChromaDB（可选） | 语义搜索 |

---

## 数据来源

| 数据库 | 内容 | 更新频率 |
|--------|------|----------|
| GISAID | 流感序列 + 元数据 | 按需拉取 |
| NCBI GenBank | 公开病毒序列 | 按需拉取 |
| WHO GISRS | 疫苗株推荐 | 每半年 |
| IEDB | 免疫表位 | 按需查询 |
| Nextstrain | 进化分析 | 参考 |
