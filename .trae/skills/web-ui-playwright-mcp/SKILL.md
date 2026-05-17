---
name: web-ui-playwright-mcp
description: 基于页面链接、运行中的站点、本地前端项目或 UI 需求说明，使用 Playwright MCP 优先完成 Web UI 自动化测试、页面验证、交互回归、端到端流程检查与截图取证，并将稳定流程沉淀为可复用且经过验证的 Python + pytest + Playwright 自动化脚本。适用于"做 web UI 自动化测试""验证页面交互""检查响应式布局""跑登录/表单/业务主流程""结合 Playwright MCP 生成、验证并执行 Python 自动化脚本"的场景。
---

必须先使用 Playwright MCP 完成 Web UI 自动化，流程稳定后按模板结构沉淀成可复用的 `Python + pytest + Playwright` 脚本。

## 工作流

1. **识别测试入口**
- 支持运行中的站点、测试环境 URL、页面需求说明、原型图、截图、纯文本操作步骤。
- 先明确是"执行自动化验证"还是"沉淀可复用脚本"，或两者都要。

2. **优先走 Playwright MCP**
- 可直接访问页面 → 优先用 MCP 执行交互和截图。
- 页面未启动或地址未知 → 先定位可访问入口。
- 涉及登录态 → 优先复用 `storageState`，其次 cookies，最后才走表单登录。

3. **提炼页面对象与关键场景**
- 整理：页面/模块、入口 URL、关键元素、关键交互、成功判定、失败风险、前置条件。
- 复杂流程拆成"页面 → 动作 → 断言 → 证据"序列。

4. **设计覆盖层级**
- 至少覆盖：页面可达性、核心元素存在、主流程、表单校验、异常提示、权限/登录、响应式布局（desktop + mobile）。
- 关键节点必须截图留证。

5. **执行自动化并沉淀脚本**
- 先用 MCP 跑通核心流程，再基于已验证的动作序列按模板结构生成脚本。
- 优先使用稳定定位方式，关键动作必须有对应断言。
- 登录步骤抽成共享 helper，不硬复制到每个测试文件。
- 脚本生成后必须实际执行验证，失败则自动修复并复跑，直到通过或明确受阻。

6. **交付说明**
- 明确哪些步骤已实际执行、哪些是生成的脚本。
- 脚本是否已验证通过，未通过则说明最后一次失败原因。
- 因验证码、SSO、动态数据等外部因素阻塞时，显式标注前置限制。

## 脚本模板结构

生成脚本时，必须按 `assets/playwright-template/` 的目录和文件结构组织：

```
ui_tests/
  auth/
    login_helper.py    # 共享登录步骤（表单登录函数）
  helpers.py            # 通用工具（截图保存等）
  smoke/
    test_login_flow.py  # 登录流程测试
    test_<flow>.py      # 其他业务流程测试
conftest.py               # pytest配置（base_url/credentials/auth_state fixture）
.env.example              # 环境变量示例
requirements.txt          # 依赖声明
screenshots/              # 截图输出目录
```

### 各文件职责

- **conftest.py**：注册 `--base-url`、`--login-url`、`--username`、`--password`、`--storage-state`、`--cookies-file` 命令行选项，提供 `base_url`、`login_url`、`credentials`、`auth_state`、`browser_context_args`、`apply_auth_state` fixture。
- **login_helper.py**：提供 `login_with_password(page, login_url, credentials)` 函数，封装表单登录流程。所有需要登录的测试统一调用此函数。
- **helpers.py**：提供 `save_named_screenshot(page, name)` 函数，截图保存到 `screenshots/` 目录。
- **test_login_flow.py**：登录成功 + 登录后页面验证。
- **test_<flow>.py**：其他业务流程测试，每个独立流程一个文件。

### 替换规则

- 将模板中的 `http://127.0.0.1:3000` 替换为实际测试地址。
- 将 `PLAYWRIGHT_USERNAME` 和 `PLAYWRIGHT_PASSWORD` 替换为实际账号密码。
- 将 `login_helper.py` 中的定位方式（`get_by_label("账号")` 等）替换为实际页面的定位方式。
- 将 `test_login_flow.py` 和 `test_<flow>.py` 中的断言替换为实际页面的断言。
- MCP 执行过程中验证过的稳定定位方式，优先复用到脚本中。

### 运行方式

```bash
pip install -r requirements.txt
playwright install chromium
pytest ui_tests/smoke -v --base-url=http://localhost:5173
```

## 生成原则

- 先验证最关键的主链路，再补边界和异常。
- 优先做高价值断言：可见性、URL 跳转、文案、按钮状态、表单结果。
- 遇到动态加载、动画或弹窗时，用稳妥的等待策略，不依赖固定 sleep。
- 登录态可复用时，优先验证"加载登录态 → 打开目标页 → 断言已登录"这条最短链路。