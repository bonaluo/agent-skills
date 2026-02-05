---
name: backend-java
description: 这是开发 Java 后端服务时使用的 skill。包含项目初始化与选型、项目结构设计、MyBatis ORM 最佳实践、容器化部署等完整技能集。使用 Java/Spring 技术栈开发后端服务时优先使用此技能。
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

## 相关技能

- [项目初始化](references/project-init.md) - 使用 Spring Initializr 创建项目并进行技术选型
- [项目结构](references/project-structure.md) - 标准 Maven 项目结构和分层架构
- [MyBatis 最佳实践](references/database-config.md) - ORM 框架使用规范和优化技巧
- [容器化最佳实践](references/containerization.md) - Docker 镜像构建和容器部署指南
