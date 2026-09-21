---
name: git-worktree
description: Git worktree 管理。创建、列出、删除 worktree，以及在 worktree 间切换。当用户需要新建 worktree、在不同分支间并行工作、清理已完成工作的 worktree 时使用。
metadata:
  version: 20260921.202053
  update-url: https://github.com/bonaluo/agent-skills@git-worktree
---

# git-worktree

Git worktree 管理技能。为用户提供交互式的 worktree 创建流程，自动推断配置并持久化用户偏好。

## 配置优先级

worktree 配置按以下优先级查找（越靠前优先级越高）：

1. 用户明确指定的参数
2. 当前工作目录中的配置：
   - `.<当前Agent目录>/skills/git-worktree/git-worktree.config`
   - `.agents/skills/git-worktree/git-worktree.config`
3. 用户主目录中的配置：
   - `~/.<当前Agent目录>/skills/git-worktree/git-worktree.config`
   - `~/.agents/skills/git-worktree/git-worktree.config`
4. Skill 默认配置（本 SKILL.md 中定义的默认值）

配置文件为 JSON 结构，文件名为 `git-worktree.config`。

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `path` | worktree 存储的相对路径或绝对路径 | `.agents/worktree` |
| `lan` | 目录命名语言，`zh` 中文 / `en` 英文 | `zh` |

## 使用时机

用户要求新建 worktree 时触发。典型场景：

- 需要在新分支上并行开发，互不干扰主分支
- 需要同时处理多个任务的代码
- 临时验证某个方案，需要隔离环境

## 创建流程

当用户要求新建 worktree 时，按以下步骤交互收集信息：

### 1. 询问 worktree 存储路径

- 从配置优先级中读取当前 `path` 值
- 如果配置中有值，直接作为默认选项提供
- 如果配置中没有值，使用默认 `.agents/worktree`，并询问用户是否将该路径写入配置

### 2. 询问 worktree 目录名称

- 根据用户要做的任务内容自动生成推荐名称
- 从配置优先级中读取 `lan` 值：
  - `zh`（默认）：推荐名称使用中文
  - `en`：推荐名称使用英文
- 如果用户提供了自定义名称，询问是否持久化保存到配置

### 3. 询问分支策略

提供以下选项：

- 基于现有分支新建分支（需要用户指定基础分支名称和新的分支名称）
- 使用现有分支（需要用户指定要使用的分支名称）

### 4. 确认并执行

向用户展示所有收集到的信息，确认后执行：

```bash
git worktree add <worktree目录路径>/<worktree目录名称> <分支引用>
```

分支引用格式：
- 基于现有分支新建：`origin/<基础分支名>:<新分支名>` 或直接 `<新分支名>`（如果本地已有）
- 使用现有分支：`<已有分支名>`

## 目录结构

```
skills/git-worktree/
├── SKILL.md            # 本文件
├── references/         # 详细说明文档
└── scripts/            # 辅助脚本
```
