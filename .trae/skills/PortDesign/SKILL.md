# 技能名称: PortDesignSkill
# 适用角色: 研发 Agent

## 核心职责
规范系统内外的数据交换契约，包括 HTTP API 与 WebSocket 协议设计。

## 执行红线与约束
1. **RESTful 标准**：所有后端的 Controller 接口必须符合 RESTful 规范，明确定义请求体、响应体及标准的 HTTP 状态码（200, 400, 401, 403, 404, 500）。
2. **实时通信契约**：涉及“看板卡片拖拽”等状态机变更的需求，必须设计严密的 WebSocket 消息载荷（Payload）协议，确保前端 Vue Draggable 与后端的双向状态一致。
3. **安全鉴权**：接口必须设计集成基于 JWT 的无状态认证拦截规则。