---
name: agent-install-location
description: "Agent 通用技能/工具安装位置决策:~/.agents 通用全局、项目 .agents、专用 agent 目录、Hermes 全局 skill 目录四路判断."
version: 1.0.0
author: Hermes Agent + xia
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agent, installation, skills, cross-agent]
    related_skills: [claude-code, opencode, codex]
---

# Agent 通用技能/工具安装位置决策

本 skill 用于判断一个通用型 AI agent 工具（或 skill）应该安装到哪里，以及如何在 Hermes 的 skill 体系里正确引用它。

> **核心结论**: 全局技能统一放 `~/.agents`，不兼容的 agent 用「先安装到专用全局目录 + 软链接复用」；特定 agent 的专属技能不进通用目录；项目通用放全局，项目特定放项目根 `~/<proj>/.agents/`。

---

## 1. 四路安装位置（判断顺序）

| # | 位置 | 适用场景 | 示例 |
|---|------|----------|------|
| **①** | **特定 coding agent 专属目录** | 该技能是某个 agent 的**专属技能**（只有该 agent 认识，不兼容通用约定） | Claude Code 的专属 workflow、Codex 专属 prompt |
| **②** | **项目根目录 `.agents/`** | 项目特定的 skill（如某个接口的测试约定、某项目编码规范） | `~/proj/.agents/api-test/` |
| **③** | **通用全局 `~/.agents/`** | 大多数 coding agent **直接兼容**、跨项目通用的技能 | Docker 规范、Compose 规范、通用工具封装 |
| **④** | **Hermes 全局 skill 目录** | 只给 Hermes 用的 skill（本 skill 就放在这里：`~/.hermes/skills/<cat>/<name>/SKILL.md`） | `~/.hermes/skills/autonomous-ai-agents/agent-install-location/` |

**决策流程（四问）：**

1. **是某个 agent 的专属技能吗？** → 是 → 走 **①**（直接装到该 agent 的全局/项目目录，不进 `~/.agents`）
2. **是项目特有的吗？** → 是 → 走 **②**（`<项目根>/.agents/`）
3. **是跨项目通用，且 agent 直接兼容 `.agents` 结构吗？** → 是 → 走 **③**（`~/.agents/<name>/`）
4. **只是给 Hermes 用、或 agent 不兼容 `.agents` 结构？** → 是 → 走 **④**

**默认降级**: 不确定时，优先 **③** `~/.agents`（约定优先）；只有确认为「专属技能」时才绕开。

---

## 2. `~/.agents` 目录约定

全局通用目录结构：

```text
~/.agents/                     # 全局通用技能/工具根目录
├── SKILL_INDEX.md            # （可选）索引
├── docker/                   # Docker/Compose 使用规范
│   └── SKILL.md
├── compose/
│   └── SKILL.md
└── <agent-name>/             # 不兼容目录约定、需软链接复用的 agent 专用包
    └── claude-code/
```

**兼容性说明**: 主流 coding agent（Claude Code、Codex、OpenCode 以及大多数基于 AGENTS.md/.hermes.md/.agents 约定的工具）可直接识别项目/全局 `/.agents` 目录下的技能文件。

---

## 3. 不兼容 agent 的「软链接复用」方案

对不直接支持 `~/.agents` 目录约定的 agent（如只认自己配置目录的），采用：

```bash
# 1) 先完整安装到该 agent 的专用全局目录
cp -r ~/.agents/cli-tool-name ~/.agents/<agent-name>/original-install/

# 2) 在通用目录打软链接，保持「单一来源」
ln -sfn ~/.agents/<agent-name>/original-install ~/.agents/cli-tool-name
```

这样 `~/.agents/<name>/` 仍是技能的唯一读写入口，agent 专用目录只读共享。

---

## 4. 全局 vs 项目：通用性判断

| 内容类型 | 存全局 | 存项目 |
|----------|--------|--------|
| 所有项目通用的操作手册 | ✅ `~/.agents/<name>/` 或 **Hermes 全局 skill** | ❌ |
| 某项目的特定接口测试流程 | ❌ | ✅ `~/proj/.agents/<name>/` |
| 某项目的专属编码规范 | ❌ | ✅ `~/proj/.agents/` |
| Hermes 专属的 skill（本 skill） | — | — | 统一存 `~/.hermes/skills/<cat>/<name>/` |

> **注意**: 跨项目通用技能应「存一处」，任何地方只需引用，避免多处副本导致维护漂移。

---

## 5. 本 skill 的位置与引用

- **Hermes 全局技能路径**: `~/.hermes/skills/autonomous-ai-agents/agent-install-location/SKILL.md`
- **加载方式**: 本技能随 Hermes 全局 skills 自动加载，会话内通过 `skill_view(name='agent-install-location')` 读取。
- **归属**: 本 skill 是 **Hermes 全局 skill**，不是通用 agent 技能，因此它本身存到 **④**，而非 `~/.agents`。

---

## 6. 维护

- 修改本 skill 后：`cd ~/.hermes/skills && git add . && git commit -m "..." && git push`
- 技能目录结构规范：`SKILL.md` 放叶节点，`references/`、`templates/`、`scripts/`、`assets/` 为可选子目录。

---

## 7. 常见问题

**Q: 怎么确认某个 agent 是否兼容 `~/.agents`？**

A: 查看该 agent 文档中「Project Context Files」部分（Claude Code / Codex / Hermes 均支持 `.agents`/`AGENTS.md` 类项目上下文约定）。若只认自身配置目录，走软链接方案。

**Q: 多个 agent 共用同一个技能时，用哪个目录？**

A: 若都兼容 `.agents` → `~/.agents/<name>/` 单一来源；若各自目录不互通 → 分别安装 + 软链接指向同一份源文件。