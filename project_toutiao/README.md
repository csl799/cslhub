# 新闻阅读（FastAPI + Vue）

Docker 不包含 MySQL：后端通过 `host.docker.internal` 连**本机 MySQL**，数据由本机库维护。

## Docker

1. 本机安装 MySQL，**创建空库**（默认名 `news_app`，与 `DATABASE_URL` 一致即可）。
2. `cp .env.example .env`，按本机改 `DATABASE_URL`。
3. 根目录执行：`docker compose up --build -d`  
   后端启动时会按 ORM **自动创建尚未存在的表**（不删数据、不改已有表结构）。
4. 前端 <http://localhost:8080>，Swagger <http://localhost:8000/docs>  
   停止：`docker compose down`

空库首次启动后表是空的，新闻/分类需自行导入或执行 `sql/optional_demo_seed.sql`（会删表，慎用）。有现成数据时用 `mysqldump` 导入即可。

连不上库：确认 MySQL 已启动；Docker Desktop 下 `host.docker.internal` 一般可用；若仍拒绝连接，检查 `bind-address` 是否仅监听 127.0.0.1（调试可临时改为 0.0.0.0）。

## 本地开发

- 后端：`pip install -r requirements.txt`，配 `DATABASE_URL` 或 `config/db_config.py` 默认串，`uvicorn main:app --reload --host 127.0.0.1 --port 8000`
- 前端：`cd frontend && npm install && npm run dev`（`/api` 代理到 8000）

## 环境变量

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | 如 `mysql+aiomysql://root:密码@host:3306/news_app?charset=utf8mb4` |
| `SQLALCHEMY_ECHO` | `true` / `false` |

## SQL（可选）

- `sql/user_favorite.sql`：若曾用手工建表，可与 ORM 对照；一般启动时已自动建表则不必执行。
- `sql/optional_demo_seed.sql`：空库写入示例分类与新闻（会删表，慎用）。
