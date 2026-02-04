---
name: know-your-env
description: 帮助agent了解当前系统环境的特殊配置和使用方式，包括PowerShell作为默认shell、conda管理的Python环境、podman作为首选容器工具等关键环境信息，避免因环境差异导致的执行错误。
---

# Know Your Environment Skill

## 概述
这个技能帮助agent了解当前系统环境的特殊配置和使用方式，避免因环境差异导致的错误。

## 环境信息

### Shell环境
- **默认Shell**: PowerShell (不是CMD)
- **重要提示**: 在PowerShell中，多个连续命令应使用`;`而不是`&&`来连接
- **正确示例**: `cd path; command1; command2`
- **错误示例**: `cd path && command1 && command2`

### Python环境
- **Python访问方式**: 系统没有直接可用的python命令
- **激活方式**: 必须先执行 `conda activate global` 来激活通用Python环境
- **使用流程**: 
  1. `conda activate global`
  2. 然后才能使用 `python` 命令

### 容器环境
- **优先容器命令**: podman (不是docker)
- **中间件部署**: MySQL等中间件使用podman部署
- **操作原则**: 当需要操作通过podman部署的服务时，必须使用podman命令
- **示例**: 
  - 启动MySQL: `podman start mysql-container`
  - 停止MySQL: `podman stop mysql-container`
  - 查看日志: `podman logs mysql-container`

## 使用指南

当agent需要执行以下操作时，应参考此技能：

1. **执行多命令序列**: 始终使用PowerShell语法（分号分隔）
2. **使用Python**: 先激活conda环境再执行python命令
3. **操作容器**: 优先使用podman而不是docker
4. **操作中间件**: 通过podman管理已部署的中间件服务

## 记忆要点

- 记住PowerShell是默认shell，不要假设是CMD
- 记住Python需要conda激活
- 记住podman是首选容器工具
- 避免重复犯相同的环境相关错误