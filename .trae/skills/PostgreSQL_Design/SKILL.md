# 技能名称: PgSQLDatabaseDesigner
# 适用场景: 在 propose 或 explore 阶段生成 design.md，涉及数据模型调整时触发。

## 核心职责
规划高扩展性、高并发的关系型数据库表结构。

## 执行红线（强制约束）
1. **引擎锁定**：所有 DDL 语句和 ORM 实体（JPA/MyBatis-Plus）必须针对 PostgreSQL 进行优化。
2. **扩展字段预留**：对于“任务详情(Task)”等极易变动的表，必须包含一个 `JSONB` 类型的字段（如 `extension_props`），以容纳未来的自定义字段，避免频繁 Alter Table。
3. **审计追踪**：所有核心业务表（用户、项目、任务）必须强制包含：`created_at`, `updated_at`, `created_by`, `updated_by` 四个审计字段。