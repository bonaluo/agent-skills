---
name: git-worktree
description: Git worktree 管理。创建、列出、删除 worktree，以及在 worktree 间切换。当用户需要新建 worktree、在不同分支间并行工作、清理已完成工作的 worktree 时使用。
metadata:
  version: 20261012.142111
  update-url: https://github.com/bonaluo/agent-skills@git-worktree
---

# git-worktree

Git worktree 管理技能。根据任务自动推荐 worktree 配置，一次确认后创建，并可持久化用户偏好。

## 配置优先级

worktree 配置按以下优先级查找（越靠前优先级越高）。每一级内部，当前 agent 类型目录优先，其次为通用的 `.agents` 目录。`<agent目录>` 由 agent 根据自身类型识别（如 `.claude`、`.codex`，不限于这两个）：

1. 用户明确指定的参数
2. 当前目录配置：
   - `.<agent目录>/skills/git-worktree/git-worktree.config`
   - `.agents/skills/git-worktree/git-worktree.config`
3. 用户主目录配置：
   - `~/.<agent目录>/skills/git-worktree/git-worktree.config`
   - `~/.agents/skills/git-worktree/git-worktree.config`
4. Skill 默认配置（下表默认值）

配置文件为 JSON 结构，文件名为 `git-worktree.config`。

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `path` | worktree 存储路径，支持相对路径和绝对路径。相对路径基于 git 仓库根目录（`git rev-parse --show-toplevel`）解析，而非当前工作目录 | `.worktree` |
| `lan` | worktree 目录命名语言，`zh` 中文 / `en` 英文 | `zh` |

## 使用时机

用户要求新建 worktree 时触发。典型场景：

- 需要在新分支上并行开发，互不干扰主分支
- 需要同时处理多个任务的代码
- 临时验证某个方案，需要隔离环境

## 创建流程

用户要求新建 worktree 时，先在内部收集以下信息（不逐项询问用户），再一次性展示推荐方案供确认。

### 1. 收集信息

**worktree 存储路径 `path`**

- 用户明确指定了路径：直接使用
- 配置中存在有效 `path`：直接使用，不再生成路径选项
- 配置不存在或无值：推荐默认 `.worktree`（即仓库根目录下的 `.worktree/`）

**worktree 目录名称**

- 根据用户任务内容自动生成推荐名称
- 语言跟随 `lan` 配置：`zh` 中文名 / `en` 英文名
- 名称对应特定任务，每次创建独立命名，不持久化复用

**分支策略**（按顺序判定，命中即止）

1. 用户指定直接使用分支 X：解析 X（本地 → 远程 → 均无则报错请用户确认），直接在 X 上创建 worktree
2. 用户指定基础分支 X 新建分支：解析 X（本地 → 远程 → 报错），新分支名自动生成
3. 用户未指定任何分支：基础分支取仓库默认分支——优先 `git symbolic-ref --short refs/remotes/origin/HEAD` 探测，失败回退 `origin/master`；无 origin 远程则报错请用户指定

**分支解析规则**（三种情况通用）：X 在本地存在则用本地 X；仅存在于远程则用 `-b X ... origin/X` 建同名本地跟踪分支；均不存在则报错。

**新分支名生成规则**：根据任务内容生成英文 slug（小写字母、数字、`-` 连接）。分支名不受 `lan` 影响，`lan` 仅控制目录名语言。

### 2. 确认

向用户一次性展示推荐组合：存储路径、目录名、分支方案（新建分支名 + 基础分支，或使用的现有分支），等待用户确认或指出修改项。

### 3. 执行

```bash
# 新建分支（基础分支可为本地分支或 origin/xxx）
git worktree add -b <新分支名> <path>/<目录名> <基础分支>

# 使用现有分支
git worktree add <path>/<目录名> <本地分支名>
```

**执行注意事项**：

- **.gitignore**：创建前检查仓库根 `.gitignore` 是否忽略 worktree 目录（如 `/.worktree/`），没有则自动追加并告知用户
- **already checked out**：目标分支已被其他 worktree checkout 时 git 会拒绝，提示用户先 `git worktree list` 查看占用情况
- **目录已存在**：提示换目录名
- **`-b` 分支已存在**：提示改用"使用现有分支"或换分支名

### 4. 保存配置

- 仅当本次 `path` 或 `lan` 实际取值与默认值不同（用户覆盖了默认）时，询问是否保存；全程使用默认值则不问
- 只保存 `path`、`lan` 两个偏好字段，分支名等一次性参数不保存
- 默认写入项目级配置（当前目录优先级中的路径），不写用户主目录

## 其他操作

**列出**

```bash
git worktree list
```

**删除**

```bash
git worktree remove <worktree路径>          # 干净 worktree
git worktree remove --force <worktree路径>  # 有未提交改动，--force 前先向用户确认
git worktree prune                          # 清理失效的 worktree 记录
```

**切换**

worktree 是独立目录，直接 `cd` 到对应目录即可；各 worktree 分支独立，无需 checkout 切换。

## 目录结构

```
skills/git-worktree/
├── SKILL.md            # 本文件
├── references/         # 详细说明文档
└── scripts/            # 辅助脚本
```
