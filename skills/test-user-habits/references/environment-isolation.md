# 环境隔离方案参考

## 通用原则

1. **端口隔离**：测试端口 > 60000，正常端口 < 60000
2. **数据库隔离**：使用独立测试数据库实例或 schema
3. **配置隔离**：通过环境变量文件（`test.env`）注入测试配置
4. **日志隔离**：日志输出到 `test-logs/` 目录
5. **进程隔离**：测试后端作为独立子进程启动

---

## Python 后端项目（Flask/FastAPI）

### 端口分配

```python
# 正常配置：.env
PORT=8080
DATABASE_URL=sqlite:///app.db

# 测试配置：test.env
PORT=60001
DATABASE_URL=sqlite:///test-app.db
```

### 启动测试后端

```python
import subprocess
import time
import os

def start_test_backend():
    """启动测试后端，返回进程对象"""
    env = os.environ.copy()
    env.update(load_test_env())  # 读取 test.env

    # 启动后端进程
    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "app:app", "--port", "60001"],
        env=env,
        stdout=open("test-logs/backend.log", "w"),
        stderr=subprocess.STDOUT,
    )

    # 等待服务就绪
    time.sleep(3)
    return proc
```

### 数据库清理

```python
import sqlite3
import os

def setup_test_db():
    """创建空白测试数据库"""
    db_path = "test-app.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    # Flyway/DDL 初始化
    subprocess.run(["python", "migrate.py", "--target", "test"])
    # 插入测试数据
    insert_test_data()
```

---

## Node.js 后端项目（Express/Koa）

### 端口分配

```javascript
// 正常：.env
PORT=8080
DB_HOST=localhost
DB_PORT=3306

// 测试：test.env
PORT=60001
DB_HOST=localhost
DB_PORT=63306
```

### Jest + Supertest E2E

```javascript
// tests/setup.js
const { startTestBackend } = require('./helpers/test-backend');

let server;
beforeAll(async () => {
  server = await startTestBackend({
    port: 60001,
    env: loadTestEnv()
  });
});

afterAll(() => {
  server.close();
});
```

### Playwright + 测试后端配合

```javascript
// playwright.config.js
module.exports = {
  baseURL: process.env.TEST_BACKEND_URL || 'http://localhost:60001',
  use: {
    baseURL: 'http://localhost:60002', // 测试前端端口
  }
};
```

---

## Vue/React 前端项目

### Vite + 测试后端

```javascript
// vite.config.js
export default defineConfig({
  server: {
    port: parseInt(process.env.TEST_FRONTEND_PORT) || 60002,
    proxy: {
      '/api': {
        target: `http://localhost:${process.env.TEST_BACKEND_PORT || 60001}`,
        changeOrigin: true
      }
    }
  }
});
```

### 启动测试前端 + 测试后端

```python
import subprocess
import os
import time

def start_test_frontend():
    """启动测试前端"""
    env = os.environ.copy()
    env["TEST_FRONTEND_PORT"] = "60002"
    env["TEST_BACKEND_PORT"] = "60001"
    env.update(load_test_env())

    proc = subprocess.Popen(
        ["npm", "run", "dev"],
        env=env,
        cwd=os.path.abspath("frontend"),
        stdout=open("test-logs/frontend.log", "w"),
        stderr=subprocess.STDOUT,
    )
    time.sleep(5)  # 等待 Vite 启动
    return proc
```

---

## Java Spring Boot 项目

### application-test.yml

```yaml
# src/test/resources/application-test.yml
server:
  port: 60001

spring:
  datasource:
    url: jdbc:mysql://localhost:63306/test_db
    username: test_user
    password: test_pass
  redis:
    host: localhost
    port: 6380
  flyway:
    locations: classpath:db/migration/test

logging:
  file:
    name: test-logs/spring-test.log
```

### Maven 测试配置

```bash
# 使用测试 profile 启动
mvn spring-boot:run -Dspring-boot.run.profiles=test
```

### 测试脚本

```python
import subprocess

def start_spring_test_backend():
    """启动 Spring Boot 测试后端"""
    proc = subprocess.Popen(
        ["mvn", "spring-boot:run", "-Dspring-boot.run.profiles=test"],
        cwd="/path/to/backend",
        stdout=open("test-logs/spring-boot-test.log", "w"),
        stderr=subprocess.STDOUT,
    )
    # 等待 Actuator 健康检查
    import time, requests
    for _ in range(30):
        try:
            r = requests.get("http://localhost:60001/actuator/health")
            if r.status_code == 200:
                return proc
        except:
            pass
        time.sleep(1)
    raise RuntimeError("Spring Boot 测试后端启动超时")
```

---

## 数据库独立实例策略

### MySQL 多实例（Linux/macOS）

```bash
# macOS Homebrew MySQL 多实例
mysql_install_db --data-dir=/usr/local/var/mysql-test

# 启动测试实例
mysqld --port=63306 --datadir=/usr/local/var/mysql-test \
  --pid-file=/tmp/mysql-test.pid \
  --socket=/tmp/mysql-test.sock \
  --log-error=test-logs/mysql-test.err

# 创建测试数据库
mysql -u root -P 63306 -S /tmp/mysql-test.sock \
  -e "CREATE DATABASE IF NOT EXISTS test_db; \
      CREATE USER IF NOT EXISTS 'test_user'@'localhost' IDENTIFIED BY 'test_pass'; \
      GRANT ALL ON test_db.* TO 'test_user'@'localhost';"
```

### MySQL 多实例（Windows）

```powershell
# 复制 MySQL 安装目录作为测试实例
Copy-Item -Recurse C:\mysql D:\mysql-test

# 用不同端口和数据目录启动
mysqld --port=63306 --datadir=D:\mysql-test\data `
  --pid-file=D:\mysql-test\data\test.pid `
  --socket=mysql-test.sock
```

---

## Redis 隔离

```bash
# Linux/macOS
redis-server --port 6380 --loglevel notice \
  --logfile test-logs/redis-test.log \
  --dir /tmp --daemonize yes

# Windows (手动)
# 下载 Redis Windows 版，用不同端口启动第二个实例
```

---

## 环境就绪检查脚本

```python
import socket
import subprocess
import time
import os
import requests

def check_port(port):
    """检查端口是否可用（已被监听=服务已启动）"""
    with socket.socket() as s:
        return s.connect_ex(('localhost', port)) == 0

def wait_for_service(url, timeout=30):
    """等待服务就绪"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code < 500:
                return True
        except:
            pass
        time.sleep(1)
    return False

def setup_and_verify():
    """完整环境就绪检查"""
    # 1. MySQL
    assert check_port(63306), "测试 MySQL 未就绪"
    # 2. Redis
    assert check_port(6380), "测试 Redis 未就绪"
    # 3. 后端
    assert wait_for_service("http://localhost:60001/api/health"), "测试后端未就绪"
    # 4. 前端
    assert wait_for_service("http://localhost:60002", timeout=10), "测试前端未就绪"
    return True
```

---

## 进程清理策略

```python
import psutil
import os
import signal

def cleanup_test_processes():
    """清理所有测试进程"""
    test_ports = [60001, 60002, 6380]
    killed = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline') or []
            cmdline_str = ' '.join(cmdline)
            # 识别测试进程
            if any(str(port) in cmdline_str for port in test_ports):
                proc.terminate()
                killed.append(proc.info['pid'])
            # 识别测试数据库进程
            if 'mysql-test' in cmdline_str or 'redis-server' in cmdline_str and '--port 6380' in cmdline_str:
                proc.terminate()
                killed.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return killed
```

---

## .gitignore 模板（测试相关）

```gitignore
# 测试输出（勿提交）
test/output/
test-logs/
test.env

# 测试数据库（可能存在）
*.test.db
test-*.db

# Playwright trace 文件
trace.zip
playwright-traces/
```
