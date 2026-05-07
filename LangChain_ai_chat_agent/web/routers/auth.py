from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.deps import get_current_user, security
from db.models import User
from auth.schemas import LoginIn, RegisterIn, TokenOut, UserOut
from auth.service import login_user, register_user, revoke_session, validate_token
from db.session import get_session

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
async def register(body: RegisterIn, session: AsyncSession = Depends(get_session)) -> TokenOut:
    try:
        _user, token, exp = await register_user(session, body.username, body.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return TokenOut(access_token=token, expires_at=exp)


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, session: AsyncSession = Depends(get_session)) -> TokenOut:
    try:
        token, exp = await login_user(session, body.username, body.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    return TokenOut(access_token=token, expires_at=exp)


@router.post("/logout")
async def logout(
    creds=Depends(security),
    session: AsyncSession = Depends(get_session),
) -> dict:
    try:
        _uid, jti = await validate_token(session, creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="token 无效") from None
    await revoke_session(session, jti)
    return {"ok": True}


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)
