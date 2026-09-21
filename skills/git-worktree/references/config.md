# worktree.config 说明

worktree 配置用于控制 worktree 创建时的默认行为。

## 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `path` | string | worktree 目录存储路径，支持相对路径和绝对路径。相对路径基于 git 仓库根目录。默认 `.agents/worktree` |
| `lan` | string | worktree 目录名称的默认语言。`zh` 为中文，`en` 为英文。默认 `zh` |

## 示例

```json
{
    "path": "./.agents/worktree",
    "lan": "zh"
}
```

## 放置位置

按优先级查找：

1. 当前工作目录 `.agents/git/worktree.config`
2. 用户目录 `~/.agents/git/worktree.config`
