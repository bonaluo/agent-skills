# Playwright 常用模式参考

## 选择器优先级

按可靠性从高到低使用选择器：

```python
# 1. 角色选择器（最推荐）- 无需了解 DOM 结构
page.get_by_role("button", name="提交")
page.get_by_role("link", name="查看详情")
page.get_by_role("textbox", name="用户名")

# 2. 标签文本（第二推荐）
page.get_by_label("用户名")          # <label for="..."> 用户名
page.get_by_placeholder("请输入")
page.get_by_text("登录")

# 3. 测试 ID（需开发配合，稳定性最高）
page.get_by_test_id("submit-btn")

# 4. CSS 选择器（最后手段）
page.locator("form .btn-primary")

# 5. XPath（避免使用，难以维护）
page.locator("//button[contains(text(),'提交')]")
```

## 页面等待策略

```python
# ✅ 推荐：智能等待元素
expect(page.get_by_role("button", name="提交")).to_be_enabled()

# ✅ 推荐：等待 URL 变化
expect(page).to_have_url(re.compile(r"/dashboard"), timeout=5000)

# ✅ 推荐：等待文本出现
expect(page.get_by_text("创建成功")).to_be_visible(timeout=3000)

# ❌ 避免：硬编码 sleep
time.sleep(2)  # 不要用
```

## 常用断言

```python
from playwright.sync_api import expect

# 元素可见/隐藏
expect(locator).to_be_visible()
expect(locator).to_be_hidden()
expect(locator).to_be_enabled()
expect(locator).to_be_disabled()

# 文本内容
expect(locator).to_have_text("期望文本")
expect(locator).to_contain_text("包含")

# URL 和标题
expect(page).to_have_url(re.compile(r"/home"))
expect(page).to_have_title("页面标题")

# 计数
expect(locator).to_have_count(3)
expect(locator).to_have_count(0)  # 元素消失
```

## 控制台捕获

```python
console_messages = []
page.on("console", lambda msg: console_messages.append({
    "type": msg.type,
    "text": msg.text,
    "location": msg.location
}))

# 测试结束后检查错误
error_logs = [m for m in console_messages if m["type"] == "error"]
assert len(error_logs) == 0, f"控制台错误: {error_logs}"
```

## 网络请求拦截

```python
from playwright.sync_api import Route

# 监控特定 API 调用
api_calls = []

def handle_route(route: Route):
    api_calls.append({
        "url": route.request.url,
        "method": route.request.method,
    })
    route.continue_()

page.route("**/api/**", handle_route)

# 验证 API 被调用
page.get_by_role("button", name="保存").click()
assert any("/api/users" in c["url"] for c in api_calls)
```

## 文件下载验证

```python
with page.expect_download() as download_info:
    page.get_by_role("link", name="下载报表").click()

download = download_info.value
assert "report" in download.suggested_filename
path = download.path()
assert os.path.exists(path)
```

## 弹窗/对话框处理

```python
# 确认对话框
page.on("dialog", lambda dialog: dialog.accept())

# 自定义对话框文本
page.on("dialog", lambda dialog: dialog.accept("自定义输入"))

# 取消对话框
page.on("dialog", lambda dialog: dialog.dismiss())
```

## 跨浏览器测试

```python
# browsers 参数: chromium（默认）, firefox, webkit
with sync_playwright() as p:
    for browser_type in [p.chromium, p.firefox, p.webkit]:
        browser = browser_type.launch()
        page = browser.new_page()
        # 测试逻辑
        browser.close()
```

## 测试截图策略

```python
# 1. 失败时自动截图（pytest 钩子）
@pytest.fixture
def page(page):
    page.on("pageerror", lambda exc: page.screenshot(path="error.png"))
    yield page

# 2. 关键步骤截图
page.screenshot(path="step1-login-form.png")
page.get_by_label("用户名").fill("admin")
page.screenshot(path="step2-filled-form.png")

# 3. 全页面截图
page.screenshot(path="full-page.png", full_page=True)
```

## pytest Playwright 集成

```python
# conftest.py - 全局配置
import pytest
from playwright.sync_api import sync_playwright, Page

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 调试用可视化
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="zh-CN"
    )
    page = context.new_page()
    yield page
    context.close()
```

## 数据驱动测试

```python
import pytest

test_cases = [
    {"username": "admin", "password": "admin123", "expected": "success"},
    {"username": "", "password": "", "expected": "field_required"},
    {"username": "admin", "password": "wrong", "expected": "auth_failed"},
]

@pytest.mark.parametrize("case", test_cases)
def test_login_param(page: Page, case):
    page.goto("/login")
    page.get_by_label("用户名").fill(case["username"])
    page.get_by_label("密码").fill(case["password"])
    page.get_by_role("button", name="登录").click()
    # 断言逻辑
```

## 性能度量

```python
import time

start = time.time()
page.goto(f"{BACKEND_URL}/heavy-page")
load_time = time.time() - start

assert load_time < 3.0, f"页面加载时间 {load_time}s 超过 3s"
```

## 测试报告结构

每个测试输出目录的结构：

```
test/output/yyyymmddhhmm/01-用户管理/01-login-test/
├── console.log         # 捕获的浏览器控制台日志
├── screenshot.png      # 测试结束截图
├── result.json         # 测试结果摘要
├── network/            # 网络请求日志（可选）
│   └── api-calls.json
└── traces/             # Playwright trace 文件（调试用）
    └── trace.zip
```

`result.json` 格式：

```json
{
  "test": "01-login-test",
  "status": "passed",
  "duration_ms": 2340,
  "assertions": [
    {"name": "login_redirect", "passed": true},
    {"name": "no_console_errors", "passed": true}
  ],
  "timestamp": "2026-04-18T17:30:00Z"
}
```
