# ARCHITECTURE

## 设计原则

系统保持模块化。每个模块只做一件事，模块之间通过清晰的输入输出文件衔接。

## 核心结构

```text
Core
├── QC
├── Alignment
├── Tree
├── Metadata
├── Annotation
├── Visualization
├── Interpretation
└── Report
```

## 模块契约

每个模块都要定义：

- 目的
- 输入
- 输出
- 依赖
- 异常情况

## 最小示例

### Tree Module

目的：

- 为流感比对后序列构建最大似然树

输入：

- `aligned.fasta`
- 可选元数据表

输出：

- `*.treefile`
- `*.log`
- `*.contree`

依赖：

- IQ-TREE

异常情况：

- 缺少比对文件
- 序列集合为空
- 存在重复或非法记录
- 建树失败

## 扩展原则

以后像 `BEAST`、`Selection`、`Protein` 这样的能力，作为新模块增加，不要回头把旧模块改成一团。

## 先规范再实现

每个模块开始写代码之前，先在 `specs/` 里补对应科研规范。
