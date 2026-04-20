from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError,SQLAlchemyError

from utils.exception import http_exception_handler,integrity_exception_handler,sqlalchemy_exception_handler,general_exception_handler

def register_exception_handlers(app):
    """
    注册全局异常处理:子类在前 父类在后 具体在前 抽象在后
    """
    app.add_exception_handler(HTTPException,http_exception_handler) # 业务层面报错
    app.add_exception_handler(IntegrityError,integrity_exception_handler) # 处理数据库完整性的约束错误
    app.add_exception_handler(SQLAlchemyError,sqlalchemy_exception_handler) # 处理SQLAlchemy 数据库错误
    app.add_exception_handler(Exception,general_exception_handler) # 兜底



