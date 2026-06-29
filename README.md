# ViroScope OS — AI 驱动的病毒学科研操作系统

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/mariontube/ViroScope-OS)
[![Python](https://img.shields.io/badge/python-3.10%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

> 一行命令，完成从原始序列到可发表进化树的完整分析。

---

## 15 秒了解

```bash
# 安装
bash install.sh

# 三步出结果
python3 -m viroscope.cli run nextclade my_seqs.fasta -d flu_h3n2_ha   # 进化枝分析
python3 -m viroscope.cli run alignment   my_seqs.fasta                # 多序列比对
python3 -m viroscope.cli run tree        aligned.fasta                # 系统发育树

# 看图
python3 -m viroscope.cli run visualization tree.nwk
```

输出：
```
├── A/Brisbane/11/2023
    │   ├── A/Victoria/4897
    │   └── A/Kansas/14
    └── A/Texas/141/2024
```

---

## 你需要什么

| 需求 | 说明 |
|------|------|
| Python 3.10+ | 系统自带或 [下载](https://python.org) |
| FASTA 序列 | 从 GISAID / NCBI 下载 |
| 网络（首次） | 下载参考数据集（~50MB）和工具 |
| 之后 | **全部离线可用** |

---

## 完整安装（1 分钟）

```bash
git clone https://github.com/mariontube/ViroScope-OS.git
cd ViroScope-OS
bash install.sh
```

`install.sh` 会自动下载 Nextclade、配置环境。MAFFT 和 IQ-TREE 需手动安装（或 conda）：

```bash
conda install -c bioconda mafft iqtree
```

---

## 10 个分析插件

| # | 插件 | 做什么 | 依赖 |
|---|------|--------|------|
| 1 | `qc` | 去重、异常检测 | 无 |
| 2 | `nextclade` | 进化枝分配、突变标注 | Nextclade |
| 3 | `alignment` | 多序列比对 | MAFFT |
| 4 | `tree` | ML 系统发育树 (IQ-TREE) | IQ-TREE |
| 5 | `annotation` | 抗原位点 / RBS / 糖基化注释 | 无 |
| 6 | `visualization` | ASCII 树 + ggtree 出图 | R(可选) |
| 7 | `mutation` | 突变追踪矩阵、抗原漂移评分 | 无 |
| 8 | `evolution` | dN/dS 选择压力分析 | 无 |
| 9 | `report` | 自动生成科研报告 | 无 |
| 10 | `ai` | 6 个 AI Agent 科研助手 | 无 |

---

## AI Agent 系统

内置 6 个专业 Agent，每个都能独立解释分析结果：

```bash
# 让 Scientist Agent 解释你的树
python3 -m viroscope.cli run ai tree_analysis.json --agent scientist
```

| Agent | 职责 |
|-------|------|
| Scientist | 解释系统发育树 |
| Reviewer | 检查分析流程错误 |
| Evolution Analyst | 分析选择压力 |
| Mutation Analyst | 解释突变抗原效应 |
| Paper Writer | 撰写论文初稿 |
| Visualization Expert | 设计发表级图表 |

---

## 完整文档

| 文档 | 内容 |
|------|------|
| [PROJECT.md](docs/PROJECT.md) | 项目定义 |
| [ROADMAP.md](docs/ROADMAP.md) | 开发路线 |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | 架构设计 |
| [RESEARCH_SPEC.md](docs/RESEARCH_SPEC.md) | 科研规范（AI 必须遵守） |
| [AI_GUIDE.md](docs/AI_GUIDE.md) | AI Agent 系统设计 |

---

## 支持的病毒（计划）

| 病毒 | 状态 |
|------|------|
| Influenza A H3N2 | ✅ 完整支持 |
| Influenza A H1N1pdm | ✅ 数据集可用 |
| Influenza A H5Nx | ✅ 数据集可用 |
| IHNV | 📋 计划中 |
| NDV | 📋 计划中 |
| SARS-CoV-2 | 📋 计划中 |

---

## 引用

如果 ViroScope OS 帮助了你的研究：

```
ViroScope OS: AI-powered virus research operating system.
https://github.com/mariontube/ViroScope-OS
```

---

## License

MIT — 学术和商业用途均免费。
