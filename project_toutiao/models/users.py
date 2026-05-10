from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    __table_args__ = (
        Index("username_UNIQUE", "username"),
        Index("phone_UNIQUE", "phone"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="用户ID"
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="用户名"
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码(加密储存)"
    )
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment="昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), comment="头像URL")
    gender: Mapped[Optional[str]] = mapped_column(
        Enum("male", "female", "unknown"), comment="性别"
    )
    bio: Mapped[Optional[str]] = mapped_column(
        String(500),
        default="这个人很懒，什么都没有留下",
        comment="个人简介",
    )
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, comment="手机号")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )


class UserToken(Base):
    __tablename__ = "user_token"

    __table_args__ = (
        Index("token_UNIQUE", "token"),
        Index("fk_user_token_user_idx", "user_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="令牌ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(User.id), nullable=False, comment="用户ID"
    )
    token: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, comment="令牌值"
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="创建时间"
    )


class UserFavorite(Base):
    """用户收藏；news_id 外键在库表维护。"""

    __tablename__ = "user_favorite"

    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="uk_user_news_favorite"),
        Index("idx_user_favorite_user_id", "user_id"),
        Index("idx_user_favorite_news_id", "news_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="收藏记录ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="用户ID"
    )
    news_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="新闻ID")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="收藏时间"
    )
