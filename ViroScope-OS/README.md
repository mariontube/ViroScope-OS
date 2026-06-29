# ViroScope OS

`ViroScope OS` 是一个面向病毒进化研究的科研操作系统。

第一阶段聚焦 `Influenza A`，并以 `H3N2 HA` 的系统发育分析作为首个落地流程。后续再扩展到其他病毒、AI辅助解释、可视化和报告生成。

## 从这里开始

如果你现在是从零开始搭项目，只做下面 4 步：

1. 阅读 [docs/PRD.md](/E:/桌面/codex/flu%20work/ViroScope-OS/docs/PRD.md)
2. 阅读 [docs/PROJECT.md](/E:/桌面/codex/flu%20work/ViroScope-OS/docs/PROJECT.md)
3. 阅读 [docs/ROADMAP.md](/E:/桌面/codex/flu%20work/ViroScope-OS/docs/ROADMAP.md)
4. 阅读 [docs/ARCHITECTURE.md](/E:/桌面/codex/flu%20work/ViroScope-OS/docs/ARCHITECTURE.md)

## 目录结构

```text
ViroScope-OS/
├── docs/         # 核心文档
├── src/          # 代码
├── tests/        # 最小测试
├── prompts/      # 提示词库
├── knowledge/    # 知识库
├── configs/      # 配置
├── database/     # 数据表与索引
└── specs/        # 科研规范
```

## 推荐开发顺序

1. 先完成项目模板
2. 再做流感元数据与QC
3. 再做比对
4. 再做系统发育树
5. 再做注释
6. 再做可视化
7. 再做突变与演化解释
8. 最后做报告输出

## 当前规则

先写科研规范，再写代码。
