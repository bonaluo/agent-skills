# 项目结构

## 标准 Maven 项目结构

```
your-project/
├── pom.xml                          # Maven 配置文件
├── src/
│   ├── main/
│   │   ├── java/com/example/       # Java 源代码
│   │   │   ├── Application.java    # 启动类
│   │   │   ├── controller/         # REST 控制器
│   │   │   ├── service/            # 业务逻辑层
│   │   │   ├── mapper/             # MyBatis Mapper 接口
│   │   │   ├── entity/             # 实体类
│   │   │   ├── dto/                # 数据传输对象
│   │   │   ├── config/             # 配置类
│   │   │   ├── exception/          # 异常处理
│   │   │   └── util/               # 工具类
│   │   └── resources/              # 配置文件
│   │       ├── application.yml     # 主配置文件
│   │       ├── application-dev.yml # 开发环境配置
│   │       ├── application-prod.yml # 生产环境配置
│   │       ├── mapper/             # MyBatis XML 映射文件
│   │       └── static/             # 静态资源
│   └── test/
│       └── java/com/example/       # 测试代码
│           └── ApplicationTests.java
├── target/                          # 编译输出目录
└── README.md                        # 项目说明文档
```

## 分层架构说明

### Controller 层
- 负责接收 HTTP 请求和返回响应
- 参数校验
- 调用 Service 层处理业务
- 统一异常处理

### Service 层
- 业务逻辑处理
- 事务管理
- 调用 Mapper 层进行数据操作

### Mapper 层
- 数据库操作
- 使用 MyBatis 注解或 XML 映射
- 遵循单一职责原则

### Entity 层
- 与数据库表一一对应
- 使用 JPA 注解或 MyBatis 注解
- 包含基本的 getter/setter

### DTO 层
- 数据传输对象
- 用于不同层之间的数据传递
- 可以包含业务逻辑相关的字段
