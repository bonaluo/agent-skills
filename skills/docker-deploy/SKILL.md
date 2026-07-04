---
name: docker-deploy
description: Docker 标准化构建部署流程。涵盖 Dockerfile、Compose 文件、env 环境变量、多环境隔离、构建脚本的一整套规范。当用户需要构建 Docker 镜像、编写 Compose 文件、配置多环境部署时使用此技能。
metadata:
  version: 20260704.0000
  update-url: https://github.com/bonaluo/agent-skills@docker-deploy
---

# docker-deploy

Docker 标准化构建部署流程。从 Dockerfile 到 Compose 到 env 到构建脚本的完整链路。

## 标准化流程

```
Dockerfile → docker-compose.yml → .env 变量 → build.sh 构建脚本 → 多环境部署
```

### 1. Dockerfile — 多阶段构建

原则：编译阶段和运行阶段分离，基础镜像通过 ARG 参数化，方便切换镜像源。

```dockerfile
# 构建参数全部前置声明
ARG GO_IMAGE=golang:1.25-alpine
ARG RUNTIME_IMAGE=alpine:latest
ARG GIT_COMMIT=unknown
ARG VERSION=unknown

FROM ${GO_IMAGE} AS builder
WORKDIR /app
COPY . .
RUN go build -ldflags="-X 'main.Version=${VERSION}' -X 'main.Commit=${GIT_COMMIT}'" -o app .

FROM ${RUNTIME_IMAGE}
COPY --from=builder /app/app /usr/local/bin/
CMD ["app"]
```

要点：
- ARG 声明在 FROM 之前才能在 FROM 行中使用
- 构建信息（版本、commit）通过 ldflags 注入二进制
- FROM 镜像全部参数化，方便国内镜像源替换

### 2. docker-compose.yml — 服务编排

分两套文件：生产环境 `docker-compose.yml`（拉云端镜像），开发环境 `docker-compose.dev.yml`（本地构建）。

**生产 compose：**

```yaml
services:
  backend:
    image: ${BACKEND_IMAGE:-app-backend}:${TAG:-latest}
    container_name: app-backend
    network_mode: bridge
    volumes:
      - ${DATA_DIR:-./data}:/data
    ports:
      - "${BACKEND_PORT:-9092}:9092"
    environment:
      - TZ=Asia/Shanghai
    restart: unless-stopped
```

**开发 compose：**

```yaml
services:
  backend:
    build:
      context: ./backend
      args:
        GIT_COMMIT: ${GIT_COMMIT:-unknown}
        VERSION: ${VERSION:-unknown}
    image: ${BACKEND_IMAGE:-app-backend}:${BUILD_DATE:-local}
    container_name: ${BACKEND_CONTAINER:-app-backend-dev}
    network_mode: bridge
    volumes:
      - ${DATA_DIR:-./data}:/data
    ports:
      - "${BACKEND_PORT:-9092}:9092"
    restart: unless-stopped
```

生产与开发差异：
- 生产用 `image` 拉云端镜像，开发用 `build` 本地构建
- 开发容器名加 `-dev` 后缀，端口 +1 避免冲突
- 开发镜像 tag 用构建日期（`BUILD_DATE`），生产用 `latest`

### 3. .env 文件 — 环境变量分层

三层 env 文件：
- `.env` — 生产环境（gitignore，不提交）
- `.env.dev` — 开发环境（gitignore，不提交）
- `.env.example` — 示例文件（提交到仓库）

**生产 `.env`：**

```bash
DATA_DIR=/path/to/data
BACKEND_IMAGE=registry/app-backend
TAG=latest
BACKEND_PORT=9092
```

**开发 `.env.dev`：**

```bash
COMPOSE_PROJECT_NAME=app-dev        # 独立项目名，隔离正式环境
DATA_DIR=./data
BACKEND_CONTAINER=app-backend-dev
BACKEND_IMAGE=app-backend
GO_IMAGE=mirror/.../golang:1.25-alpine
SINGBOX_IMAGE=ghcr.io/.../sing-box:v1.13.12
BACKEND_PORT=9093                   # +1 避免冲突
```

**示例文件 `.env.example`：**

```bash
# 复制为 .env.dev 后按需修改
# TAG/BUILD_DATE 由 build.sh 自动生成，无需在此配置
COMPOSE_PROJECT_NAME=app-dev
DATA_DIR=./data
BACKEND_CONTAINER=app-backend-dev
# BACKEND_PORT=9093
```

要点：
- 示例文件中值用注释形式，让用户自行决定是否覆盖默认值
- 构建参数（GO_IMAGE 等）与运行参数（端口等）分离
- 变量名统一大写+下划线

### 4. build.sh — 构建入口脚本

开发环境通过脚本统一入口，禁止直接执行 `docker compose` 命令。

```bash
#!/bin/bash
set -e
BUILD_DATE=$(TZ=Asia/Shanghai date +%y.%m.%d.%H.%M)
GIT_COMMIT=$(git rev-parse --short HEAD)
VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo 'unknown')
VERSION=${VERSION}-${BUILD_DATE}
BUILD_DATE=$BUILD_DATE GIT_COMMIT=$GIT_COMMIT VERSION=$VERSION \
  docker compose -f docker-compose.dev.yml --env-file .env.dev up -d --build
```

要点：
- 动态值（日期、commit、version）在脚本中生成，不放入 env 文件
- 使用行内环境变量（`VAR=val cmd`）传入 compose，不 export 污染全局
- `--env-file` 指定配置文件，`-f` 指定 compose 文件
- `VERSION` 拼接 git tag + 构建日期，左下角一眼看出是否新代码

### 5. 多环境隔离

核心：通过 `COMPOSE_PROJECT_NAME` 隔离不同环境。

| | 正式环境 | 开发环境 |
|---|---|---|
| 项目名 | `app`（默认） | `app-dev` |
| 容器名 | `app-backend` | `app-backend-dev` |
| 端口 | 9000 / 9092 | 9001 / 9093 |
| 镜像 | 云端 `registry/app:latest` | 本地构建 `app:26.07.04.22.30` |
| 启动 | `docker compose up -d` | `./build.sh` |
| env | `.env` | `--env-file .env.dev` |

如果不用 `COMPOSE_PROJECT_NAME`，两个 compose 共享项目名，`docker compose -f docker-compose.yml up` 会误操作开发容器。

### 6. .gitignore 配置

```gitignore
.env
.env.dev
data/
.claude/
```

- 含密钥的 env 文件不提交
- 数据目录不提交
- 示例 `.env.example` 提交到仓库

### 7. 常用 Docker 命令速查

| 操作 | 命令 |
|------|------|
| 构建并启动（生产） | `docker compose up -d` |
| 构建并启动（开发） | `./build.sh` |
| 查看日志 | `docker compose logs -f` |
| 停止 | `docker compose down` |
| 重载配置 | `docker compose restart` |
| 进容器 | `docker exec -it <name> sh` |
| 清理所有 | `docker compose down -v` |
| 查看资源 | `docker stats` |
| 查看项目容器 | `docker compose -p <project> ps` |
