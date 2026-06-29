# MODULE_SPEC.md — 模块接口规范

## 通用接口

每个 ViroScope 模块必须实现以下接口：

```yaml
module:
  name: string           # 模块名（如 "tree"）
  version: string        # 语义版本（如 "0.1.0"）
  description: string    # 一句话描述

dependencies:
  - tool: string         # 外部工具名
    min_version: string  # 最低版本
  - python: string       # Python 包依赖

input:
  format: string         # 输入格式（fasta/csv/tsv...）
  required_fields:       # 必需字段
    - name: string
      type: string
  optional_fields:       # 可选字段

output:
  format: string         # 输出格式
  files:
    - name: string
      description: string

exceptions:
  - name: string         # 异常名
    condition: string    # 触发条件
    action: string       # 处理方式
```

---

## Module: QC

| 项 | 值 |
|----|-----|
| 输入 | `sequences.fasta` |
| 输出 | `cleaned.fasta`, `qc_report.json`, `removed.txt` |
| 依赖 | FastQC, CD-HIT |

### 异常

| 异常 | 条件 | 处理 |
|------|------|------|
| NoSequence | 输入无有效序列 | 终止，提示检查文件 |
| AllLowQuality | 全部序列质量不合格 | 输出空 + 报告 |
| DuplicateHighRate | 去重后保留 <10% | 警告，继续 |

---

## Module: Alignment

| 项 | 值 |
|----|-----|
| 输入 | `cleaned.fasta` |
| 输出 | `aligned.fasta` |
| 依赖 | MAFFT |

### 异常

| 异常 | 条件 | 处理 |
|------|------|------|
| TooFewSequences | 序列数 < 3 | 终止建树 |
| SequenceTooShort | 长度 < 预期 50% | 警告，标记 |
| MAFFTTimeout | 超过 30 分钟 | 降级到 FFT-NS-1 |

---

## Module: Tree

| 项 | 值 |
|----|-----|
| 输入 | `aligned.fasta` |
| 输出 | `treefile` (newick), `iqtree.log`, `contree` (if bootstrap) |
| 依赖 | IQ-TREE |

### 异常

| 异常 | 条件 | 处理 |
|------|------|------|
| NoAlignment | 输入无比对文件 | 终止 |
| DuplicateSequence | 完全相同的序列 | 去重后继续 |
| TreeFailed | IQ-TREE 异常退出 | 终止，输出 log |
| LowBootstrap | 多数节点 < 70 | 警告，继续 |

---

## Module: Annotation

| 项 | 值 |
|----|-----|
| 输入 | `aligned.fasta` (HA 基因) |
| 输出 | `annotation.json`, `annotation_summary.tsv` |
| 依赖 | 内置参考序列（A/Aichi/2/1968 H3N2 编号体系） |

### 异常

| 异常 | 条件 | 处理 |
|------|------|------|
| NotHA | 不是 HA 基因 | 终止 |
| FrameShift | 移码突变 > 5% 序列 | 警告，标记 |

---

## Module: Visualization

| 项 | 值 |
|----|-----|
| 输入 | `treefile` + `annotation.json` |
| 输出 | `tree.png`, `mutation_heatmap.png` |
| 依赖 | R (ggtree, ggtreeExtra) |

---

## Module: Mutation

| 项 | 值 |
|----|-----|
| 输入 | `aligned.fasta` + `annotation.json` |
| 输出 | `mutation_matrix.tsv`, `antigenic_distance.tsv` |

---

## Module: Report

| 项 | 值 |
|----|-----|
| 输入 | 所有上游输出 |
| 输出 | `report.md`, `figures/` |
| 依赖 | AI Agent (Paper Writer) |
