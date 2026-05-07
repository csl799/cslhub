"""从环境变量拼 MySQL 异步连接 URL（与 checkpoint 使用同一库名）。"""

from __future__ import annotations

import os
import re
from urllib.parse import quote_plus


def require_env(name: str) -> str:
    v = os.getenv(name)
    if not v or not str(v).strip():
        raise ValueError(f"请在 .env 中设置非空的 {name}")
    return str(v).strip()


def mysql_database() -> str:
    db = os.getenv("MYSQL_DATABASE", "langgraph_checkpoint").strip()
    if not re.fullmatch(r"[A-Za-z0-9_]+", db):
        raise ValueError("MYSQL_DATABASE 只能包含字母、数字、下划线")
    return db


def async_database_url() -> str:
    host = os.getenv("MYSQL_HOST", "localhost").strip()
    port = os.getenv("MYSQL_PORT", "3306").strip() or "3306"
    user = quote_plus(require_env("MYSQL_USER"))
    password = quote_plus(os.getenv("MYSQL_PASSWORD") or "")
    db = quote_plus(mysql_database())
    return f"mysql+asyncmy://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4"
