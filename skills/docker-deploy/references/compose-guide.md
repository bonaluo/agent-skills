# Compose 文件编写参考

## 生产环境 compose（docker-compose.yml）

特点：拉取云端镜像，容器名固定，配置简单。

```yaml
services:
  backend:
    image: ${BACKEND_IMAGE:-registry/app-backend}:${TAG:-latest}
    container_name: app-backend
    network_mode: bridge
    volumes:
      - ${DATA_DIR:-./data}:/data
    ports:
      - "${BACKEND_PORT:-9092}:9092"
    environment:
      - TZ=Asia/Shanghai
    restart: unless-stopped

  frontend:
    image: ${FRONTEND_IMAGE:-registry/app-frontend}:${TAG:-latest}
    container_name: app-frontend
    network_mode: bridge
    ports:
      - "${FRONTEND_PORT:-9000}:9000"
    environment:
      - PORT=9000
    restart: unless-stopped
    depends_on:
      - backend
```

## 开发环境 compose（docker-compose.dev.yml）

特点：本地构建镜像，容器名可配置，端口 +1。

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      args:
        GO_IMAGE: ${GO_IMAGE:-golang:1.25-alpine}
        GIT_COMMIT: ${GIT_COMMIT:-unknown}
        VERSION: ${VERSION:-unknown}
        SINGBOX_IMAGE: ${SINGBOX_IMAGE:-ghcr.io/.../sing-box:v1.13}
    image: ${BACKEND_IMAGE:-app-backend}:${BUILD_DATE:-local}
    container_name: ${BACKEND_CONTAINER:-app-backend-dev}
    network_mode: bridge
    volumes:
      - ${DATA_DIR:-./data}:/data
    ports:
      - "${BACKEND_PORT:-9093}:9092"
    environment:
      - TZ=Asia/Shanghai
    restart: unless-stopped
```

## 变量约定

生产与开发使用不同 env 文件，共用同一个 compose 变量名体系：

| 变量 | 生产默认值 | 开发默认值 |
|------|-----------|-----------|
| `BACKEND_IMAGE` | `registry/app-backend` | `app-backend` |
| `TAG` / `BUILD_DATE` | `latest` | `26.07.04.22.30` |
| `BACKEND_PORT` | `9092` | `9093` |
| `COMPOSE_PROJECT_NAME` | 目录名 | `app-dev` |
| `BACKEND_CONTAINER` | `app-backend` | `app-backend-dev` |

## 注意事项

1. **container_name 变量化** — `${BACKEND_CONTAINER:-default}` 让容器名可在 env 中覆盖
2. **image 用 BUILD_DATE 而非 TAG** — 开发环境用构建日期做镜像 tag，区分不同构建版本
3. **depends_on 只保证启动顺序** — 不保证服务就绪，需要健康检查需额外配置
4. **extra_hosts** — 开发时可添加内网 DNS 解析
