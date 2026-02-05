# 容器化最佳实践

## 镜像构建

### 1. 使用多阶段构建
使用多阶段构建可以显著减小最终镜像体积，将构建环境和运行环境分离。

### 2. 选择合适的 JDK 镜像
- 开发环境：使用 `eclipse-temurin:17-jdk-alpine`（包含完整 JDK）
- 生产环境：使用 `eclipse-temurin:17-jre-alpine`（仅 JRE，体积更小）
- 避免使用 `-alpine` 镜像如果应用依赖 glibc（Alpine 使用 musl）

### 3. 优化构建缓存
- 先 COPY `pom.xml`，再 COPY 源码，利用 Docker 层缓存机制
- 避免频繁更改的文件放在 COPY 指令的前面

### 4. 使用 `.dockerignore`
排除不必要的文件可以减小构建上下文和镜像体积：
```
target/
.git/
.gitignore
*.md
.vscode/
.idea/
*.iml
*.log
node_modules/
```

## 安全性

### 1. 使用非 root 用户运行
- 在 Dockerfile 中创建专用用户运行应用
- 避免容器被攻破后获得主机 root 权限

### 2. 敏感信息管理
- 不要硬编码密码、密钥在 Dockerfile 或配置文件中
- 使用环境变量注入敏感信息
- 生产环境使用 Docker Secrets 或外部密钥管理服务
- 使用 `.env` 文件管理环境变量（不要提交到版本控制）

### 3. 最小化镜像体积
- 使用官方轻量镜像
- 删除不必要的软件包和文件
- 合并 RUN 指令减少镜像层数

## 配置管理

### 1. 环境变量配置
- 使用环境变量配置应用参数
- 区分不同环境（dev、test、prod）的配置
- 使用 Spring Profile 配合环境变量

### 2. 健康检查（Healthcheck）
- 配置 HTTP 端点健康检查
- 设置合理的检查间隔、超时时间和重试次数
- 确保应用就绪后才接受流量

### 3. 资源限制
- 配置 CPU 和内存限制
- 避免容器占用过多资源影响其他服务
- 根据应用实际需求设置合理的限制

## 持久化与网络

### 1. 数据持久化
- 使用 volumes 挂载持久化数据
- 避免将重要数据存储在容器层
- 生产环境使用外部数据库而非容器内数据库

### 2. 网络配置
- 使用自定义网络实现容器间通信
- 避免使用默认 bridge 网络
- 使用服务发现而非硬编码 IP 地址

## 生产环境注意事项

### 1. 日志管理
- 将日志输出到 stdout/stderr
- 使用日志驱动收集和管理日志
- 避免日志文件占用过多磁盘空间

### 2. 监控与告警
- 集成监控系统（Prometheus、Grafana）
- 配置告警规则
- 收集容器指标（CPU、内存、网络、磁盘）

### 3. 服务编排
- 生产环境使用 Kubernetes 或 Docker Swarm 进行编排
- 配置自动伸缩和负载均衡
- 实现滚动更新和回滚机制

### 4. 镜像标签管理
- 使用语义化版本标签
- 使用 `latest` 标签时要谨慎
- 保留历史版本便于回滚

## 常用命令

| 操作 | 命令 |
|------|------|
| 构建镜像 | `docker build -t your-image:tag .` |
| 运行容器 | `docker run -d -p 8080:8080 --name app your-image:tag` |
| 查看日志 | `docker logs -f app` |
| 进入容器 | `docker exec -it app sh` |
| 停止容器 | `docker stop app` |
| 查看镜像 | `docker images` |
| 删除镜像 | `docker rmi your-image:tag` |
