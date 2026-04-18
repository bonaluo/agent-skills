---
name: skill-user-habits
description: Manages personal skill creation, installation, updating and usage conventions. Triggers when creating, installing, updating, or using skills. Covers version management, metadata specs, directory structure, and symlink management. / 管理个人 skill 的创建、安装、更新、使用规范。当需要创建新 skill、修改 skill、更新 skill 或使用 skill 时触发此技能。包含版本号管理、元数据规范、目录结构和软链接管理。
metadata:
  version: 20260418.1827
  update-url: https://github.com/bonaluo/agent-skills@skill-user-habits
---

# 个人 Skill 使用习惯

## 元数据规范

所有 skill 必须包含以下元数据字段：

```yaml
metadata:
  version: yyyymmdd.hhmm  # 例如 20260417.0236，每次修改必须更新
  update-url: https://github.com/用户名/仓库名@skill名称
```

**description 格式说明**（必须使用中英双语）：
- 使用 `/` 分隔中英文内容，格式为：`英文描述 / 中文描述`
- 英文部分在前，中文部分在后
- 两个部分都应该完整表达该 skill 的功能

**version 格式说明**：`yyyymmdd.hhmm`，如 `20260417.0236` 表示 2026年4月17日 02:36 创建/更新。

> **强制要求**：任何对 skill 文件的修改（创建、更新、修改内容），在完成修改后**必须立即**更新该 skill 的 `metadata.version`。Version 是判断 skill 是否需要更新的唯一依据，未及时更新会导致其他用户使用过时版本。

**获取 version**（每次修改前执行）：

先判断当前 shell 环境类型，执行下面的命令如果输出bash、sh、zsh等内容说明是linux环境，如果命令行的前缀包含ps则说明是powershell环境

```bash
# 判断方法
echo $0
```

根据不同的环境执行不同的命令获取当前时间：

```bash
# Linux/macOS (bash/zsh)
date "+%Y%m%d.%H%M"
```

```powershell
# PowerShell
Get-Date -Format "yyyyMMdd.HHmm"
```

> **Windows CMD 用户**：CMD 获取带前导零的时间较为繁琐，建议打开 PowerShell 执行上述命令。

**update-url 格式说明**：从 git 仓库地址推导。
- 仓库地址：`git@github.com:bonaluo/agent-skills.git`
- Skill 名称：`demo-skill`
- 更新地址：`https://github.com/bonaluo/agent-skills@demo-skill`

---

## 创建 Skill

### 确定创建目录

1. 检查 `~/.config/skill.env` 文件是否存在
2. 如果存在，读取 `default-skill-dir` 值作为默认目录
3. 如果不存在，询问用户默认创建位置，并创建该文件存储路径
4. 如果用户指定了目录，优先使用用户指定的目录

### 初始化步骤

1. 在目标目录下创建 skill 目录（如 `skills/demo-skill/`）
2. **自动获取当前版本号**：根据 shell 类型执行对应命令（见上方"自动获取版本号"）
3. 创建 `SKILL.md`，包含完整的 YAML frontmatter（name、description、metadata）
4. 根据需要添加 `references/`、`scripts/`、`assets/` 子目录

---

## 安装 Skill

### 安装目录级别

支持两级安装目录（按优先级从高到低）：
1. **项目目录**：`./.agents/skills/<skill-name>/`
2. **用户目录**：`~/.agents/skills/<skill-name>/`

### 安装流程

1. **必须获得用户确认**后才能安装
2. 将 skill 内容复制到目标目录
3. 根据当前智能体环境创建软链接：
   - **Claude Code + 用户目录** → 创建 `~/.claude/skills/<skill-name>` 指向 `~/.agents/skills/<skill-name>`
   - **Claude Code + 项目目录** → 创建 `~/.claude/skills/<skill-name>` 指向 `./.agents/skills/<skill-name>`

### 软链接命令（Windows）

```bash
# 用户目录安装
mklink /D "%USERPROFILE%\.claude\skills\<skill-name>" "%USERPROFILE%\.agents\skills\<skill-name>"

# 项目目录安装
mklink /D "%USERPROFILE%\.claude\skills\<skill-name>" "h:\note\agent-skills\.agents\skills\<skill-name>"
```

---

## 使用 Skill

### 启动前更新检查

**重要**：使用任何 skill 前，必须检查并执行更新（两个条件缺一不可）：

1. **读取 skill 的 `metadata.version` 字段**
2. **读取 skill 的 `metadata.update-url` 字段**

**更新条件**：只有同时满足以下情况才执行更新：
- `metadata.version` 字段存在且非空
- `metadata.update-url` 字段存在且非空

**跳过更新**：缺少 `metadata.version` 或 `metadata.update-url` 时跳过更新检查。

### 更新执行

根据 `update-url` 从 GitHub 获取最新版本并替换本地文件。

**更新命令**（两种方式等价，后者是前者的简化版）：

```bash
# 完整形式
npx skills add https://github.com/bonaluo/agent-skills.git -s <skill-name>

# 简化形式（GitHub 仓库可用）
npx skills add bonaluo/agent-skills@<skill-name>
```

**简化版规则**：当 skill 仓库托管在 GitHub 时，`https://github.com/用户名/仓库名@skill名` 可简化为 `用户名/仓库名@skill名`。

---

## 禁止行为

**不要自动打包 skill**：修改 skill 后，**禁止**执行 `python .agents/skills/skill-creator/scripts/package_skill.py` 打包命令。只有在用户明确要求时才进行打包操作。

> **原因**：打包会生成 `.skill` 文件，容易与 git 追踪的文件混淆。每次修改后只需更新 `metadata.version` 即可。

---

## 示例

### 新建 skill 时的元数据

```yaml
---
name: my-new-skill
description: This is a new skill description. / 这是一个新 skill 的描述
metadata:
  version: 20260417.0300
  update-url: https://github.com/bonaluo/agent-skills@my-new-skill
---
```

### 安装确认提示

```
我将为你安装 skill：
- 名称：demo-skill
- 来源：h:\note\agent-skills\skills\demo-skill\
- 目标目录：~/.agents/skills/
- 软链接：~/.claude/skills/demo-skill

是否确认安装？(y/n)
```
