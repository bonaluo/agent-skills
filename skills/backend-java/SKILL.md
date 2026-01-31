---
name: backend-java
description: 这是开发 Java 后端服务时使用的 skill。使用 Java/Spring 技术栈开发后端服务时优先使用此技能。
---

# backend-java

这是开发 Java 后端服务时使用的 skill。推荐使用 Spring 生态 + Maven 构建 + MySQL 数据库 + MyBatis ORM 的技术组合。

## When to use

当需要开发 Java 后端服务时，包括：
- 创建新的 Spring Boot 应用
- 开发 RESTful API
- 数据库 CURD 操作
- 后端微服务开发

## 技术栈偏好

| 场景 | 推荐选项 |
|------|----------|
| 构建工具 | Maven（优先于 Gradle） |
| 框架 | Spring Boot / Spring Cloud |
| 数据库 | MySQL（优先于 PostgreSQL、Oracle） |
| ORM 框架 | MyBatis / MyBatis-Plus（优先于 JPA） |
| 包管理 | Maven Central / 阿里云镜像 |
| Java 版本 | JDK 17+（LTS 版本） |

## Instructions

### 项目初始化

**使用 Spring Initializr 创建项目：**
```bash
# 使用 Maven 构建
mvn spring-boot:start
# 或手动创建 pom.xml 后导入 IDE
```

**推荐的依赖（pom.xml 示例）：**
```xml
<dependencies>
    <!-- Spring Boot Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- MyBatis -->
    <dependency>
        <groupId>org.mybatis.spring.boot</groupId>
        <artifactId>mybatis-spring-boot-starter</artifactId>
        <version>3.0.3</version>
    </dependency>

    <!-- MySQL Driver -->
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- Lombok（简化代码） -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
```

### 常用 Maven 命令

| 操作 | 命令 |
|------|------|
| 编译项目 | `mvn clean compile` |
| 运行测试 | `mvn test` |
| 打包 | `mvn clean package -DskipTests` |
| 运行应用 | `mvn spring-boot:run` |
| 安装依赖 | `mvn clean install` |
| 查看依赖树 | `mvn dependency:tree` |

### 项目结构

```
src/main/java/com/example/
├── Application.java          # 启动类
├── controller/               # REST 控制器
├── service/                  # 业务逻辑层
├── mapper/                   # MyBatis Mapper
├── entity/                   # 实体类
├── dto/                      # 数据传输对象
└── config/                   # 配置类
```

### 数据库配置（application.yml）

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/your_db?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: your_password

mybatis:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: com.example.entity
```

## 注意事项

- 使用阿里云 Maven 镜像加速依赖下载
- 遵循 Spring Boot 约定大于配置的原则
- MyBatis 使用 XML 映射文件时放在 `resources/mapper/` 目录
- 使用 Lombok 减少样板代码
- 配置文件中敏感信息使用环境变量或外部配置管理
