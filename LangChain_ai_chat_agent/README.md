# LangChain AI Chat Agent

基于 **FastAPI**、**LangChain / LangGraph** 的网页对话应用：支持工具调用、MySQL 持久化会话状态、用户注册登录（JWT）、多会话与流式输出。

## 功能概览

- **对话（Agent）**：`create_agent` + 系统提示词；工具包括 **Open-Meteo 天气**、**Tavily 联网搜索**（需 API Key）；LangGraph **MySQL Checkpointer** 按 `thread_id` 保存状态；消息条数超阈值时 **摘要中间件** 压缩历史。
- **Web**：静态页 + **SSE** 流式回复；点击历史会话可 **拉取 checkpoint 中的消息记录**。
- **用户**：注册 / 登录（密码 **bcrypt** 哈希存储）、JWT、退出时吊销会话记录；会话列表与 LangGraph `thread_id` 绑定。

## 环境要求

- **Python 3.12+**（`Dockerfile` 使用 3.12；本地建议同主版本）
- **MySQL 8**（本地安装或使用仓库内 `docker-compose`）

## 快速开始（本地）

1. 克隆仓库并进入项目根目录。

2. 复制环境变量模板并编辑：

   ```bash
   cp .env.example .env
   ```

   至少配置：

   | 变量 | 说明 |
   |------|------|
   | `MYSQL_USER` / `MYSQL_PASSWORD` | 连接 MySQL（本地运行时） |
   | `JWT_SECRET_KEY` | JWT 签名密钥（须足够随机） |
   | `DEEPSEEK_API_KEY` 等 | 与所选聊天模型一致（见 LangChain DeepSeek 集成文档） |
   | `TAVILY_API_KEY` | 可选，启用联网搜索 |

3. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

4. 启动 Web 服务：

   ```bash
   python -m web.app
   ```

   浏览器访问：<http://127.0.0.1:8000>

5. （可选）命令行冒烟测试 Agent：

   ```bash
   python main.py
   ```

## Docker Compose

在项目根目录：

```bash
docker compose up --build
```

- 默认 Web：<http://localhost:8000>（可用环境变量 `WEB_PORT` 修改映射）。
- Compose 内 MySQL 的 root 密码默认 **`devroot`**（可用 `MYSQL_ROOT_PASSWORD` 覆盖）；`web` 服务会通过环境变量连接名为 `mysql` 的服务。
- 宿主机映射 MySQL 端口默认为 **`3307:3306`**（`MYSQL_PUBLISH_PORT`，避免与本机已有 3306 冲突）。

若 Docker Desktop 中出现 **多个同名 `web` 容器**，只应保留当前 compose 创建的一组；重复容器抢占 **8000** 会导致其中一个无法启动，可先执行 `docker compose down` 再重新 `up`。

## 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/auth/register` | 注册并返回 JWT |
| `POST` | `/api/auth/login` | 登录 |
| `POST` | `/api/auth/logout` | 吊销当前 JWT |
| `GET` | `/api/auth/me` | 当前用户 |
| `GET` / `POST` | `/api/conversations` | 会话列表 / 新建会话 |
| `GET` | `/api/conversations/{id}/messages` | 该会话 checkpoint 历史消息 |
| `POST` | `/api/chat/stream` | SSE 流式对话（需 Bearer Token） |

请求头：`Authorization: Bearer <access_token>`。

## 目录结构（简要）

```
chat_agent.py          # 创建 Agent、流式与历史消息读取
database/              # LangGraph MySQL checkpoint（PyMySQL）
db/                    # SQLAlchemy 异步模型与引擎（用户、会话、JWT jti）
auth/                  # 注册登录、JWT、密码哈希
web/                   # FastAPI 应用、路由、静态前端
tools/                 # 天气、Tavily 搜索
middleware/            # 摘要中间件
prompts.py             # 系统提示词
main.py                # CLI 示例
Dockerfile
docker-compose.yml
```

## 许可证

未在仓库中统一指定许可证时，默认保留所有权利；如需开源请自行补充 `LICENSE` 文件。
