# 新闻阅读（FastAPI + Vue）

Docker 不包含 MySQL：后端通过 `host.docker.internal` 连**本机 MySQL**，数据由本机库维护。

## Docker

1. 本机安装 MySQL，建好库（默认 `news_app`，可在 `.env` 改）。
2. `cp .env.example .env`，按本机改 `DATABASE_URL`。
3. 根目录执行：`docker compose up --build -d`
4. 前端 <http://localhost:8080>，Swagger <http://localhost:8000/docs>  
   停止：`docker compose down`

克隆他人仓库要对方数据时：索要 `mysqldump` 备份，本机 `mysql < backup.sql` 导入后再起容器。空库可选手工执行 `sql/optional_demo_seed.sql`（会删表，勿在有数据环境执行）。

连不上库：确认 MySQL 已启动；Docker Desktop 下 `host.docker.internal` 一般可用；若仍拒绝连接，检查 `bind-address` 是否仅监听 127.0.0.1（调试可临时改为 0.0.0.0）。

## 本地开发

- 后端：`pip install -r requirements.txt`，配 `DATABASE_URL` 或 `config/db_config.py` 默认串，`uvicorn main:app --reload --host 127.0.0.1 --port 8000`
- 前端：`cd frontend && npm install && npm run dev`（`/api` 代理到 8000）

## 环境变量

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | 如 `mysql+aiomysql://root:密码@host:3306/news_app?charset=utf8mb4` |
| `SQLALCHEMY_ECHO` | `true` / `false` |

## SQL

- `sql/user_favorite.sql`：单独建收藏表时可参考。
- `sql/optional_demo_seed.sql`：空库示例数据（慎用）。
