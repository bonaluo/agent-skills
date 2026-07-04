# .env 环境变量分层参考

## 三层结构

```
.env            # 生产环境 — 不提交
.env.dev        # 开发环境 — 不提交
.env.example    # 示例模板 — 提 交
```

## .env（生产环境）

```bash
# 数据目录（独立持久化路径）
DATA_DIR=/path/to/production/data

# 镜像配置（从云端仓库拉取）
BACKEND_IMAGE=registry/app-backend
FRONTEND_IMAGE=registry/app-frontend
TAG=latest

# 端口配置
FRONTEND_PORT=9000
BACKEND_PORT=9092
```

生产环境不需要构建参数（GO_IMAGE、NPM_REGISTRY 等），只定义运行时变量。

## .env.dev（开发环境）

```bash
# 独立项目名 — 关键！避免与生产容器冲突
COMPOSE_PROJECT_NAME=app-dev

# 数据目录（本地测试数据）
DATA_DIR=./data

# 容器名称（-dev 后缀）
BACKEND_CONTAINER=app-backend-dev
FRONTEND_CONTAINER=app-frontend-dev

# 镜像配置（本地构建）
BACKEND_IMAGE=app-backend
FRONTEND_IMAGE=app-frontend

# 构建参数（国内镜像加速）
GO_IMAGE=docker.m.daocloud.io/library/golang:1.25-alpine
NODE_IMAGE=docker.m.daocloud.io/library/node:22-alpine
NPM_REGISTRY=https://registry.npmmirror.com
SINGBOX_IMAGE=ghcr.io/sagernet/sing-box:v1.13.12

# 端口（正式环境 +1 避免冲突）
FRONTEND_PORT=9001
BACKEND_PORT=9093
```

## .env.example（参考模板）

示例文件全部值以注释形式提供，用户自行取消注释：

```bash
# 复制为 .env.dev 后按需修改
# BUILD_DATE 由 build.sh 自动生成

# 项目名（dev 独立项目）
COMPOSE_PROJECT_NAME=app-dev

# 数据目录
DATA_DIR=./data

# 容器名称
# BACKEND_CONTAINER=app-backend-dev
# FRONTEND_CONTAINER=app-frontend-dev

# 构建参数
# GO_IMAGE=docker.m.daocloud.io/library/golang:1.25-alpine
# NODE_IMAGE=docker.m.daocloud.io/library/node:22-alpine
# NPM_REGISTRY=https://registry.npmmirror.com
# SINGBOX_IMAGE=ghcr.io/sagernet/sing-box:v1.13.12

# 端口（正式环境 +1）
# FRONTEND_PORT=9001
# BACKEND_PORT=9093
```

## 设计原则

1. **敏感信息不进仓库** — `.env` 和 `.env.dev` 在 `.gitignore` 中
2. **默认值在 compose 文件中** — `${VAR:-default}` 保证缺失变量不报错
3. **动态值在脚本中** — BUILD_DATE、GIT_COMMIT 等动态值由 build.sh 生成
4. **静态值在 env 中** — 端口、镜像源、容器名等可配置静态值放到 env
5. **example 用注释** — 让用户主动选择开启，避免无脑复制

## 变量命名规范

- 全大写 + 下划线：`BACKEND_PORT`、`DATA_DIR`
- 模块前缀：`BACKEND_`、`FRONTEND_`、`SINGBOX_`
- 布尔值用 `true`/`false` 字符串
