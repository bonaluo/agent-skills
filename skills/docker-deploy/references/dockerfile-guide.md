# Dockerfile 编写参考

## 多阶段构建（Multi-stage Build）

```
阶段1 (builder): 编译代码，包含 SDK/依赖 → 产物体积大
阶段2 (runtime): 仅包含运行时依赖 + 编译产物 → 产物体积小
```

### Go 后端示例

```dockerfile
# === 构建参数（必须在 FROM 之前声明）===
ARG GO_IMAGE=golang:1.25-alpine
ARG SINGBOX_IMAGE=ghcr.io/sagernet/sing-box:v1.13.12
ARG GIT_COMMIT=unknown
ARG VERSION=unknown

# === 阶段一：编译 ===
FROM ${GO_IMAGE} AS builder
ARG GIT_COMMIT
ARG VERSION
WORKDIR /app
COPY go.mod main.go ./
COPY config/ config/
COPY handlers/ handlers/
COPY models/ models/
COPY services/ services/

# 通过 ldflags 注入版本信息
RUN CGO_ENABLED=0 go build \
  -ldflags="-X 'config.GitCommit=${GIT_COMMIT}' -X 'config.Version=${VERSION}'" \
  -o app .

# === 阶段二：运行 ===
FROM ${SINGBOX_IMAGE}
# 国内镜像源加速
RUN sed -i 's|dl-cdn.alpinelinux.org|mirrors.aliyun.com|g' /etc/apk/repositories \
  && apk add --no-cache curl
COPY --from=builder /app/app /usr/local/bin/
CMD ["app"]
```

### Node.js 前端示例

```dockerfile
ARG NODE_IMAGE=node:22-alpine
ARG NPM_REGISTRY=https://registry.npmjs.org

FROM ${NODE_IMAGE} AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install --registry ${NPM_REGISTRY}
COPY . .
RUN npm run build

FROM ${NODE_IMAGE}
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 9000
CMD ["node", "server.js"]
```

## ARG 作用域陷阱

```dockerfile
# ✅ 正确：FROM 中使用的 ARG 必须在 FROM 之前声明
ARG IMAGE=alpine:latest
FROM ${IMAGE}          # OK

# ❌ 错误：ARG 在 FROM 之后声明，FROM 中不可用
FROM builder AS stage1
ARG IMAGE=alpine:latest
FROM ${IMAGE}          # 报错 — base name should not be blank
```

ARG 规则：
- 全局 ARG（FROM 之前）：可在 FROM 行中使用，不可在 stage 内使用
- Stage ARG（FROM 之后）：仅在当前 stage 内可用，如需复用须重新声明

## 最佳实践

1. **FROM 镜像全部 ARG 化** — 方便切换国内镜像源
2. **ldflags 注入元数据** — 版本号、commit hash 编入二进制
3. **COPY 分层** — 先 copy 依赖文件（go.mod/package.json），再 copy 源码，利用 Docker 层缓存
4. **.dockerignore** — 排除 node_modules、.git、日志等无关文件
5. **alpine 换源** — 国内构建时替换 apk 源为阿里云镜像
