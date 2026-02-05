# Flyway 数据库版本管理

## 核心优势

1. **版本化管理**：通过迁移脚本精确控制数据库变更历史
2. **自动化迁移**：应用启动时自动执行数据库升级
3. **团队协作**：多人协作开发时保持数据库结构一致性
4. **回滚支持**：支持迁移回滚，便于修复问题

## 依赖配置

### Maven 依赖

```xml
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
    <version>10.14.1</version>
</dependency>
```

### Spring Boot 集成

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jdbc</artifactId>
</dependency>
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
</dependency>
```

## 目录结构

```
src/main/resources/
└── db/
    └── migration/              # Flyway 迁移脚本目录
        ├── V1__init.sql        # 初始版本
        ├── V2__add_user_table.sql
        └── V3__add_index.sql
```

## 配置文件

### application.yml

```yaml
spring:
  flyway:
    enabled: true
    baseline-on-migrate: true
    validate-on-migrate: true
    encoding: UTF-8
    locations: classpath:db/migration
    baseline-version: 1
    out-of-order: false
    clean-disabled: true  # 禁用清理，生产环境必须开启

  datasource:
    url: jdbc:mysql://localhost:3306/your_db
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
    driver-class-name: com.mysql.cj.jdbc.Driver
```

### application.properties

```properties
spring.flyway.enabled=true
spring.flyway.baseline-on-migrate=true
spring.flyway.locations=classpath:db/migration
spring.flyway.baseline-version=1
spring.flyway.clean-disabled=true

spring.datasource.url=jdbc:mysql://localhost:3306/your_db
spring.datasource.username=${DB_USERNAME}
spring.datasource.password=${DB_PASSWORD}
```

## 迁移脚本规范

### 命名规则

```
V<版本号>__<描述>.sql
```

- 版本号使用整数（如 `V1__`、`V2__`）
- 描述使用下划线分隔的简短说明
- 使用双下划线 `__` 分隔版本号和描述

### 版本号示例

```sql
V1__init_schema.sql
V2__create_user_table.sql
V3__add_email_column.sql
V4__create_order_table.sql
V5__add_user_index.sql
```

### 脚本编写规范

1. **每个迁移只做一件事**：单一职责，便于追踪
2. **使用事务**：默认自动包装为事务，失败会回滚
3. **编写可重复执行的脚本**：使用 `IF NOT EXISTS`
4. **添加注释**：说明变更目的和影响
5. **避免破坏性变更**：新增列、表优先，删除操作需谨慎

## 迁移脚本示例

### 初始化脚本（V1__init.sql）

```sql
-- 用户表
CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
  `password` VARCHAR(100) NOT NULL COMMENT '加密密码',
  `email` VARCHAR(100) COMMENT '邮箱',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX `idx_username` (`username`),
  INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 角色表
CREATE TABLE IF NOT EXISTS `roles` (
  `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL UNIQUE COMMENT '角色名',
  `description` VARCHAR(200) COMMENT '描述'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS `user_roles` (
  `user_id` BIGINT NOT NULL,
  `role_id` BIGINT NOT NULL,
  PRIMARY KEY (`user_id`, `role_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`role_id`) REFERENCES `roles`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';
```

### 新增列（V2__add_user_phone.sql）

```sql
-- 为用户表添加手机号字段
ALTER TABLE `users`
ADD COLUMN `phone` VARCHAR(20) COMMENT '手机号' AFTER `email`;
```

### 新增索引（V3__add_user_status_index.sql）

```sql
-- 为用户表添加状态字段和索引
ALTER TABLE `users`
ADD COLUMN `status` TINYINT DEFAULT 1 COMMENT '状态：1-正常，0-禁用' AFTER `phone`;

CREATE INDEX `idx_status` ON `users`(`status`);
```

## 高级用法

### 基线迁移（Baseline Migration）

对于已有数据库项目，首次引入 Flyway：

```bash
# 1. 创建基线版本
flyway baseline -baselineVersion="1" -baselineDescription="Existing DB"

# 2. 或在配置文件中启用自动基线
spring.flyway.baseline-on-migrate=true
```

### 迁移回滚

```java
// 使用 Flyway API 进行回滚
@Autowired
private Flyway flyway;

public void rollbackMigration() {
    flyway.repair();  // 修复 metadata 表
    flyway.clean();   // 清理所有对象（仅开发环境）
}
```

### 非版本化迁移（Repeatable Migrations）

```sql
-- 文件名以 R 开头
R__create_views.sql

CREATE OR REPLACE VIEW active_users AS
SELECT id, username, email
FROM users
WHERE status = 1;
```

### Java 迁移

```java
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.springframework.jdbc.core.JdbcTemplate;

public class V6__AddAuditLogTable extends BaseJavaMigration {

    @Override
    public void migrate(Context context) throws Exception {
        JdbcTemplate jdbcTemplate = new JdbcTemplate(context.getConfiguration().getDataSource());

        jdbcTemplate.execute(
            "CREATE TABLE IF NOT EXISTS `audit_log` (" +
            "  `id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY," +
            "  `action` VARCHAR(50) NOT NULL," +
            "  `user_id` BIGINT," +
            "  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP" +
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        );
    }
}
```

## 常用命令

### Maven 命令

```bash
# 迁移数据库
mvn flyway:migrate

# 回滚到指定版本
mvn flyway:undo -Dflyway.target=1

# 修复 metadata 表
mvn flyway:repair

# 清理数据库（仅开发环境）
mvn flyway:clean

# 验证迁移脚本
mvn flyway:validate

# 信息查询
mvn flyway:info
```

### CLI 命令

```bash
# 下载 Flyway CLI
# https://flywaydb.org/download/community

# 迁移
flyway migrate -url=jdbc:mysql://localhost:3306/db -user=root -password=xxx

# 回滚
flyway undo -target=1

# 信息查询
flyway info
```

## 多环境配置

### 开发环境（application-dev.yml）

```yaml
spring:
  flyway:
    enabled: true
    clean-disabled: false  # 允许清理，方便开发
    locations: classpath:db/migration,classpath:db/migration/dev
```

### 测试环境（application-test.yml）

```yaml
spring:
  flyway:
    enabled: true
    baseline-on-migrate: true
    locations: classpath:db/migration,classpath:db/migration/test
```

### 生产环境（application-prod.yml）

```yaml
spring:
  flyway:
    enabled: true
    baseline-on-migrate: false  # 生产环境禁用基线，防止意外覆盖
    validate-on-migrate: true   # 严格验证
    clean-disabled: true        # 禁止清理
    locations: classpath:db/migration
```

## 最佳实践

### 1. 版本控制

- 所有迁移脚本必须纳入 Git 版本管理
- 不要修改已提交的迁移脚本
- 新的变更创建新的迁移文件

### 2. 脚本审查

- 团队成员审查每个迁移脚本
- 确保不会破坏现有数据
- 测试迁移的可重复执行性

### 3. 分支管理

- 功能分支的迁移脚本需要协调版本号
- 合并到主分支后，确保版本号唯一
- 使用较大的版本号跳跃（如 100, 200, 300）预留空间

### 4. 数据迁移

```sql
-- V10__migrate_legacy_data.sql

-- 插入默认数据
INSERT INTO `roles` (`id`, `name`, `description`) VALUES
(1, 'ADMIN', '系统管理员'),
(2, 'USER', '普通用户')
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`);

-- 数据转换
UPDATE `users` SET `status` = 1 WHERE `status` IS NULL;
```

### 5. 监控与日志

```yaml
logging:
  level:
    org.flywaydb: DEBUG
```

### 6. CI/CD 集成

```yaml
# .github/workflows/deploy.yml
steps:
  - name: Flyway Migration
    run: mvn flyway:migrate -Dflyway.url=$DB_URL -Dflyway.user=$DB_USER -Dflyway.password=$DB_PASSWORD
    env:
      DB_URL: ${{ secrets.PROD_DB_URL }}
      DB_USER: ${{ secrets.PROD_DB_USER }}
      DB_PASSWORD: ${{ secrets.PROD_DB_PASSWORD }}
```

## 常见问题

### Q1: 已存在的数据库如何引入 Flyway？

**方案**：使用基线功能

```yaml
spring:
  flyway:
    enabled: true
    baseline-on-migrate: true
    baseline-version: 1
    locations: classpath:db/migration
```

首次运行时会创建 `flyway_schema_history` 表，记录当前版本为 1。

### Q2: 迁移失败怎么办？

1. 查看 `flyway_schema_history` 表中的失败记录
2. 修复脚本问题
3. 使用 `flyway repair` 命令修复 metadata 表
4. 重新执行迁移

### Q3: 如何处理多人开发的版本冲突？

- 约定版本号规则（如：功能分支使用 100+，主分支使用 1,2,3...）
- 合并时调整版本号，确保唯一性
- 使用较大的版本号跳跃预留空间

### Q4: 生产环境如何安全回滚？

**不推荐在生产环境使用 `flyway undo`**

推荐做法：
1. 创建新的迁移脚本修复问题
2. 使用版本控制确保可追溯
3. 在测试环境充分验证后再部署

### Q5: 迁移脚本太大导致执行超时？

- 拆分大脚本为多个小脚本
- 批量数据迁移时分批次执行
- 调整数据库超时配置

```yaml
spring:
  datasource:
    hikari:
      connection-timeout: 30000
```

## 总结

Flyway 提供了简单可靠的数据库版本管理方案：

- ✅ 版本化迁移脚本，易于追踪
- ✅ 自动化执行，减少人工错误
- ✅ 支持多种数据库，跨平台兼容
- ✅ 与 Spring Boot 无缝集成
- ✅ 支持 SQL 和 Java 两种迁移方式

通过规范的迁移流程和团队协作，可以有效提升数据库变更的可靠性和可维护性。
