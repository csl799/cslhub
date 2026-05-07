from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.service import validate_token
from db.models import User
from db.session import get_session

security = HTTPBearer()


async def get_current_user_id(
    creds: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> int:
    try:
        uid, _jti = await validate_token(session, creds.credentials)
        return uid
    except Exception:
        raise HTTPException(status_code=401, detail="未登录或 token 无效") from None


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> User:
    r = await session.execute(select(User).where(User.id == user_id))
    u = r.scalar_one_or_none()
    if u is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return u
