import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

ASYNC_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4",
)

_echo = os.getenv("SQLALCHEMY_ECHO", "true").lower() in ("1", "true", "yes")

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=_echo,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db_schema() -> None:
    """若表不存在则按 ORM 建表；不删数据、不做结构迁移。"""
    import models.news  # noqa: F401
    import models.users  # noqa: F401
    from models.news import Base as NewsBase
    from models.users import Base as UsersBase

    async with async_engine.begin() as conn:
        await conn.run_sync(NewsBase.metadata.create_all)
        await conn.run_sync(UsersBase.metadata.create_all)
