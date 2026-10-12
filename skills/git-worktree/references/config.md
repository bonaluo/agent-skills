# worktree.config 说明

worktree 配置用于控制 worktree 创建时的默认行为。

## 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `path` | string | worktree 目录存储路径，支持相对路径和绝对路径。相对路径基于 git 仓库根目录解析。默认 `.worktree` |
| `lan` | string | worktree 目录名称的默认语言。`zh` 为中文，`en` 为英文。默认 `zh`。仅影响目录名；分支名始终为英文 slug，不受 `lan` 控制 |

## 示例

```json
{
    "path": ".worktree",
    "lan": "zh"
}
```

## 放置位置

按优先级查找（越靠前优先级越高）。每一级内部，当前 agent 类型目录优先，其次为通用 `.agents` 目录（`<agent目录>` 由 agent 根据自身类型识别，如 `.claude`）：

1. 当前工作目录：
   - `.<agent目录>/skills/git-worktree/git-worktree.config`
   - `.agents/skills/git-worktree/git-worktree.config`
2. 用户主目录：
   - `~/.<agent目录>/skills/git-worktree/git-worktree.config`
   - `~/.agents/skills/git-worktree/git-worktree.config`

## 保存行为

创建 worktree 结束时，若本次 `path` 或 `lan` 实际取值与默认值不同，可询问用户是否保存；默认写入项目级路径（当前工作目录下的优先级路径），不写用户主目录。
