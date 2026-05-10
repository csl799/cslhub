import traceback

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status

DEBUG_MODE = True


async def http_exception_handler(_request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    err = str(exc.orig)
    if "username_UNIQUE" in err or "Duplicate entry" in err:
        detail = "用户名已存在"
    elif "FOREIGN KEY" in err:
        detail = "关联数据不存在"
    else:
        detail = "数据约束冲突，请检查输入"

    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": "IntegrityError",
            "error_detail": err,
            "path": str(request.url),
        }
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"code": 400, "message": detail, "data": error_data},
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    orig = getattr(exc, "orig", None)
    brief = str(orig) if orig is not None else str(exc)
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": type(exc).__name__,
            "error_detail": str(exc),
            "error_orig": brief,
            "traceback": traceback.format_exc(),
            "path": str(request.url),
        }
    message = "数据库操作失败，请稍后重试"
    if DEBUG_MODE and brief:
        message = f"数据库操作失败：{brief}"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": 500, "message": message, "data": error_data},
    )


async def general_exception_handler(request: Request, exc: Exception):
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": type(exc).__name__,
            "error_detail": str(exc),
            "traceback": traceback.format_exc(),
            "path": str(request.url),
        }
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": 500, "message": "服务器内部错误", "data": error_data},
    )
