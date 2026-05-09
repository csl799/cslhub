from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import News
from models.users import UserFavorite


async def get_favorite_row(db: AsyncSession, user_id: int, news_id: int):
    stmt = select(UserFavorite).where(
        UserFavorite.user_id == user_id,
        UserFavorite.news_id == news_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def news_exists(db: AsyncSession, news_id: int) -> bool:
    stmt = select(func.count(News.id)).where(News.id == news_id)
    result = await db.execute(stmt)
    return (result.scalar_one() or 0) > 0


async def add_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    if not await news_exists(db, news_id):
        return False
    if await get_favorite_row(db, user_id, news_id):
        return None
    row = UserFavorite(user_id=user_id, news_id=news_id)
    db.add(row)
    await db.flush()
    return True


async def remove_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    stmt = delete(UserFavorite).where(
        UserFavorite.user_id == user_id,
        UserFavorite.news_id == news_id,
    )
    result = await db.execute(stmt)
    return result.rowcount > 0


async def count_favorites(db: AsyncSession, user_id: int) -> int:
    stmt = select(func.count(UserFavorite.id)).where(UserFavorite.user_id == user_id)
    result = await db.execute(stmt)
    return int(result.scalar_one() or 0)


async def list_favorites(
    db: AsyncSession, user_id: int, offset: int, limit: int
):
    stmt = (
        select(News, UserFavorite.created_at)
        .join(UserFavorite, UserFavorite.news_id == News.id)
        .where(UserFavorite.user_id == user_id)
        .order_by(UserFavorite.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "id": news.id,
            "title": news.title,
            "description": news.description,
            "image": news.image,
            "author": news.author,
            "publishTime": news.publish_time,
            "categoryId": news.category_id,
            "views": news.views,
            "favoritedAt": favorited_at,
        }
        for news, favorited_at in rows
    ]


async def clear_favorites(db: AsyncSession, user_id: int) -> int:
    stmt = delete(UserFavorite).where(UserFavorite.user_id == user_id)
    result = await db.execute(stmt)
    return int(result.rowcount or 0)
