\# AI驱动的智能任务协同看板系统技术设计文档

\## 1. 技术栈

\- 前端: Vue 3 (Composition API) + Vue Draggable + Tailwind CSS

\- 后端: Spring Boot 3 + Spring AI + Spring Security

\- 数据库: PostgreSQL 16 + Redis

\- 通信: WebSocket (STOMP) + RESTful API

\- 认证: JWT (JSON Web Token)



\## 2. 数据库表结构设计

\### 2.1 users表

```sql

CREATE TABLE users (

&#x20;   id BIGSERIAL PRIMARY KEY,

&#x20;   email VARCHAR(255) NOT NULL UNIQUE,

&#x20;   password VARCHAR(255) NOT NULL,

&#x20;   username VARCHAR(100) NOT NULL,

&#x20;   avatar\_url VARCHAR(255),

&#x20;   created\_at TIMESTAMP NOT NULL DEFAULT CURRENT\_TIMESTAMP,

&#x20;   updated\_at TIMESTAMP NOT NULL DEFAULT CURRENT\_TIMESTAMP

);

