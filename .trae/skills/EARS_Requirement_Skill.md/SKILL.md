# 技能名称: EARSSyntaxEnforcer
# 适用场景: 当用户执行 OpenSpec 的 propose 或 explore 阶段时，用于规范业务逻辑描述。

## 核心职责
在生成 `specs/*.md` 或 `proposal.md` 之前，强制审查需求描述是否无歧义，并转换为 EARS 语法体系。

## 执行红线（强制约束）
1. **禁用模糊语义**：禁止使用“可能”、“大概”、“尽量快速”等不可测试的词汇。
2. **强制使用 EARS 句式**：
   - 基础响应: "The <system> shall <response>"
   - 事件触发: "When <trigger>, the <system> shall <response>" 
   - 状态依赖: "While <state>, the <system> shall <response>"
   - 异常处理: "If <trigger>, then the <system> shall <response>"
3. **输出格式**：在输出需求时，必须加粗标注 EARS 关键字（如 **When**, **shall**）。