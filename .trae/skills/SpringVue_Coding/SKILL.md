# 技能名称: SpringVueArchitect
# 适用场景: 当系统进入 openspec-apply-change 阶段，开始实质性修改代码时触发。

## 核心职责
确保 R&D Agent 生成的代码绝对符合团队制定的 Spring Boot 3 + Vue 3 技术底座。

## 执行红线（强制约束）
1. **前端隔离**：涉及前端界面（如看板拖拽），必须使用 Vue 3 的 Composition API (`<script setup>`)，拖拽逻辑强制依赖 `vuedraggable`，状态管理使用 Pinia。
2. **后端隔离**：控制器必须符合 RESTful 规范，安全层强制集成 Spring Security + JWT，禁止使用 Session。
3. **实时通信**：涉及看板卡片位置变更的需求，必须同时生成 WebSocket 推送逻辑，确保多端状态同步。
4. **单步执行协议**：在实现 `tasks.md` 时，禁止“跳步”合并提交，完成一个 Task 必须打勾 `-[x]` 并记录 AI 日志。