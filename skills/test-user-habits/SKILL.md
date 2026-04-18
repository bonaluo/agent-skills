---
name: test-user-habits
description: |
  管理项目自动化测试的完整工作流程。当需要创建测试、运行测试、管理测试环境、执行 Playwright E2E 测试、或确保测试环境与生产环境隔离时触发此技能。覆盖测试目录规划、环境隔离策略、Playwright 脚本编写规范、测试输出管理。
metadata:
  version: 20260418.1745
  update-url: https://github.com/bonaluo/agent-skills@test-user-habits
---

# 测试规范与自动化

本技能管理项目测试的完整生命周期：**环境准备 → 测试执行 → 结果验证 → 环境清理**。

## 核心理念

1. **浏览器是唯一入口**：所有测试必须从真实浏览器发起，模拟真实用户操作。禁止直接调用后端 API 作为主要验证手段（API 只能作为辅助校验）。
2. **环境完全隔离**：测试不得污染开发/生产环境，不得依赖真实数据，所有端口必须使用 60000 以上的测试专用端口。
3. **依赖必须就绪**：测试执行前，所有依赖环境（后端服务、数据库、Redis 等）必须启动并验证可用。

---

## 测试目录结构

在项目根目录下创建以下结构（若不存在）：

```
<项目根目录>/
├── test/
│   ├── playwright/              # Playwright 测试脚本根目录
│   │   └── 01-用户管理/         # 按功能模块组织
│   │       └── 01-login-test.py
│   │   └── 02-数据管理/
│   │       └── 01-create-test.py
│   └── output/                  # 测试输出（勿提交至 git）
│       └── [自动生成的时间戳目录]/
│           └── 01-用户管理/
│               └── 01-login-test/
│                   ├── console.log
│                   ├── screenshot.png
│                   └── result.json
└── test.env/                    # 测试专用环境变量（勿提交至 git）
```

**重要**：`test/output/` 目录必须加入 `.gitignore`。

---

## 环境隔离策略

### 端口分配规则

**所有测试端口必须 > 60000**，包括数据库、中间件等。以下为各服务的端口分配模式：

| 服务 | 正常端口 | 测试端口范围 | 说明 |
|------|---------|------------|------|
| 后端服务 | 8080 | **60001–60999** | 随机选取可用端口 |
| 数据库 | 3306 | **63306–63999** | 独立测试实例 |
| Redis | 6379 | **66379–66999** | 独立测试实例 |
| 前端开发服务器 | 5173 | **65173–65999** | 测试前端专用端口 |
| 其他中间件 | — | **6XXXX** | 各自随机选取 > 60000 的端口 |

> **禁止使用 60000 以下的端口进行任何测试活动**，包括数据库、缓存、消息队列等。

### 获取随机可用端口

```python
import socket

def get_free_port(min_port=60000, max_port=65535):
    """获取大于 min_port 的随机可用端口"""
    while True:
        port = min_port + hash(str(__import__('time').time())) % (max_port - min_port)
        with socket.socket() as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
```

### 环境变量隔离

通过 `test.env` 文件注入测试环境变量：

```bash
# test.env 示例
TEST_BACKEND_PORT=60001
TEST_FRONTEND_PORT=65173
TEST_DB_HOST=localhost
TEST_DB_PORT=63306
TEST_DB_NAME=test_db
TEST_DB_USER=test_user
TEST_DB_PASSWORD=test_pass
TEST_REDIS_HOST=localhost
TEST_REDIS_PORT=66379
```

---

## Playwright 测试编写规范

### 最小测试单元原则

**每个测试文件只测一个功能**。禁止在一个脚本中测试多个独立功能。

### 文件命名规则

`{序号}-{功能模块}/{序号}-{具体功能}-test.py`

```
test/playwright/
└── 01-用户管理/
    ├── 01-login-test.py        # 登录
    ├── 02-register-test.py     # 注册
    └── 03-reset-pwd-test.py    # 重置密码
```

### 测试脚本模板

```python
"""
功能：用户登录
验收标准：输入正确凭据后成功进入主页，控制台无 Error 日志
前置条件：测试后端运行中，测试用户已创建
"""

import pytest
import time
import json
import os
from playwright.sync_api import sync_playwright, Page, expect

# 测试配置（由环境自动注入）
BACKEND_URL = os.environ.get("TEST_BACKEND_URL", "http://localhost:60001")
OUTPUT_DIR = os.environ.get("TEST_OUTPUT_DIR", "test/output/current")

class TestLogin:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.console_errors = []
        self.page.on("console", lambda msg: self.console_errors.append(msg))
        yield
        # 每个测试后保存输出
        self._save_output()

    def _save_output(self):
        """保存测试输出到 OUTPUT_DIR"""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        # 保存控制台日志
        with open(os.path.join(OUTPUT_DIR, "console.log"), "w", encoding="utf-8") as f:
            f.write("\n".join(str(m) for m in self.console_errors))
        # 保存截图
        self.page.screenshot(path=os.path.join(OUTPUT_DIR, "screenshot.png"))

    def test_login_success(self, page: Page):
        """验收标准：有效凭据登录成功"""
        page.goto(f"{BACKEND_URL}/login")
        page.get_by_label("用户名").fill("testuser")
        page.get_by_label("密码").fill("testpass")
        page.get_by_role("button", name="登录").click()
        expect(page).to_have_url(re.compile(r"/home|/dashboard"), timeout=5000)
        # 验证无控制台错误
        error_logs = [m for m in self.console_errors if m.type == "error"]
        assert len(error_logs) == 0, f"控制台存在错误: {error_logs}"

    def test_login_wrong_password(self, page: Page):
        """验收标准：错误密码拒绝登录"""
        page.goto(f"{BACKEND_URL}/login")
        page.get_by_label("用户名").fill("testuser")
        page.get_by_label("密码").fill("wrongpass")
        page.get_by_role("button", name="登录").click()
        expect(page.get_by_text("用户名或密码错误")).to_be_visible(timeout=3000)
```

### 测试后端 API 校验

Playwright 测试中应结合后端 API 验证数据一致性：

```python
import requests

def test_user_created_via_api(page: Page):
    """通过 API 验证用户创建结果"""
    # 1. UI 操作
    page.goto(f"{BACKEND_URL}/users/new")
    page.get_by_label("用户名").fill("newuser")
    page.get_by_role("button", name="创建").click()
    expect(page.get_by_text("创建成功")).to_be_visible()

    # 2. 后端 API 校验（测试后端端口，非生产端口）
    resp = requests.get(f"{BACKEND_URL}/api/users/newuser")
    assert resp.status_code == 200
    assert resp.json()["username"] == "newuser"
```

---

## 全自动执行工作流

当用户要求运行测试时，执行以下完整流程。**所有阶段必须完成后才进行下一阶段**。

### 阶段 1：环境准备

**依赖就绪是执行测试的前提**。按以下顺序准备：

1. **分配测试资源**：
   - 读取项目现有配置（如 `.env`、配置文件）
   - 分配所有测试端口（全部 > 60000）：后端端口、数据库端口（63306+）、Redis 端口（66379+）、前端端口（65173+）
   - 创建/更新 `test.env` 存储本次测试配置
2. **启动中间件**（按依赖顺序）：
   - 启动测试数据库，验证连接就绪（ping 或健康检查）
   - 启动测试 Redis，验证连接就绪
   - 执行数据库迁移/初始化脚本，注入测试数据
3. **启动测试后端**：使用 `test.env` 配置启动，日志写入 `test-logs/backend.log`，等待健康检查通过
4. **启动测试前端**：配置代理指向测试后端端口，日志写入 `test-logs/frontend.log`
5. **验证环境就绪**：逐一 ping 所有服务，确认全部可用后再进入执行阶段

> **任何依赖未就绪都不得执行测试**。报告缺失项并等待用户处理。

### 阶段 2：执行测试

测试入口：**浏览器**。通过 Playwright 操作真实浏览器页面。

1. **生成时间戳输出目录**：`test/output/{yyyy}{mm}{dd}{hh}{mm}/`
2. **设置环境变量**：`TEST_OUTPUT_DIR`、`TEST_BACKEND_URL`、`TEST_FRONTEND_URL`
3. **执行 Playwright 测试**：逐个运行测试文件，从浏览器页面发起操作
4. **捕获所有输出**：
   - Playwright 控制台日志
   - 每步关键操作截图
   - 测试断言结果（result.json）

### 阶段 3：结果验证

1. 解析每个测试的 `result.json`，汇总通过/失败状态
2. 若有失败，结合浏览器控制台日志和截图分析原因（UI 问题、后端错误、网络问题）
3. 生成测试报告摘要，包含通过率、失败原因和关键截图

### 阶段 4：环境清理

1. 停止测试前端进程
2. 停止测试后端进程
3. 停止测试数据库和 Redis（如为临时实例）
4. 保留测试输出目录（供人工复查）

---

## .gitignore 管理

**首次创建测试目录后**，必须处理 `.gitignore`：

1. 检查项目根目录是否存在 `.gitignore`
2. 若存在，追加以下内容：
   ```
   test/output/
   test.env
   test-logs/
   ```
3. 若不存在，创建 `.gitignore` 并写入上述内容
4. **验证** git 是否忽略这些目录：
   ```bash
   git check-ignore -v test/output/
   ```

---

## 参考文档

详细的使用模式见以下参考文档（按需加载）：

- [references/playwright-patterns.md](references/playwright-patterns.md) — Playwright 常用模式、选择器、断言
- [references/environment-isolation.md](references/environment-isolation.md) — 各类型项目的环境隔离方案
