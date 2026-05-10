from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import users
from models.users import User
from schemas.users import (
    UserAuthResponse,
    UserChangePasswordRequest,
    UserInfoResponse,
    UserRequest,
    UserUpdateRequest,
)
from utils import response
from utils.auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    existing_user = await users.get_by_username(db, username=user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户已存在")

    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(
        token=token, userInfo=UserInfoResponse.model_validate(user)
    )
    return response.success_response(message="注册成功", data=response_data)


@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(
        token=token, userInfo=UserInfoResponse.model_validate(user)
    )
    return response.success_response(message="登录成功", data=response_data)


@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return response.success_response(
        message="获取用户信息成功", data=UserInfoResponse.model_validate(user)
    )


@router.put("/update")
async def update_user_info(
    user_data: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await users.update_user(db, user.username, user_data)
    return response.success_response(
        message="更新用户信息成功", data=UserInfoResponse.model_validate(user)
    )


@router.put("/update_password")
async def update_user_password(
    password_data: UserChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ok = await users.update_password(
        db, user, password_data.old_password, password_data.new_password
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改密码失败"
        )
    return response.success_response(message="修改密码成功")
