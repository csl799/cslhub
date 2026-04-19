from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import crud

from config.db_config import get_db
from schemas.users import UserRequest, UserAuthResponse, UserInfoBase, UserInfoResponse
from crud import users
from utils import response

router = APIRouter(prefix="/api/user",tags=["users"])


@router.post("/register")
async def register(user_data:UserRequest,db:AsyncSession = Depends(get_db)):# 用户信息和db
    # 验证用户是否存在 创建用户 生产token访问令牌 响应访问结果
    existing_user = await users.get_by_username(db, username=user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="用户已存在")
    user = await users.create_user(db,user_data)
    token = await users.create_token(db,user.id)
    response_data = UserAuthResponse(token=token,userInfo=UserInfoResponse.model_validate(user))
    return response.success_response(message="注册成功",data=response_data)