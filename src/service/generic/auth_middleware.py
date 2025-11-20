from collections.abc import Callable

from fastapi import Request
from jwt import PyJWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.common.di_container import di
from src.controller.routing.auth import AUTH_ROUTER_PREFIX
from src.service.auth_service import get_user_by_id, get_user_id_from_token


class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, excluded_paths: list[str] | None = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            AUTH_ROUTER_PREFIX,
            "/",
            "/healthcheck",
            "/open",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next: Callable):
        # Простой white-list: пропускаем Auth и docs
        path = request.url.path
        if any(path.startswith(p) for p in self.excluded_paths):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                {"detail": "Not authenticated"}, status_code=401, headers={"WWW-Authenticate": "Bearer"}
            )

        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Invalid auth header"}, status_code=401, headers={"WWW-Authenticate": "Bearer"}
            )

        token = auth_header.split(" ", 1)[1].strip()
        err_401 = JSONResponse(
            {"detail": "Could not validate credentials"}, status_code=401, headers={"WWW-Authenticate": "Bearer"}
        )
        try:
            user_str = get_user_id_from_token(token)
            if not user_str:
                return err_401
            user_id = int(user_str)
        except (PyJWTError, TypeError, ValueError):
            return err_401

        # Загрузим пользователя из БД
        async with di.pg_connection_provider.get_session() as session:
            user = await get_user_by_id(session, user_id)
            if not user:
                return JSONResponse(
                    {"detail": "User not found"}, status_code=401, headers={"WWW-Authenticate": "Bearer"}
                )

            # Положим пользователя в request.state чтобы handler-ы могли его достать
            request.state.user = user

        # Продолжим цепочку
        return await call_next(request)
