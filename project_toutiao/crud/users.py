import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils import security


async def get_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserRequest):
    hashed = security.get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_token(db: AsyncSession, user_id: int):
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    result = await db.execute(select(UserToken).where(UserToken.user_id == user_id))
    row = result.scalar_one_or_none()
    if row:
        row.token = token
        row.expires_at = expires_at
    else:
        db.add(UserToken(user_id=user_id, token=token, expires_at=expires_at))
    await db.commit()
    return token


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_by_username(db, username)
    if not user or not security.verify_password(password, user.password):
        return None
    return user


async def get_user_by_token(db: AsyncSession, token: str):
    result = await db.execute(select(UserToken).where(UserToken.token == token))
    row = result.scalar_one_or_none()
    if not row or row.expires_at < datetime.now():
        return None
    result = await db.execute(select(User).where(User.id == row.user_id))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    payload = user_data.model_dump(exclude_none=True, exclude_unset=True)
    result = await db.execute(
        update(User).where(User.username == username).values(**payload)
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")
    return await get_by_username(db, username)


async def update_password(
    db: AsyncSession, user: User, old_password: str, new_password: str
):
    if not security.verify_password(old_password, user.password):
        return False
    user.password = security.get_hash_password(new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True
