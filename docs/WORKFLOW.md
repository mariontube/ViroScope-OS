# WORKFLOW.md — 科研流程

## 完整科研工作流

```
Question（科学问题）
    │
    ▼
Sequence Retrieval（序列获取：GISAID / NCBI）
    │
    ▼
QC（质控：去冗余、异常检测）
    │
    ▼
Alignment（多序列比对：MAFFT）
    │
    ▼
Tree（系统发育树：IQ-TREE / BEAST）
    │
    ▼
Annotation（注释：抗原位点、糖基化、RBS）
    │
    ▼
Interpretation（科研解释）
    │
    ▼
Publication（论文图表 / 报告生成）
```

---

## Phase 1: 科学问题定义

回答以下问题后再启动分析：

1. 研究目的是什么？
   - 疫苗株推荐？
   - 进化速率估算？
   - 跨宿主传播？
   - 抗原漂移特征？

2. 分析范围？
   - 全球 / 区域 / 国家？
   - 时间范围？
   - 亚型 / 谱系？

3. 预期产出？
   - 系统发育树
   - 抗原位点突变热力图
   - 时间树 + 进化速率
   - 完整论文初稿

---

## Phase 2: 序列获取

### 来源优先级
1. GISAID（流感首选）
2. NCBI GenBank（公开数据）
3. IRD（流感研究数据库）

### 采样规范 → 见 `specs/phylogeny.md`

---

## Phase 3: QC → Alignment → Tree

按顺序执行 ViroScope 模块：
1. `viroscope qc` — 序列清洗
2. `viroscope align` — 多序列比对
3. `viroscope tree` — 建树

---

## Phase 4: 注释与解释

1. 抗原位点突变注释
2. 糖基化位点变化
3. RBS 突变
4. 选择压力分析（dN/dS）

---

## Phase 5: 输出

1. 进化树图（标注关键谱系）
2. 突变热力图（抗原位点）
3. 抗原距离矩阵
4. AI 生成的科研报告
5. 论文图（可发表格式）

---

## 决策树（什么时候用什么分析）

```
需要看进化关系？
├── ML Tree（IQ-TREE）     — 大多数场景
└── Time Tree（BEAST）     — 需要时间刻度+进化速率

需要看抗原关系？
├── Antigenic Distance     — 突变计数 + 抗原位点加权
└── Antigenic Cartography  — 血清学数据（HI 滴度）

需要看选择压力？
├── dN/dS (SLAC/FEL)       — 位点水平
└── MEME                    — 分支水平
```
