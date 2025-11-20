from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.di_container import di
from src.controller.schemas.schemas import Token, UserCreate, UserLogin
from src.integration.repository.entity import User
from src.integration.repository.user_repository import UserRepository
from src.service.auth_service import (
    create_access_token,
    verify_password,
    get_user_id_from_token,
    create_user,
    get_user_by_login,
)

AUTH_ROUTER_PREFIX = "/auth"

auth_router = APIRouter(prefix=AUTH_ROUTER_PREFIX, tags=["Авторизация"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    repo: UserRepository = Depends(UserRepository),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = int(get_user_id_from_token(token))
    except (JWTError, TypeError, ValueError):
        raise credentials_exception

    user = await repo.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user


@auth_router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, session: AsyncSession = Depends(di.get_pg_session)):
    existing = await get_user_by_login(session, payload.login)
    if existing:
        raise HTTPException(status_code=409, detail="User with this login already exists")

    user = await create_user(session, payload.login, payload.password)

    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token)


@auth_router.post("/login", response_model=Token)
async def login(payload: UserLogin, session: AsyncSession = Depends(di.get_pg_session)):
    user = await get_user_by_login(session, payload.login)
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)


