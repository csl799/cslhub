from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt

_ALG = "HS256"


def _secret() -> str:
    s = os.getenv("JWT_SECRET_KEY", "").strip()
    if not s:
        raise ValueError("请在 .env 中设置 JWT_SECRET_KEY（用于签发登录 token）")
    return s


def token_ttl_hours() -> int:
    return int(os.getenv("JWT_EXPIRE_HOURS", "168").strip() or "168")


def create_access_token(user_id: int, jti: str) -> tuple[str, datetime]:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=token_ttl_hours())
    payload = {
        "sub": str(user_id),
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, _secret(), algorithm=_ALG)
    return token, exp


def decode_token(token: str) -> dict:
    return jwt.decode(token, _secret(), algorithms=[_ALG])


def new_jti() -> str:
    return str(uuid.uuid4())
