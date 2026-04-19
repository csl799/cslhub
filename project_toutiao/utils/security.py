from passlib.context import CryptContext



# 创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")


# 密码加密
def get_hash_password(password:str):
    safe_password_bytes = password.encode("utf-8")[:72]
    safe_password = safe_password_bytes.decode("utf-8",errors="ignore")

    return pwd_context.hash(safe_password)