---
name: skill-config-standard
description: 创建 Skill 时管理固定配置变量的规范。当 Skill 需要用户提供固定配置（如路径、前缀等）时，应在此 Skill 中定义对应的 <skill>.config 文件，并遵循统一的配置查找优先级。
metadata:
  version: 20260921.210500
  update-url: https://github.com/bonaluo/agent-skills@skill-config-standard
---

# skill-config-standard

本技能规定了在开发其他 Skill 时，如何声明和使用固定配置变量（如路径、命名前缀、默认语言等）。当一个 Skill 需要从用户处获取固定配置（非敏感信息）时，应遵循本规范提供 `<skill>.config` 文件，并使用统一的配置查找顺序。

## 何时使用

- 当你编写的 Skill 需要用户在不同环境中提供固定值（例如：worktree 存储路径、模板目录、默认分支名称等）时。
- 配置项为非敏感信息（敏感信息请使用环境变量或 vault）。
- 需要在多个优先级间进行配置覆盖（明确指定 > 当前项目 > 用户全局 > 默认值）。

## 配置文件命名与位置

每个 Skill 若需要固定配置，应在其 Skill 目录下提供一个名为 `<skill-name>.config` 的 JSON 文件（例如 `git-worktree.config`）。该文件描述了该 Skill 的默认配置。

用户可以通过以下方式覆盖配置（优先级从高到低）：

1. **用户明确指定的参数**（在调用 Skill 时通过参数直接传入）
2. **当前工作目录中的配置**：
   - `.<当前Agent目录>/skills/<skill-name>/<skill-name>.config`
   - `.agents/skills/<skill-name>/<skill-name>.config`
3. **用户主目录中的配置**：
   - `~/.<当前Agent目录>/skills/<skill-name>/<skill-name>.config`
   - `~/.agents/skills/<skill-name>/<skill-name>.config`
4. **Skill 默认配置**（即 Skill 目录下的 `<skill-name>.config` 文件）

> 注意：`<当前Agent目录>` 指代当前运行的 Code Agent 目录名（如 `.claude`、`.pi` 等），若未检测到则回退到通用 `.agents` 目录。

## 配置项建议

- 所有配置项应为 JSON 键值对，值类型建议为字符串、数字或布尔值。
- 配置项应具备清晰的中文名称和英文别名（可选），并在 SKILL.md 中说明其用途。
- 建议在配置项名称上使用小写并采用下划线分隔（snake_case）。

## 示例：git-worktree.config

```json
{
    "path": ".agents/worktree",
    "lan": "zh"
}
```

| 键名 | 类型 | 说明 |
|------|------|------|
| `path` | string | worktree 目录存放的相对或绝对路径，默认 `.agents/worktree` |
| `lan`  | string | 目录命名语言，`zh` 中文 / `en` 英文，默认 `zh` |

## 在 Skill 中读取配置

Skill 内部应提供一个配置读取脚本（如 `scripts/config.py`），按照上述优先级加载并返回最终配置字典。参考 `git-worktree` Skill 的 `scripts/config.py` 实现方式。

## 创建流程

1. 在 Skill 目录下新建 `<skill-name>.config` 文件，写入默认配置。
2. 在 SKILL.md 中“配置优先级”章节说明配置项及其用途。
3. 提供配置读取脚本（可参考现有实现）。
4. 在 Skill 使用说明中引导用户如何通过环境变量、命令行参数或局部配置文件覆盖默认值。

## 关联技能

- `git-worktree`：本规范的参考实现，展示了如何在 Skill 中管理固定配置。
- `skill-creator`：创建新 Skill 时可参考本规范添加配置管理。
