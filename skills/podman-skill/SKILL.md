---
name: podman-skill
description: A skill for using podman containers locally. Use this skill when performing container-related operations. Podman can replace docker and does not require a daemon. / 这是一个本地使用 podman 容器的 skill，当使用容器相关的操作时可使用此技能。podman 可以替代 docker 使用，且无需守护进程。
metadata:
  version: 20260417.0000
  update-url: https://github.com/bonaluo/agent-skills@podman-skill
---

# podman-skill

这是一个本地使用 podman 容器的 skill，当使用容器相关的操作时可使用此技能。podman 可以替代 docker 使用，且无需守护进程。

## When to use

当你需要使用容器时，尤其是一个不需要持久化的中间件时（在没有绑定卷的情况下），如果本地没有符合要求的组件，你应该使用 podman 创建并使用中间件。

## Instructions

### 基础使用

1. **远程 Podman 连接（推荐）**
   - 优先使用名称为 `podman-remote-win` 的远程连接，使用 `-c` 参数指定：
   ```
   podman -c podman-remote-win ps
   podman -c podman-remote-win run -d --name redis redis:alpine
   ```

2. **本地连接（备用）**
   - 如果 `podman-remote-win` 连接不存在或出现报错、超时等情况，使用默认连接：
   ```
   podman ps
   podman run -d --name redis redis:alpine
   ```

### 常用命令

| 操作 | 命令示例 |
|------|----------|
| 查看运行中的容器 | `podman -c podman-remote-win ps` |
| 查看所有容器 | `podman -c podman-remote-win ps -a` |
| 停止容器 | `podman -c podman-remote-win stop <container_id>` |
| 删除容器 | `podman -c podman-remote-win rm <container_id>` |
| 查看镜像 | `podman -c podman-remote-win images` |
| 拉取镜像 | `podman -c podman-remote-win pull nginx:alpine` |
| 查看日志 | `podman -c podman-remote-win logs <container_id>` |
| 进入容器 | `podman -c podman-remote-win exec -it <container_id> sh` |

### 注意事项

- 非持久化场景使用容器：容器停止后数据会丢失，重要数据请挂载卷
- 使用 `-d` 参数让容器在后台运行
- 使用 `--name` 为容器指定名称便于管理
- 用完记得清理：停止并删除不再使用的容器

### 故障排除

1. **连接超时或失败**
   - 检查远程 Podman 服务是否运行
   - 尝试使用本地连接方式

2. **镜像拉取慢**
   - 配置国内镜像加速器
   ```bash
   podman -c podman-remote-win login registry.docker-cn.com
   ```
