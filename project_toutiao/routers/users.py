from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import crud

import utils.auth
from config.db_config import get_db
from schemas.users import UserRequest, UserAuthResponse, UserInfoBase, UserInfoResponse,UserUpdateRequest
from crud import users
from utils import response,auth
from models.users import User
from utils.auth import get_current_user

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



@router.post("/login")
async def login(user_data:UserRequest,db:AsyncSession = Depends(get_db)):
    # 登录逻辑 验证用户是否存在 验证密码 生产token 响应结果
    user = await users.authenticate_user(db,user_data.username,user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="用户名或密码错误")

    token = await users.create_token(db,user.id)
    response_data = UserAuthResponse(token=token,userInfo=UserInfoResponse.model_validate(user))

    return response.success_response(message="登录成功",data = response_data)



# 查token查用户 封装crud 功能整合成一个工具函数 路由导入使用 依赖注入
@router.get("/info")
async def get_user_info(user:User = Depends(auth.get_current_user)):
    return response.success_response(message="获取用户信息成功",data=UserInfoResponse.model_validate(user))



# 修改用户信息 验证token 更新用户输入数据 put提交 请求体参数 定义pydantic模型类 响应结果
# 参数包含用户输入的 验证token的 db调用更新的方法
@router.put("/update")
async def update_user_info(
        user_data:UserUpdateRequest,
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    user = await users.update_user(db,user.username,user_data)

    return response.success_response(message = "更新用户信息成功",data = UserInfoResponse.model_validate(user))






