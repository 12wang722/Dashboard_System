---
name: api-doc-to-pytest
description: 基于接口文档、OpenAPI/Swagger、Postman 集合、curl 示例、截图或 Markdown 接口说明，生成通用的 pytest 接口自动化测试代码与配套数据。适用于"根据接口文档生成 pytest 接口测试用例""把接口说明转成可执行自动化回归用例""快速搭建通用 API 自动化测试骨架"的场景。
---

将接口文档转成可执行的 `pytest` 接口自动化测试代码。

## 工作流

1. **识别输入来源**
- 支持 Swagger/OpenAPI、Postman Collection、Markdown、接口截图、curl 示例、纯文本。
- 只基于用户本次任务显式提供的文档生成，禁止自动读取工作区历史文件。

2. **判断工程形态**
- 有现成工程 → 复用其惯例；无现成基建 → 参考 `assets/project-template/` 生成骨架。

3. **提炼接口清单与缺口**
- 每个接口整理：`模块`、`method`、`path`、`auth`、`request/response schema`、`业务规则`。
- 输出"缺口清单"，关键信息不足先提问，不得强行编造。

4. **生成 pytest 代码**
- 默认 `client + data + tests` 结构，单接口可退化为单文件。
- 覆盖至少 1 条成功 + 2 类失败/边界场景，链路明确时补 1 条链路场景。
- 断言至少覆盖：状态码、成功/失败标记、关键业务字段。
- 依赖登录态的接口抽成 fixture，多非法入参用 `@pytest.mark.parametrize`。
- 交付时说明：文档已给出 vs 推断的部分，缺少环境/账号无法运行时直接说明。

## 生成原则

- 先生成"能跑且容易改"的代码，再追求复杂抽象。
- 默认 `requests + pytest`，断言以稳定字段为主。
- 接口前后依赖用 fixture/helper 处理，文档有示例响应时优先提炼断言锚点。
