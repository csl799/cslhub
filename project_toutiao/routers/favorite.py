from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import favorite as favorite_crud
from models.users import User
from schemas.favorite import FavoriteNewsRequest
from utils import response
from utils.auth import get_current_user

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/status")
async def favorite_status(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await favorite_crud.get_favorite_row(db, user.id, news_id)
    return response.success_response(
        message="ok", data={"favorited": row is not None}
    )


@router.post("/add")
async def add_favorite(
    body: FavoriteNewsRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await favorite_crud.add_favorite(db, user.id, body.news_id)
    if res is False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="新闻不存在")
    if res is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="已收藏该新闻")
    return response.success_response(message="收藏成功", data=None)


@router.delete("/remove")
async def remove_favorite(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not await favorite_crud.remove_favorite(db, user.id, news_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未收藏该新闻")
    return response.success_response(message="已取消收藏", data=None)


@router.get("/list")
async def list_favorites(
    page: int = 1,
    page_size: int = Query(10, alias="pageSize", le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    page = max(page, 1)
    offset = (page - 1) * page_size
    items = await favorite_crud.list_favorites(db, user.id, offset, page_size)
    total = await favorite_crud.count_favorites(db, user.id)
    has_more = (offset + len(items)) < total
    return response.success_response(
        message="获取收藏列表成功",
        data={"list": items, "total": total, "hasMore": has_more},
    )


@router.delete("/clear")
async def clear_favorites(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await favorite_crud.clear_favorites(db, user.id)
    return response.success_response(
        message="已清空收藏列表", data={"removed": deleted}
    )
