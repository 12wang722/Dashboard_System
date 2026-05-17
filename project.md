# 智能任务协同看板项目 - 技术宪法 (Project Constitution)

## 1. 核心技术栈锁定
本系统所有代码生成与架构设计必须严格遵守以下技术选型，任何 Agent 不得擅自引入其他替代框架：
* [cite_start]**前端架构**：强制使用 Vue 3 结合 Vue Draggable (基于 Sortable.js 的封装) 来构建高响应式的组件化界面 [cite: 10]。
* [cite_start]**后端微服务**：强制使用 Spring Boot 3，并深度集成 Spring AI 模块以驱动后端的智能化能力 [cite: 11]。
* [cite_start]**数据持久化**：必须使用 PostgreSQL 作为关系型数据库，用于持久化用户实体、项目元数据及任务状态轨迹 [cite: 16][cite_start]。支持 JSONB 等灵活数据类型以存储扩展字段 [cite: 17]。

## 2. 架构与通信红线
* [cite_start]**实时状态同步**：系统是一个复杂的状态机，界面拖拽必须与底层状态保持一致 [cite: 10][cite_start]。必须通过 WebSocket 维持多客户端的实时状态同步 [cite: 16, 17]。
* [cite_start]**安全与认证**：前端使用 Vue Router 路由守卫，后端强制通过 JWT (JSON Web Tokens) 实现无状态用户认证 [cite: 11, 17]。
* [cite_start]**缓存机制**：统一禁止使用本地缓存，必须强制依赖 Redis 等架构级硬约束来进行状态管理与缓存 。

## 3. 需求规范约束 (SDD)
* [cite_start]**语法强制**：产品设计 Agent 在输出 `specs/*.md` 规范文档时，必须严格使用 EARS (简化需求语法框架) [cite: 46, 47]。
* [cite_start]**无歧义性**：所有业务逻辑必须使用诸如 "The <system> shall <response>" 或 "When <trigger>, the <system> shall <response>" 的模式编写，以确保测试 Agent 能够无歧义地逆向解析出测试用例 [cite: 48, 74]。

## 4. Agent 行为与边界隔离
* [cite_start]**产品设计 Agent**：在提议阶段（Propose）利用 OpenSpec 规范层 Skill 输出 `proposal.md` 和 `tasks.md` 时，**绝对禁止**生成任何可执行的源代码 [cite: 61]。
* [cite_start]**研发 Agent**：在 SOLO 模式下编码时，必须严格按照 `tasks.md` 中的步骤顺序**单步执行**，并在完成每一步后主动在 `tasks.md` 中打钩标记完成 (`-[x]`)，严禁跳跃式重构 [cite: 71, 95]。

