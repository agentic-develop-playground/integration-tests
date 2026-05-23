# services/calculator_umbrella 模块测试用例清单

> 用例规约 — 描述「单条用例怎么写」，给具体的 case 写作者参考。
> 与同目录的 [`TestStrategy.md`](TestStrategy.md)（整体策略）配套使用。

## 1. 用例命名

`<被测能力>-<前置条件>-<预期结果>`，如 `login-with-wrong-password-returns-401`。

## 2. 每条用例必含字段

| 字段                    | 说明                                                  |
| ----------------------- | ----------------------------------------------------- |
| 用例 ID                 | 全仓唯一，建议带模块前缀，如 `auth.login.001`         |
| 对应 task(issueID) 链接 | `<issue-url>`（指向 backlog 仓 issue）                |
| 前置条件                | 数据 / 环境 / 依赖服务状态                            |
| 操作步骤                | 编号步骤，每步一行                                    |
| 预期结果                | 可观察、可断言（HTTP 状态码 / DB 行数 / 日志内容）    |
| 优先级                  | P0 / P1 / P2                                          |
| 类型                    | smoke / unit / integration / interface contract / e2e |

## 3. 用例分层

- **smoke**：每次 PR 必跑，5 分钟内完成
- **unit (UT)**：覆盖率门禁见团队测试规范
- **interface contract**：跨服务接口契约（Pact / OpenAPI schema 对比）
- **integration**：依赖真实 DB / 真实下游，跑在预览环境
- **e2e**：跑在预览环境，仅核心黄金链路

---

## 4. 全量用例清单

| 用例 ID | 对应 task(issueID) 链接 | 前置条件 | 操作步骤 | 预期结果 | 优先级 | 类型 |
|---------|--------------------------|----------|----------|----------|--------|------|
| sqrt.api.001 | [T-100-01](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端服务已启动，/api/sqrt 端点可访问 | 1. 发送 POST /api/sqrt 请求<br>2. 请求体：`{"value": 16}` | HTTP 200，响应体 `{"result": 4}` | P0 | interface contract |
| sqrt.api.002 | [T-100-01](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端服务已启动，/api/sqrt 端点可访问 | 1. 发送 POST /api/sqrt 请求<br>2. 请求体：`{"value": 2}` | HTTP 200，响应体 `{"result": 1.414213}`（精确到6位小数） | P0 | interface contract |
| sqrt.api.003 | [T-100-01](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端服务已启动，/api/sqrt 端点可访问 | 1. 发送 POST /api/sqrt 请求<br>2. 请求体：`{"value": 0}` | HTTP 200，响应体 `{"result": 0}` | P0 | interface contract |
| sqrt.api.004 | [T-100-01](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端服务已启动，/api/sqrt 端点可访问 | 1. 发送 POST /api/sqrt 请求<br>2. 请求体：`{"value": 1}` | HTTP 200，响应体 `{"result": 1}` | P0 | interface contract |
| sqrt.api.005 | [T-100-01](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端服务已启动，/api/sqrt 端点可访问 | 1. 发送 POST /api/sqrt 请求<br>2. 请求体：`{"value": -1}` | HTTP 400，响应体 `{"error": "value must be non-negative"}` | P0 | interface contract |
| sqrt.api.006 | [T-100-01](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端服务已启动，/api/sqrt 端点可访问 | 1. 发送 POST /api/sqrt 请求<br>2. 请求体：`{"value": "abc"}` | HTTP 400，响应体包含错误信息（非 number 类型校验） | P0 | interface contract |
| sqrt.api.007 | [T-100-01](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端服务已启动，/api/sqrt 端点可访问 | 1. 发送 POST /api/sqrt 请求<br>2. 请求体：`{"value": null}` | HTTP 400，响应体包含错误信息（非 number 类型校验） | P1 | interface contract |
| sqrt.api.008 | [T-100-01](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端服务已启动，/api/sqrt 端点可访问 | 1. 发送 POST /api/sqrt 请求<br>2. 请求体：`{}`（缺参） | HTTP 400，响应体包含错误信息（缺参校验） | P0 | interface contract |
| sqrt.api.009 | [T-100-01](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端服务已启动，/api/sqrt 端点可访问 | 1. 发送 POST /api/sqrt 请求<br>2. 请求体：无请求体 | HTTP 400，响应体包含错误信息（缺参校验） | P1 | interface contract |
| sqrt.api.010 | [T-100-01](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端服务已启动，/api/sqrt 端点可访问 | 1. 发送 POST /api/sqrt 请求<br>2. 请求体：`{"value": NaN}` | HTTP 400，响应体包含错误信息（非 number 类型校验） | P1 | interface contract |
| sqrt.unit.001 | [T-100-02](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端单元测试环境已配置 | 1. 运行单元测试<br>2. 测试用例：value=0 | 断言结果为 0，测试通过 | P0 | unit |
| sqrt.unit.002 | [T-100-02](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端单元测试环境已配置 | 1. 运行单元测试<br>2. 测试用例：value=1 | 断言结果为 1，测试通过 | P0 | unit |
| sqrt.unit.003 | [T-100-02](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端单元测试环境已配置 | 1. 运行单元测试<br>2. 测试用例：value=16 | 断言结果为 4，测试通过 | P0 | unit |
| sqrt.unit.004 | [T-100-02](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端单元测试环境已配置 | 1. 运行单元测试<br>2. 测试用例：value=2 | 断言结果≈1.414214（精确到6位小数），测试通过 | P0 | unit |
| sqrt.unit.005 | [T-100-02](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端单元测试环境已配置 | 1. 运行单元测试<br>2. 测试用例：value=-1（负数） | 断言抛出错误或返回 400 错误信息，测试通过 | P0 | unit |
| sqrt.unit.006 | [T-100-02](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端单元测试环境已配置 | 1. 运行单元测试<br>2. 测试用例：value=NaN | 断言抛出错误或返回 400 错误信息，测试通过 | P1 | unit |
| sqrt.unit.007 | [T-100-02](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端单元测试环境已配置 | 1. 运行单元测试<br>2. 测试用例：缺字段 value | 断言抛出错误或返回 400 错误信息，测试通过 | P1 | unit |
| sqrt.frontend.001 | [T-100-03](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 前端应用已启动，Calculator 组件已加载，后端服务可访问 | 1. 在 Calculator 显示框输入数字 16<br>2. 点击 √ 按钮 | 显示框显示结果 4，无 toast 弹出 | P0 | e2e |
| sqrt.frontend.002 | [T-100-03](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 前端应用已启动，Calculator 组件已加载，后端服务可访问 | 1. 在 Calculator 显示框输入数字 2<br>2. 点击 √ 按钮 | 显示框显示结果≈1.414214（去掉末尾零），无 toast 弹出 | P0 | e2e |
| sqrt.frontend.003 | [T-100-03](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 前端应用已启动，Calculator 组件已加载，后端服务可访问 | 1. 在 Calculator 显示框输入数字 -1<br>2. 点击 √ 按钮 | 弹出 toast 提示"value must be non-negative"，显示框不被污染（保持原值或清空） | P0 | e2e |
| sqrt.frontend.004 | [T-100-03](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 前端应用已启动，Calculator 组件已加载 | 1. 观察 Calculator 组件布局<br>2. 确认 √ 按钮位置 | √ 按钮位于百分比按钮旁，图标清晰可识别，可点击 | P1 | e2e |
| sqrt.integration.001 | [T-100-03](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 前端应用已启动，后端服务已启动，网络连通 | 1. 前端输入数字 16 并点击 √ 按钮<br>2. 捕获前端发出的 HTTP 请求<br>3. 检查后端响应 | 前端发送 POST /api/sqrt 请求体 `{"value": 16}`，后端返回 HTTP 200 `{"result": 4}`，前端显示框更新为 4 | P0 | integration |
| sqrt.integration.002 | [T-100-03](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 前端应用已启动，后端服务已启动，网络连通 | 1. 前端输入数字 -5 并点击 √ 按钮<br>2. 捕获前端发出的 HTTP 请求<br>3. 检查后端响应 | 前端发送 POST /api/sqrt 请求体 `{"value": -5}`，后端返回 HTTP 400 `{"error": "value must be non-negative"}`，前端弹出 toast 提示 | P0 | integration |
| sqrt.openapi.001 | [T-100-04](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | OpenAPI schema 文件已更新 | 1. 打开 OpenAPI schema 文件<br>2. 检查 /api/sqrt 端点定义 | schema 包含 /api/sqrt POST 端点，定义请求体 schema 和响应体 schema | P1 | interface contract |
| sqrt.e2e.001 | [T-100-05](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 前端应用已启动，后端服务已启动，端到端环境已就绪 | 1. 打开 Calculator 应用<br>2. 输入数字 16<br>3. 点击 √ 按钮<br>4. 观察显示框结果 | 显示框显示结果 4，整个流程无错误，响应及时 | P0 | e2e |
| sqrt.e2e.002 | [T-100-05](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 前端应用已启动，后端服务已启动，端到端环境已就绪 | 1. 打开 Calculator 应用<br>2. 输入数字 -1<br>3. 点击 √ 按钮<br>4. 观察 toast 提示和显示框 | 弹出 toast 提示错误信息，显示框不被污染 | P0 | e2e |
| sqrt.e2e.003 | [T-100-05](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 前端应用已启动，后端服务已启动，端到端环境已就绪 | 1. 打开 Calculator 应用<br>2. 输入数字 0<br>3. 点击 √ 按钮<br>4. 观察显示框结果 | 显示框显示结果 0，整个流程无错误 | P1 | e2e |
| sqrt.perf.001 | [T-100-01](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端服务已启动，性能测试工具已配置 | 1. 发送单次 POST /api/sqrt 请求，请求体 `{"value": 16}`<br>2. 记录响应时间<br>3. 重复10次取平均值 | 平均响应时间 < 1ms | P1 | interface contract |
| sqrt.perf.002 | [T-100-01](https://github.com/agentic-develop-playground/calculator-umbrella/issues/100) | 后端服务已启动，性能测试工具已配置 | 1. 使用工具模拟10并发请求 POST /api/sqrt，请求体 `{"value": <随机非负数>}`<br>2. 记录 P99 延迟 | P99 延迟 < 10ms，无错误响应 | P1 | interface contract |

---

## 5. 关联

- 整体策略写法 → [`TestStrategy.md`](TestStrategy.md)
- 测试经验沉淀 → 团队知识库
- 通用流水线测试编排 → 团队测试规范