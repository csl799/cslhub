from __future__ import annotations

import asyncio

import bcrypt

# bcrypt 仅支持最多 72 字节口令；按 UTF-8 截断，避免多字节字符被截断一半


def _password_bytes(plain: str) -> bytes:
    if not isinstance(plain, str):
        plain = str(plain)
    return plain.encode("utf-8")[:72]


async def hash_password(plain: str) -> str:

    def _run() -> str:
        return bcrypt.hashpw(_password_bytes(plain), bcrypt.gensalt()).decode("ascii")

    return await asyncio.to_thread(_run)


async def verify_password(plain: str, hashed: str) -> bool:

    def _run() -> bool:
        try:
            return bcrypt.checkpw(_password_bytes(plain), hashed.encode("ascii"))
        except (ValueError, TypeError):
            return False

    return await asyncio.to_thread(_run)
