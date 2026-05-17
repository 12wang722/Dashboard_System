---
name: testcase-xmind-generator
description: 分析用户提供的需求描述、需求文档或需求图片，提炼测试点并生成符合规范的可执行测试用例，最终直接输出 .xmind 测试用例脑图。适用于“根据需求生成测试用例并导出 XMind”的场景。
---

根据需求生成可执行测试用例，并直接输出 `.xmind` 文件。

## 工作流

必须严格按照以下工作流顺序执行，禁止跳步、并步或绕过其中任一步骤。

1. 规范化需求输入。
- 支持用户文本、需求文档、需求图片。
- 文件类输入使用 `scripts/extract_requirements.py` 做统一抽取。
- 只允许基于用户在当前任务中显式提供的文本、文件路径、图片或补充说明执行。
- 禁止额外读取 `output/requirements`、历史生成的需求文档、仓库内其他需求文件，除非用户明确要求。
- 禁止把工作区中现有的 `.md/.docx/.png/.json` 需求文件自动视为本次输入。
- 若输入包含图片，必须先做 OCR，再结合图片视觉理解整理需求，不得只基于 OCR 原文直接生成测试用例。
- 在进入用例设计前，必须先生成 1 份中间 Markdown 需求文档：`output/requirements/normalized-requirements.md`。
- 中间 Markdown 需求文档必须体现：功能点、业务规则、状态/流程、异常与边界、非功能结论、待确认问题；若图片包含标注/圈选/箭头/红字说明，必须提炼变更意图。
- 图片视觉理解时，必须按页面用途、区域划分、控件关系、交互入口、状态变化、标注表达的变更意图来整理，不能只罗列 OCR 文本。
- 提炼模块、角色、业务规则、状态、约束、异常路径。

2. 需求熟悉与疑点澄清（必做）。
- 先完整阅读需求并产出“疑点清单”（范围、角色、规则口径、边界、异常、非功能指标、验收标准）。
- 若存在关键信息缺失或歧义，必须先向用户提问并等待补充，不得直接跳过。
- 仅在疑点已澄清或明确记录假设后，才能进入用例设计。
- 必须先拆出“需求条目清单”（模块 -> 功能点 -> 规则点）并编号。
- 使用 `scripts/build_requirements_index.py` 生成条目索引（`R-001...`）。

3. 先执行通用测试设计策略（必做）。
- 在生成任何用例前，必须先按 `references/testcase-design-strategy.md` 完成覆盖思考。
- 至少判断并记录：正向、反向/异常、边界值、等价类、状态流程、场景法、优先级与类型标记。
- 必须显式评估非功能覆盖（安全、性能、兼容、稳定性）；若本次不纳入，必须在输出中写明不纳入原因。
- 若某策略不适用，必须明确写出不适用原因。

4. 生成可执行测试用例。
- 叶子节点必须是可执行用例，不是抽象测试点。
- 每条用例必须包含：`Title`, `Preconditions`, `Steps`, `Expected`, `Priority`, `Type`。

5. 应用覆盖清单。
- 至少覆盖：主流程、校验、边界、状态迁移、权限、异常处理、集成/兼容性。
- 去重并合并语义等价用例。
- 输出中必须体现非功能覆盖结论：已纳入的非功能用例类型，或明确“不纳入+原因”。
- 必须输出“覆盖矩阵”：每个需求条目至少映射 1 条用例；未覆盖条目数必须为 0。

6. 生成 case-tree JSON。
- 层级：`Project -> Module -> Scenario -> Case`。
- 命名规范：
  - Module：名词短语。
  - Scenario：条件 + 动作。
  - Case 标题：`Cxxx [P?] <brief-title>`。
- 生成时强制字段类型：`preconditions`、`steps` 必须为数组（即使只有一条也用数组）。
- 每条用例应包含 `covers`（需求条目ID数组），用于覆盖矩阵校验。
- 生成后必须立即执行 `scripts/normalize_case_tree.py`，确保字段结构标准化。
- 注意：`covers` 仅用于覆盖校验，不导出到 XMind。
- 当 `requirements-index.json` 和 case-tree JSON 都已准备完成后，默认必须调用 `scripts/run_pipeline.py` 作为后续标准执行入口。

7. 导出前执行质量门禁。
- `run_pipeline.py` 默认负责以下固定流程：
  - case-tree 标准化
  - 质量校验
  - 覆盖矩阵生成
  - 覆盖门禁
- 正常执行时，不应手工逐个调用上述脚本。
- 若 `run_pipeline.py` 因覆盖失败或质量门禁失败而中断，必须回到用例编写阶段补齐缺口，再重新调用工作流并执行门禁脚本 `run_pipeline.py`。
- 只有在排错、定位某一步失败原因、或需要局部补跑时，才单独调用内部脚本。

8. 导出 XMind。
- 使用 `scripts/export_xmind.py` 生成 `.xmind`。
- 导出脚本默认生成新旧双格式兼容包（同时包含 `content.json` 与 `content.xml` 相关文件），提升跨版本 XMind 打开成功率。

## 超大需求分模块约束

- 当单次生成无法覆盖全部场景时，允许按模块分批生成并导出多份 XMind。
- 分模块导出前，先使用 `scripts/split_case_tree_by_module.py` 将总 case-tree 按模块拆分。
- 每个模块文件都必须继续以标准工作流执行。
- 分模块导出是执行策略，不是放弃全量覆盖；最终仍需回到总 case-tree 做全量覆盖门禁（未覆盖条目 = 0）。

## 资源使用

- 用例规范：`references/testcase-spec.md`
- 设计策略：`references/testcase-design-strategy.md`
- JSON 示例：`references/case-tree.example.json`
- 输入类型与 OCR 说明：`references/requirement-inputs.md`
- 中间 Markdown 生成脚本：`scripts/build_requirement_markdown.py`
- XMind 模板：`assets/xmind-template.xmind`（默认优先使用）
- 需求抽取脚本：`scripts/extract_requirements.py`
- 需求条目索引脚本：`scripts/build_requirements_index.py`
- case-tree 标准化脚本：`scripts/normalize_case_tree.py`
- 覆盖矩阵脚本：`scripts/build_coverage_matrix.py`
- 覆盖门禁脚本：`scripts/coverage_gate.py`
- case-tree 分模块脚本：`scripts/split_case_tree_by_module.py`
- XMind 导出脚本：`scripts/export_xmind.py`
- 质量校验脚本：`scripts/quality_gate.py`
- 统一流水线主入口：`scripts/run_pipeline.py`

模板来源规则：
- 优先读取环境变量 `XMIND_TEMPLATE_PATH` 指定模板。
- 未指定时使用 `assets/xmind-template.xmind`。
- 不使用仓库外部路径兜底，确保技能可移植。

## 路径约定

- 需求抽取文本默认输出到：`output/requirements/normalized-requirements.txt`
- 中间需求 Markdown 默认输出到：`output/requirements/normalized-requirements.md`
- 结构化用例 JSON 默认输出到：`output/case-tree/case-tree.json`
- 最终 XMind 默认输出到：`output/xmind/<需求名>_<时间戳>.xmind`
- 若用户明确指定路径，优先使用用户路径。

## 命令示例

```powershell
$skillDir = "D:\path\to\testcase-xmind-generator"
$scriptDir = Join-Path $skillDir "scripts"
if (!(Test-Path $scriptDir)) { throw "脚本目录不存在: $scriptDir" }

python "$scriptDir\extract_requirements.py" `
  --input docs/requirement.md docs/ui-requirement.png `
  --output output/requirements/normalized-requirements.txt

python "$scriptDir\build_requirement_markdown.py" `
  --input output/requirements/normalized-requirements.txt `
  --output output/requirements/normalized-requirements.md

python "$scriptDir\run_pipeline.py" `
  --requirements-index output/requirements/requirements-index.json `
  --case-tree output/case-tree/case-tree.json

python "$scriptDir\split_case_tree_by_module.py" `
  --input output/case-tree/case-tree.json `
  --output-dir output/case-tree/modules

python "$scriptDir\run_pipeline.py" `
  --requirements-index output/requirements/requirements-index.json `
  --case-tree output/case-tree/modules/01_Module_A.json
```

## 输出约定

使用该技能完成任务时，输出应包含：
- 中间需求 Markdown 绝对路径。
- 生成的 `.xmind` 绝对路径。
- 覆盖摘要（模块/场景/用例数量）。
- 非功能覆盖摘要（安全/性能/兼容/稳定性是否覆盖，或不覆盖原因）。
- 假设项与未决需求歧义。

## 闭环规则

- 覆盖不全时，不结束任务；必须继续补写用例直到覆盖门禁通过。
- 禁止在覆盖门禁失败状态下导出最终 XMind。
- 禁止在用户未提供对应需求材料时，擅自读取 `output/requirements` 或其他历史需求产物作为补充输入。