from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt_utils import create_access_token, new_jti
from auth.passwords import hash_password, verify_password
from db.models import AuthSession, Conversation, User

_USERNAME_RE = re.compile(r"^[A-Za-z0-9_\u4e00-\u9fff]{3,32}$")


def _utc_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def issue_token_for_user(session: AsyncSession, user_id: int) -> tuple[str, datetime]:
    jti = new_jti()
    token, exp = create_access_token(user_id, jti)
    exp_naive = exp.astimezone(timezone.utc).replace(tzinfo=None)
    session.add(AuthSession(user_id=user_id, jti=jti, expires_at=exp_naive))
    await session.commit()
    return token, exp


async def register_user(session: AsyncSession, username: str, password: str) -> tuple[User, str, datetime]:
    u = username.strip()
    if not _USERNAME_RE.fullmatch(u):
        raise ValueError("用户名须为 3～32 位，仅字母、数字、下划线或中文")
    h = await hash_password(password)
    user = User(username=u, password_hash=h)
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ValueError("用户名已存在") from None
    await session.refresh(user)
    token, exp = await issue_token_for_user(session, user.id)
    return user, token, exp


async def login_user(session: AsyncSession, username: str, password: str) -> tuple[str, datetime]:
    r = await session.execute(select(User).where(User.username == username.strip()))
    user = r.scalar_one_or_none()
    if user is None or not await verify_password(password, user.password_hash):
        raise ValueError("用户名或密码错误")
    return await issue_token_for_user(session, user.id)


async def revoke_session(session: AsyncSession, jti: str) -> None:
    await session.execute(update(AuthSession).where(AuthSession.jti == jti).values(revoked=True))
    await session.commit()


async def validate_token(session: AsyncSession, token: str) -> tuple[int, str]:
    from auth.jwt_utils import decode_token

    data = decode_token(token)
    uid = int(data["sub"])
    jti = data["jti"]
    r = await session.execute(
        select(AuthSession).where(AuthSession.jti == jti, AuthSession.user_id == uid)
    )
    row = r.scalar_one_or_none()
    if row is None or row.revoked:
        raise ValueError("token 已失效")
    if row.expires_at < _utc_naive():
        raise ValueError("token 已过期")
    return uid, jti


async def list_conversations(session: AsyncSession, user_id: int) -> list[Conversation]:
    r = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return list(r.scalars().all())


async def create_conversation(session: AsyncSession, user_id: int, title: str = "新会话") -> Conversation:
    tid = str(uuid.uuid4())
    c = Conversation(user_id=user_id, thread_id=tid, title=title[:255])
    session.add(c)
    await session.commit()
    await session.refresh(c)
    return c


async def get_owned_conversation(session: AsyncSession, user_id: int, conv_id: int) -> Conversation | None:
    r = await session.execute(
        select(Conversation).where(Conversation.id == conv_id, Conversation.user_id == user_id)
    )
    return r.scalar_one_or_none()


async def touch_conversation(session: AsyncSession, conv_id: int) -> None:
    await session.execute(
        update(Conversation).where(Conversation.id == conv_id).values(updated_at=_utc_naive())
    )
    await session.commit()


async def set_conversation_title_if_default(session: AsyncSession, conv_id: int, first_message: str) -> None:
    t = first_message.strip().replace("\n", " ")[:80]
    if not t:
        return
    await session.execute(
        update(Conversation)
        .where(Conversation.id == conv_id, Conversation.title == "新会话")
        .values(title=t, updated_at=_utc_naive())
    )
    await session.commit()
