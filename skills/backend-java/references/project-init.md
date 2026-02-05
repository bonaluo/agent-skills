# 项目初始化与选型

## 使用 Spring Initializr 创建项目

访问 https://start.spring.io/ 在线生成项目，或使用 IDE 内置的 Spring Initializr 功能。

## 项目选型讨论

在初始化项目前，需要与您确认以下技术选型：

### 1. 构建工具选择
- **Maven**（默认推荐）：社区生态完善，依赖管理成熟
- **Gradle**：构建速度更快，配置更灵活，Kotlin DSL 支持更好

### 2. JDK 版本
- **JDK 17**（LTS，推荐）：长期支持版本，稳定性好
- **JDK 21**（最新 LTS）：新特性更多，性能更好
- 其他版本（需要指定）

### 3. Spring Boot 版本
- **Spring Boot 3.x**（最新，推荐）：支持 JDK 17+，新特性
- **Spring Boot 2.7.x**：最后一个 2.x 系列，适合需要兼容旧系统的项目

### 4. 必选组件（默认包含）
- **Lombok**：简化实体类、DTO 等样板代码

### 5. 可选组件（根据项目需求选择）

**Web 相关：**
- Spring Web：RESTful API 开发基础
- Spring WebFlux：响应式编程支持
- Spring Security：认证授权

**数据持久化：**
- MyBatis / MyBatis-Plus：ORM 框架（推荐）
- JPA / Hibernate：另一种 ORM 选择
- 数据库驱动（MySQL、PostgreSQL、Oracle 等）

**开发工具：**
- Spring Boot DevTools：热部署
- Spring Boot Actuator：监控和管理
- Spring Boot Configuration Processor：配置提示

**测试相关：**
- Spring Boot Starter Test：测试支持
- JUnit 5：单元测试框架

**其他：**
- Redis：缓存
- Kafka / RabbitMQ：消息队列
- Elasticsearch：搜索

### 6. 项目元数据
- Group ID（如：com.example）
- Artifact ID（项目名称）
- Package Name（包名）
- 项目名称
- 项目描述

## 初始化流程

1. 确认以上选型选项
2. 使用 Spring Initializr 生成项目骨架
3. 导入到 IDE（IntelliJ IDEA / Eclipse / VSCode）
4. 配置 Maven/Gradle 镜像（推荐阿里云镜像加速）
5. 验证项目可以正常编译运行

## 后续配置建议

- 配置代码风格和格式化规则
- 配置 Git 忽略文件（.gitignore）
- 配置日志框架（Logback / Log4j2）
- 配置统一异常处理
- 配置跨域支持（如需要）
