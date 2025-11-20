from datetime import UTC, datetime, timedelta
from typing import Optional

import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.integration.repository.entity import User
from src.integration.repository.user_repository import UserRepository


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, "JWT_EXPIRATION_MINUTES", 60 * 24)  # default: 1 day
SECRET_KEY = settings.JWT_SECRET

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.now(UTC)
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = now + expires_delta
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_user_id_from_token(token) -> Optional[str]:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload.get("sub")


async def create_user(session: AsyncSession, login: str, password: str) -> User:
    repo = UserRepository(session)
    user = await repo.create_user(login, get_password_hash(password))
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    return await UserRepository(session).get_user_by_id(user_id)


async def get_user_by_login(session: AsyncSession, login: str) -> Optional[User]:
    return await UserRepository(session).get_user_by_login(login)
