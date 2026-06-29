# ARCHITECTURE.md — 插件化架构

## 设计原则

1. **插件化** — 每个分析模块是独立插件，可单独安装/升级/替换
2. **数据流** — 模块间通过标准化的输入/输出接口传递数据
3. **无状态** — 每个模块不依赖全局状态（配置文件除外）
4. **工具封装** — 不重新发明算法，封装 MAFFT、IQ-TREE、BEAST 等成熟工具

## 核心架构

```
ViroScope OS
├── Core（核心引擎）
│   ├── Plugin Loader    — 插件发现、加载、版本管理
│   ├── Config System    — YAML 配置管理
│   ├── CLI              — 命令行入口
│   └── Logger           — 统一日志
│
├── Plugins（分析插件）
│   ├── QC               — 序列质控
│   ├── Alignment        — 多序列比对
│   ├── Tree             — 系统发育树
│   ├── Metadata         — 元数据管理
│   ├── Annotation       — 功能注释
│   ├── Mutation         — 突变分析
│   ├── Evolution        — 进化分析
│   ├── Visualization    — 可视化
│   ├── Report           — 报告生成
│   └── AI               — AI Agent 系统
│
├── Knowledge Base（知识库）
│   ├── Virus DB         — 病毒参考序列/注释
│   ├── Mutation DB      — 已知突变效应
│   ├── Epitope DB       — 抗原表位
│   └── Vaccine DB       — 疫苗株信息
│
└── Specs（科研规范）
    ├── Phylogeny        — 建树规范
    ├── Interpretation   — 结论规范
    ├── Visualization    — 作图规范
    └── Publication      — 发表规范
```

## 插件接口规范

每个插件必须实现：

```python
class Plugin:
    name: str
    version: str
    dependencies: list[str]       # 依赖的外部工具
    input_spec: dict              # 输入格式
    output_spec: dict             # 输出格式
    
    def run(self, input_data, config) -> output_data:
        ...
    
    def validate_input(self, input_data) -> bool:
        ...
    
    def validate_output(self, output_data) -> bool:
        ...
```

## 依赖的外部工具

| 工具 | 用途 | 对应插件 |
|------|------|----------|
| MAFFT | 多序列比对 | Alignment |
| IQ-TREE | 系统发育树 | Tree |
| FastQC | 序列质控 | QC |
| CD-HIT | 去冗余 | QC |
| BEAST | 时间树 | Evolution |
| TreeTime | 时间树 | Evolution |
| ggtree | R 可视化 | Visualization |
| PyMOL | 蛋白结构 | Annotation |

## 数据流

```
FASTA → QC → Alignment → Tree → Annotation → Visualization → Report
                                     ↓
                                Metadata DB
                                     ↓
                                AI Agent
```

## 目录结构

```
ViroScope-OS/
├── src/
│   ├── core/           # 核心引擎
│   └── plugins/        # 分析插件
├── docs/               # 文档
├── specs/              # 科研规范
├── prompts/            # AI Prompt 库
├── knowledge/          # 知识库
├── tests/              # 测试
├── configs/            # 配置文件
└── database/           # 数据库相关
```
