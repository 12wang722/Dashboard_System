# 技能名称: RequirementSkill
# 适用角色: 产品设计 Agent

## 核心职责
[cite_start]本能力不仅赋予 Agent 理解现代协作业务场景的能力，更强制其在梳理用户认证、项目管理等需求时必须采用 EARS 格式编写 [cite: 60][cite_start]。它使得 Agent 能够主动追问需求边界，穷举异常分支，并在编写文档前理清系统逻辑的因果关系 。

## 执行红线与约束 (强制遵守)

### 1. 产出物与边界限制
* [cite_start]必须在提议阶段严格配合 OpenSpec 流程，依次产出标准化的 Markdown 制品：`proposal.md`、`specs/*.md` (Delta Specs)、`design.md` 以及 `tasks.md` [cite: 39, 40]。
* [cite_start]**绝对禁止**在提议和需求分析阶段生成任何可执行的源代码 [cite: 61]。

### 2. 强制使用 EARS 语法体系
[cite_start]在编写 `specs/*.md` 规范文档时，必须使用以下五种 EARS 逻辑结构之一来消除自然语言的模糊性，并在输出时加粗触发词 [cite: 48]：
* [cite_start]**无处不在的需求 (Ubiquitous)**: 描述系统始终具备的基础能力。格式：`The <system> shall <response>` [cite: 48]。
* [cite_start]**事件驱动的需求 (Event-driven)**: 描述系统对离散事件的响应。格式：`When <trigger>, the <system> shall <response>` [cite: 48]。
* [cite_start]**状态驱动的需求 (State-driven)**: 描述系统在特定状态下的行为。格式：`While <state>, the <system> shall <response>` [cite: 48]。
* [cite_start]**无用/异常行为需求 (Unwanted)**: 描述系统如何处理错误或冲突。格式：`If <trigger>, then the <system> shall <response>` [cite: 48]。
* [cite_start]**复杂逻辑需求 (Complex)**: 组合状态与事件。格式：`While <state>, When <trigger>, the <system> shall <response>` [cite: 48]。

### 3. 任务拆解颗粒度
[cite_start]在生成 `tasks.md` 时，必须将需求拆解为 5 至 15 个颗粒度极小的实施步骤 [cite: 40][cite_start]。每个步骤必须具有独立可测试性，按依赖关系严格排序（例如：先执行数据库设计，再编写接口），并提供 `-[ ]` 复选框供研发 Agent 追踪 [cite: 40]。