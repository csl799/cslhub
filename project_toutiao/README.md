# 新闻阅读项目（FastAPI + Vue）

Docker 部署时**不会自带 MySQL 容器**：后端通过 `host.docker.internal` 连接**宿主机本机已安装的 MySQL**，因此新闻、分类等数据都在面试官（或你）**自己维护的数据库里**，与是否用 Docker 无关。

---

## 面试官：一键看全栈

### 1. 准备本机 MySQL

- 已安装并启动 MySQL，库名需与连接串一致（默认 **`news_app`**，可在 `.env` 里改）。
- 若你克隆的是他人仓库，请让对方提供 **`mysqldump` 导出文件**，导入后再启动容器（见下文「数据迁移」）。
- 若只是空库想先跑通页面，可**手工**在 MySQL 里执行 `sql/optional_demo_seed.sql`（会删表重建，**勿在有数据的库上执行**）。

### 2. 配置数据库连接

```bash
cp .env.example .env
```

编辑 `.env`，把 `DATABASE_URL` 里的 **用户名、密码、库名** 改成与本机 MySQL 一致。

### 3. 启动 Docker

在项目根目录：

```bash
docker compose up --build -d
```

### 4. 访问

| 说明           | 地址 |
|----------------|------|
| **整站（前端）** | <http://localhost:8080> |
| **接口文档**     | <http://localhost:8000/docs> |

前端通过 Nginx 把浏览器请求 **`/api/*`** 转发到容器内的后端，无需再配 Vite 代理。

### 5. MySQL 连不上时

- 确认本机 MySQL 已启动，且存在对应库。
- Windows / Mac 使用 **Docker Desktop** 时，`host.docker.internal` 一般可用。
- 若仍 `Connection refused`，多半是 MySQL 只监听了 `127.0.0.1`：可将 `my.cnf` 里 `bind-address` 改为 `0.0.0.0`（仅限本机调试，生产请改回并做好权限）。

### 6. 停止

```bash
docker compose down
```

---

## 作者：把本地新闻数据交给面试官

在本机（有完整数据时）导出：

```bash
mysqldump -u root -p --databases news_app > news_app_backup.sql
```

将 `news_app_backup.sql` 与项目一并交给对方；对方在本机 MySQL 执行：

```bash
mysql -u root -p < news_app_backup.sql
```

再按上文配置 `.env` 并 `docker compose up` 即可看到你的新闻数据。

---

## 本地开发（不用 Docker）

- **后端**：`pip install -r requirements.txt`，配置 `config/db_config.py` 或环境变量 `DATABASE_URL`，执行 `uvicorn main:app --reload --host 127.0.0.1 --port 8000`。
- **前端**：`cd frontend && npm install && npm run dev`（开发时 Vite 会把 `/api` 代理到 `127.0.0.1:8000`）。

---

## 环境变量说明

| 变量 | 含义 |
|------|------|
| `DATABASE_URL` | 异步 MySQL 连接串，Docker 内请使用主机名 **`host.docker.internal`** 指向宿主机。 |
| `SQLALCHEMY_ECHO` | `true` / `false`，是否打印 SQL。 |

---

## 其他 SQL 文件

- `sql/user_favorite.sql`：仅收藏表时参考或补表。
- `sql/optional_demo_seed.sql`：**可选**空库演示，执行前请确认无重要数据。
