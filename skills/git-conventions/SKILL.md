---
name: git-conventions
description: Use when creating git commits or reviewing commit history
---

# Git 提交规范

## 核心原则

**所有提交必须带类型前缀。** 无前缀的提交信息违反本规范。

## 提交信息格式

```
<type>: <简短描述>

[可选正文]

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

## 类型前缀

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加文件预览接口` |
| `fix` | 修复 bug | `fix: 修复进度条卡住问题` |
| `docs` | 文档变更 | `docs: 更新 API 文档` |
| `style` | 代码格式（不影响功能） | `style: 格式化代码风格` |
| `refactor` | 重构（不修复不改功能） | `refactor: 提取扫描服务逻辑` |
| `perf` | 性能优化 | `perf: 优化哈希计算速度` |
| `test` | 测试相关 | `test: 添加单元测试` |
| `chore` | 构建/工具/依赖更新 | `chore: 更新依赖版本` |
| `ci` | CI 配置 | `ci: 添加 GitHub Actions` |
| `build` | 构建系统变更 | `build: 迁移到 Maven` |
| `revert` | 回退提交 | `revert: 回退 xxx 提交` |

## 描述规则

- 使用中文，简洁明了
- 以动词开头（如"添加"、"修复"、"优化"）
- 不超过 72 字符
- 不使用句号结尾

## 正文规则

- 解释 **why** 而非 **what**
- 每行不超过 72 字符
- 使用 `-` 或 `*` 列举要点

## 常见错误

| 错误写法 | 正确写法 |
|----------|----------|
| `添加了登录功能` | `feat: 添加登录功能` |
| `fix bug` | `fix: 修复登录验证失败问题` |
| `更新 README` | `docs: 更新 README 使用说明` |
| `提交代码` | `feat: 实现用户认证模块` |

## 多文件变更

如果一次提交包含多个类型，以主要类型为准：
- 新功能 + 重构 → `feat`
- 修复 bug + 重构 → `fix`
- 多个同等重要变更 → `chore`

## 提交前检查

1. `git diff --cached` 确认变更内容
2. 确认变更与提交信息匹配
3. 确认有类型前缀
4. `git log --oneline -3` 验证提交历史
