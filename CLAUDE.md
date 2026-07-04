# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

## 概述

这是一个面向 Claude Code 的**技能库** — 收集了多种专业技能，用于扩展 Claude 在特定领域的能力。技能是模块化、自包含的包，包含专业知识、工作流程和工具。

## 仓库结构

```
.agents/skills/skill-creator/  # 技能创建工具
skills/                         # 已发布的技能
    ├── backend-java/           # Spring Boot + Maven + MySQL + MyBatis
    ├── scriptcat-skill/        # 浏览器用户脚本开发
    ├── podman-skill/           # 容器操作
    ├── docker-deploy/          # Docker 标准化构建部署流程
    └── paginate-skill/         # 分页组件
```

## 技能结构

每个技能遵循此模式：
```
skill-name/
├── SKILL.md          # 必需：YAML frontmatter + 使用说明
├── references/       # 可选：按需加载的详细文档
├── scripts/          # 可选：可执行脚本 (Python/Bash)
└── assets/           # 可选：输出文件 (模板、图片等)
```

## 创建新技能

使用技能创建工作流：

1. **初始化**：运行 `python .agents/skills/skill-creator/scripts/init_skill.py <name> --path skills/`
2. **实现**：编辑 SKILL.md 并添加 references/scripts/assets
3. **打包**：运行 `python .agents/skills/skill-creator/scripts/package_skill.py skills/<name>/`

关键原则：
- SKILL.md 必须包含 YAML frontmatter，包含 `name` 和 `description`
- 保持 SKILL.md 在 500 行以内，详细内容移至 `references/`
- 指令使用祈使句形式
- 只创建必要文件 — 不需要 README、CHANGELOG 等

## 可用技能

| 技能 | 使用场景 |
|------|----------|
| backend-java | Java 后端服务，Spring Boot、Maven、MyBatis、MySQL、Flyway |
| scriptcat-skill | 浏览器用户脚本，GM 函数，跨域请求 |
| podman-skill | 本地容器操作（先使用远程连接 `podman-remote-win`） |
| docker-deploy | Docker 标准化构建部署，Dockerfile → Compose → env → 多环境 |
| paginate-skill | 固定位置分页 UI 组件 |
| doc-manage | 结构化文档管理，使用 index.doc.md 索引，分类子目录组织 |
| skill-creator | 创建或更新技能 |

## 技能创建器参考

`.agents/skills/skill-creator/` 目录包含：
- `SKILL.md` — 技能创建方法论和工作流模式
- `references/workflows.md` — 顺序和条件工作流模式
- `references/output-patterns.md` — 模板和示例模式
- `scripts/init_skill.py` — 脚手架工具
- `scripts/package_skill.py` — 验证和打包技能为 .skill 文件
- `scripts/quick_validate.py` — 验证技能（不打包）
