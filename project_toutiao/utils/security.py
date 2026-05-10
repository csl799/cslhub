from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash_password(password: str) -> str:
    raw = password.encode("utf-8")[:72]
    safe = raw.decode("utf-8", errors="ignore")
    return pwd_context.hash(safe)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
