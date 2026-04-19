from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func,update
from models.news import Category,News



async def get_categories(db:AsyncSession,skip: int = 0,limit: int = 100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()



async def get_news_list(db:AsyncSession,category_id: int,skip: int = 0,limit: int = 100):
    # 查询指定分类下的所有新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()



async def get_news_count(db:AsyncSession,category_id:int):
    # 查询指定分类下的新闻数量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one() # 只能有一个结果，否则报错



async def get_news_detail(db:AsyncSession,news_id: int):
    # 查询某个新闻的详细内容
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()



async def increase_news_views(db:AsyncSession,news_id: int):
    # 更新浏览量
    stmt = update(News).where(News.id == news_id).values(views = News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    # 数据库的更新 检查数据库是否真的命中了数据 命中了返回True
    return result.rowcount > 0



async def related_news(db:AsyncSession,category_id:int,news_id: int,limit:int = 5):
    # 查询同类的其他新闻,按浏览量和发布时间前五
    stmt = select(News).where(
        News.id != news_id,
        News.category_id == category_id
    ).order_by(News.views.desc(),
               News.publish_time.desc()).limit(limit)
    result = await db.execute(stmt)
    # return result.scalars().all()
    related_news = result.scalars().all()
    # 列表推导式 推导出新闻的核心数据 然后再return
    return [{
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "image": news.image,
        "author": news.author,
        "publishTime": news.publish_time,
        "category": news.category_id,
        "views": news.views,
    } for news in related_news]