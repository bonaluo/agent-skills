---
name: git-conventions
description: Use when creating git commits or reviewing commit history. / 使用此技能进行 Git 提交创建或提交历史审查。
metadata:
  version: 20260419.1606
  update-url: https://github.com/bonaluo/agent-skills@git-conventions
---

# Git 提交规范

## 核心原则

1. **提交信息必须遵循指定的格式** — 使用统一格式确保可读性和可追溯性
2. **提交前应该逐个检查提交的内容** — 确保只提交本次会话相关的变更

---

## 一、提交信息格式

### 格式说明

```
<type>: <简短描述>

<正文内容，每行以 - 开头>
```

**注意**：
- 标题行和正文之间必须隔一行
- 正文每行必须以 `-` 开头

### 示例

```
feat: 添加用户登录功能

- 实现用户名密码认证
- 添加 Token 刷新机制
- 集成现有用户表结构
```

### 类型前缀

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

### 标题规则

- 使用中文，简洁明了
- 以动词开头（如"添加"、"修复"、"优化"）
- 不超过 72 字符
- 不使用句号结尾

#### 必须明确修改主体

**标题中必须明确指出修改的主体（文件、类、skill 名称等），让读者一眼就知道本次提交修改了什么。**

| 错误写法 | 正确写法 |
|----------|----------|
| `fix: 将修改skill必须更新version规范移至元数据规范部分` | `fix: 修改skill-user-habits将必须更新version规范移至元数据规范部分` |
| `docs: description 增加修改、更新 skill 触发条件` | `docs: 优化skill-user-habits description 增加修改、更新 skill 触发条件` |
| `feat: 增加用户管理模块` | `feat: 新增UserService类实现用户管理模块` |

#### 禁止模糊描述

禁止使用"增加xxx字段"、"修改xxx属性"等模糊描述，必须明确指出被修改的具体目标：

| 禁止写法 | 正确写法 |
|----------|----------|
| `增加状态字段` | `User类增加status字段` |
| `修改配置` | `config.json增加retryTimes配置` |
| `优化文档` | `README.md优化安装步骤说明` |
| `更新依赖` | `package.json更新vue版本至3.4` |

### 正文规则

- 解释 **why** 而非 **what**
- 每行不超过 72 字符
- 使用 `-` 或 `*` 列举要点

#### 多文件变更

如果一次提交包含多个类型，以主要类型为准：
- 新功能 + 重构 → `feat`
- 修复 bug + 重构 → `fix`
- 多个同等重要变更 → `chore`

### 常见错误

| 错误写法 | 正确写法 |
|----------|----------|
| `添加了登录功能` | `feat: 添加登录功能` |
| `fix bug` | `fix: 修复登录验证失败问题` |
| `更新 README` | `docs: 更新 README 使用说明` |
| `提交代码` | `feat: 实现用户认证模块` |

---

## 二、分阶段检查

### 阶段一：暂存文件检查

**禁止使用 `git add -A` 或 `git add .` 全量提交。** 必须精确指定本次会话修改的文件。

#### 操作步骤

1. 使用 `git status` 查看所有变更
2. 仅将本次会话相关的文件加入暂存区：
   ```bash
   git add <文件1> <文件2>
   ```
3. 使用 `git diff --cached` 确认暂存内容
4. 确认暂存区中没有混入其他无关变更

#### 判断标准

如果一个文件：
- 不是本次会话创建或修改的
- 不是本次重构必需变更的（如格式化、迁移）

则不应提交。

#### 示例

```bash
# 正确做法
git add src/auth/login.ts tests/auth.test.ts
git commit -m "feat: 添加用户登录功能"

# 错误做法
git add -A  # 会混入无关文件
git add .   # 会混入无关文件
```

### 阶段二：提交前检查

1. `git status` 确认暂存的文件都是本次会话相关
2. `git diff --cached` 确认变更内容
3. 确认变更与提交信息匹配
4. 确认有类型前缀
5. `git log --oneline -3` 验证提交历史
