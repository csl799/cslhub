"""Checkpoint 持久化：本地 MySQL，自动建库并调用 LangGraph `PyMySQLSaver.setup()` 建表。"""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from urllib.parse import quote_plus


def _require_env(name: str) -> str:
    v = os.getenv(name)
    if not v or not str(v).strip():
        raise ValueError(f"请在环境变量或 .env 中设置非空的 {name}")
    return str(v).strip()


def _mysql_database_name() -> str:
    db = os.getenv("MYSQL_DATABASE", "langgraph_checkpoint").strip()
    if not re.fullmatch(r"[A-Za-z0-9_]+", db):
        raise ValueError(
            "MYSQL_DATABASE 只能包含字母、数字、下划线；当前值无效或存在注入风险。"
        )
    return db


def _mysql_connect_params(*, with_database: bool) -> dict[str, Any]:
    host = os.getenv("MYSQL_HOST", "localhost").strip()
    port_raw = os.getenv("MYSQL_PORT", "3306").strip() or "3306"
    port = int(port_raw)
    user = _require_env("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD") or ""
    params: dict[str, Any] = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "autocommit": True,
    }
    if with_database:
        params["database"] = _mysql_database_name()
    return params


def _normalize_mysql_checkpoint_collation() -> None:
    """统一库与 checkpoint 表的校对规则为 utf8mb4_0900_ai_ci，避免 MySQL 1267。"""
    import pymysql

    db = _mysql_database_name()
    params = _mysql_connect_params(with_database=True)
    conn = pymysql.connect(**params)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"ALTER DATABASE `{db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
            )
            cur.execute(
                """
                SELECT TABLE_NAME FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
                  AND TABLE_NAME IN (
                      'checkpoint_migrations', 'checkpoints',
                      'checkpoint_blobs', 'checkpoint_writes'
                  )
                """,
                (db,),
            )
            for (table_name,) in cur.fetchall():
                cur.execute(
                    f"ALTER TABLE `{table_name}` CONVERT TO CHARACTER SET utf8mb4 "
                    "COLLATE utf8mb4_0900_ai_ci"
                )
    finally:
        conn.close()


def _ensure_mysql_database_exists() -> None:
    import pymysql

    params = _mysql_connect_params(with_database=False)
    db = _mysql_database_name()
    conn = pymysql.connect(**params)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
            )
    finally:
        conn.close()


def _build_mysql_conn_string() -> str:
    p = _mysql_connect_params(with_database=True)
    user = quote_plus(p["user"])
    password = quote_plus(p["password"])
    host = p["host"]
    port = p["port"]
    db = _mysql_database_name()
    return f"mysql://{user}:{password}@{host}:{port}/{db}"


@contextmanager
def checkpoint_lifecycle() -> Iterator[Any]:
    """
    确保数据库存在 → 校对规则一致 → `setup()` 建表 → yield checkpointer。

    环境变量：MYSQL_USER（必填）、MYSQL_PASSWORD、MYSQL_DATABASE、MYSQL_HOST、MYSQL_PORT。
    """
    from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver

    _ensure_mysql_database_exists()
    _normalize_mysql_checkpoint_collation()
    uri = _build_mysql_conn_string()
    with PyMySQLSaver.from_conn_string(uri) as saver:
        saver.setup()
        yield saver
