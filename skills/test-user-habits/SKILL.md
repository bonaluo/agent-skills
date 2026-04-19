---
name: test-user-habits
description: |
  Manages the complete workflow for project automated testing. Trigger this skill when creating tests, running tests, managing test environments, executing Playwright E2E tests, or ensuring test environment isolation from production. Covers test directory planning, environment isolation strategies, Playwright script writing standards, and test output management. / 管理项目自动化测试的完整工作流程。当需要创建测试、运行测试、管理测试环境、执行 Playwright E2E 测试、或确保测试环境与生产环境隔离时触发此技能。覆盖测试目录规划、环境隔离策略、Playwright 脚本编写规范、测试输出管理。
metadata:
  version: 20260419.1439
  update-url: https://github.com/bonaluo/agent-skills@test-user-habits
---

# 测试规范与自动化

本技能管理项目测试的完整生命周期：**环境准备 → 测试执行 → 结果验证 → 环境清理**。

## 核心理念

1. **浏览器是唯一入口**：所有测试必须从真实浏览器发起，模拟真实用户操作在前端页面。禁止直接调用后端 API 作为主要验证手段（API 只能作为辅助校验）。
2. **测试位于前端项目**：Playwright E2E 测试必须位于**前端项目**目录内，因为项目根目录可能同时包含前端项目和后端项目。
3. **配套环境服务测试**：后端服务、数据库、Redis 等是辅助 Playwright 测试的配套环境，用于模拟真实用户体验。
4. **环境完全隔离**：测试不得污染开发/生产环境，不得依赖真实数据，所有端口必须使用 60000 以上的测试专用端口。
5. **依赖必须就绪**：测试执行前，所有配套环境（后端服务、数据库、Redis 等）必须启动并验证可用。

---

## 测试目录结构

**重要**：Playwright 测试是浏览器端 E2E 测试，必须位于**前端项目**内部。项目根目录可能同时包含前端项目和后端项目，测试目录应放在前端项目中。

### 前端项目测试结构

```
<前端项目目录>/
├── src/                         # 前端源代码
├── test/                        # Playwright 测试（位于前端项目）
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

### 配套测试环境（辅助 Playwright 测试）

Playwright 测试需要配套环境来模拟真实用户体验，这些环境是**辅助性质**的：

```
<项目根目录>/                           # 包含前端和后端的完整项目
├── frontend/                          # 前端项目（含 Playwright 测试）
│   ├── src/
│   ├── test/                         # ★ Playwright 测试必须在这里
│   │   ├── playwright/
│   │   └── output/
│   └── test.env
├── backend/                           # 后端服务（测试用）
│   └── (测试端口运行)
├── services/                         # 测试辅助服务
│   ├── mysql-test/                   # 测试数据库（端口 63306+）
│   └── redis-test/                   # 测试 Redis（端口 66379+）
└── test.env                           # 统一测试环境变量
```

**重要**：
- `test/output/` 目录必须加入前端项目的 `.gitignore`
- 测试环境变量可放在前端项目或项目根目录的 `test.env`

---

## 环境隔离策略

### 配套测试环境说明

**Playwright 测试依赖配套环境来模拟真实用户体验**。这些环境是辅助性质的，核心是浏览器端测试：

- **测试后端**：提供 API 服务，供 Playwright 通过浏览器调用
- **测试数据库**：独立实例，存储测试数据，不污染开发/生产数据
- **测试 Redis**：独立实例，用于缓存和会话管理测试
- **测试中间件**：根据项目需求（消息队列、对象存储等）

### 端口分配规则

**所有测试端口必须 > 60000**，包括后端服务、数据库、中间件等。以下为各服务的端口分配模式：

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

**注意**：Playwright 测试的是前端页面，因此 `page.goto()` 应使用前端服务器地址（FRONTEND_URL），而不是后端地址。测试后端 API 时才使用 BACKEND_URL。

```python
"""
功能：用户登录
验收标准：输入正确凭据后成功进入主页，控制台无 Error 日志
前置条件：测试前端和后端运行中，测试用户已创建
"""

import pytest
import time
import json
import os
from playwright.sync_api import sync_playwright, Page, expect

# 测试配置（由环境自动注入）
FRONTEND_URL = os.environ.get("TEST_FRONTEND_URL", "http://localhost:65173")
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
        page.goto(f"{FRONTEND_URL}/login")  # ★ 使用前端 URL，不是后端 URL
        page.get_by_label("用户名").fill("testuser")
        page.get_by_label("密码").fill("testpass")
        page.get_by_role("button", name="登录").click()
        expect(page).to_have_url(re.compile(r"/home|/dashboard"), timeout=5000)
        # 验证无控制台错误
        error_logs = [m for m in self.console_errors if m.type == "error"]
        assert len(error_logs) == 0, f"控制台存在错误: {error_logs}"

    def test_login_wrong_password(self, page: Page):
        """验收标准：错误密码拒绝登录"""
        page.goto(f"{FRONTEND_URL}/login")  # ★ 使用前端 URL，不是后端 URL
        page.get_by_label("用户名").fill("testuser")
        page.get_by_label("密码").fill("wrongpass")
        page.get_by_role("button", name="登录").click()
        expect(page.get_by_text("用户名或密码错误")).to_be_visible(timeout=3000)
```

### 测试后端 API 校验

Playwright 测试中可结合后端 API 验证数据一致性（API 校验是辅助手段）：

```python
import requests

def test_user_created_via_api(page: Page):
    """通过 API 验证用户创建结果"""
    # 1. UI 操作（使用前端 URL）
    page.goto(f"{FRONTEND_URL}/users/new")
    page.get_by_label("用户名").fill("newuser")
    page.get_by_role("button", name="创建").click()
    expect(page.get_by_text("创建成功")).to_be_visible()

    # 2. 后端 API 校验（使用后端 URL）
    resp = requests.get(f"{BACKEND_URL}/api/users/newuser")
    assert resp.status_code == 200
    assert resp.json()["username"] == "newuser"
```

---

## 全自动执行工作流

当用户要求运行测试时，执行以下完整流程。**所有阶段必须完成后才进行下一阶段**。

### 阶段 1：环境准备

**Playwright 测试依赖配套环境就绪**。按以下顺序准备：

1. **确认前端项目路径**：
   - 确认 Playwright 测试位于前端项目目录下
   - 确认前端项目结构（src、test 等目录）
2. **分配测试资源**：
   - 读取项目现有配置（如 `.env`、配置文件）
   - 分配所有测试端口（全部 > 60000）：后端端口、数据库端口（63306+）、Redis 端口（66379+）、前端端口（65173+）
   - 创建/更新前端项目或根目录的 `test.env` 存储本次测试配置
3. **启动配套服务**（按依赖顺序，为 Playwright 测试提供支持）：
   - 启动测试数据库，验证连接就绪（ping 或健康检查）
   - 启动测试 Redis，验证连接就绪
   - 执行数据库迁移/初始化脚本，注入测试数据
4. **启动测试后端**：使用 `test.env` 配置启动，日志写入 `test-logs/backend.log`，等待健康检查通过
5. **启动测试前端**：配置代理指向测试后端端口，日志写入 `test-logs/frontend.log`
6. **验证环境就绪**：逐一 ping 所有服务，确认全部可用后再进入执行阶段

> **任何依赖未就绪都不得执行测试**。报告缺失项并等待用户处理。

### 阶段 2：执行测试

测试入口：**浏览器**。通过 Playwright 在真实浏览器中操作前端页面。

1. **切换到前端项目目录**：`cd frontend`（确保在正确的前端项目目录执行）
2. **生成时间戳输出目录**：`test/output/{yyyy}{mm}{dd}{hh}{mm}/`
3. **设置环境变量**：`TEST_OUTPUT_DIR`、`TEST_BACKEND_URL`、`TEST_FRONTEND_URL`
4. **执行 Playwright 测试**：逐个运行测试文件，从浏览器页面发起操作
5. **捕获所有输出**：
   - Playwright 控制台日志
   - 每步关键操作截图
   - 测试断言结果（result.json）

### 阶段 3：结果验证

1. 解析每个测试的 `result.json`，汇总通过/失败状态
2. 若有失败，结合浏览器控制台日志和截图分析原因（UI 问题、后端错误、网络问题）
3. 生成测试报告摘要，包含通过率、失败原因和关键截图

### 阶段 4：环境清理

清理为 Playwright 测试配套的环境：

1. 停止测试前端进程
2. 停止测试后端进程
3. 停止测试数据库和 Redis（如为临时实例）
4. 保留测试输出目录（供人工复查）

---

## .gitignore 管理

**首次创建测试目录后**，必须确保测试输出目录被 git 忽略：

1. **判断 .gitignore 位置**：
   - 若前端项目有独立的 `.gitignore`（独立仓库或子模块），则添加到前端项目的 `.gitignore`
   - 若前端项目没有独立的 `.gitignore`（与后端共享同一个 git 仓库），则添加到项目根目录的 `.gitignore`
2. 追加以下内容到对应的 `.gitignore`：
   ```
   test/output/
   test.env
   test-logs/
   ```
3. **验证** git 是否忽略这些目录：
   ```bash
   # 在对应的项目目录执行
   git check-ignore -v test/output/
   ```

---

## 参考文档

详细的使用模式见以下参考文档（按需加载）：

- [references/playwright-patterns.md](references/playwright-patterns.md) — Playwright 常用模式、选择器、断言
- [references/environment-isolation.md](references/environment-isolation.md) — 各类型项目的环境隔离方案
