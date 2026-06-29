# CODING_GUIDE.md — 开发规范

## 语言与环境

- **主语言**: Python 3.10+
- **可视化**: R (ggtree, ggplot2) — 仅 Visualization 插件
- **运行平台**: Linux（AutoDL）/ macOS
- **包管理**: conda / mamba

## 代码风格

- 遵循 [PEP 8](https://peps.python.org/pep-0008/)
- 类型注解：所有公共函数必须有 type hints
- 文档字符串：Google style docstrings

```python
def align_sequences(
    input_fasta: str,
    method: str = "auto",
    nthread: int = 4,
) -> str:
    """Run MAFFT multiple sequence alignment.
    
    Args:
        input_fasta: Path to input FASTA file.
        method: MAFFT method (auto, linsi, ginsi, fftns).
        nthread: Number of CPU threads.
    
    Returns:
        Path to aligned output FASTA.
    
    Raises:
        AlignmentError: If MAFFT returns non-zero exit code.
    """
```

## 项目结构

```
src/
├── core/
│   ├── __init__.py
│   ├── plugin_loader.py   # 插件发现与加载
│   ├── config.py          # YAML 配置管理
│   ├── cli.py             # Click CLI 入口
│   └── logger.py          # 统一日志
│
└── plugins/
    ├── __init__.py
    ├── base.py            # 插件基类
    ├── qc/
    │   ├── __init__.py
    │   └── plugin.py
    ├── alignment/
    │   ├── __init__.py
    │   └── plugin.py
    └── tree/
        ├── __init__.py
        └── plugin.py
```

## 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块 | snake_case | `plugin_loader.py` |
| 类 | PascalCase | `PluginLoader` |
| 函数 | snake_case | `load_plugin()` |
| 常量 | UPPER_SNAKE | `DEFAULT_NTHREAD` |
| 私有 | `_` 前缀 | `_validate_input()` |

## Git 规范

### Commit Message

```
<type>: <short description>

Types: feat, fix, docs, refactor, test, chore

Example:
feat: add IQ-TREE plugin with model auto-selection
fix: handle empty FASTA in QC module
docs: update sampling guidelines in RESEARCH_SPEC.md
```

### Branch 命名

```
feature/plugin-tree
fix/alignment-timeout
docs/module-spec-v0.2
```

## 测试

- 框架：pytest
- 覆盖目标：核心模块 ≥80%
- CI：GitHub Actions（Phase 1 后添加）

## 依赖管理

- Python 依赖：`requirements.txt` 或 `environment.yaml`
- 外部工具：在 README 中列出，不自动安装
- 版本固定：核心依赖固定主版本号
