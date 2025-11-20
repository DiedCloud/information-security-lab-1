from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Depends
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from src.controller.routing.auth import auth_router, get_current_user
from src.controller.routing.crud_router import crud_router
from src.controller.routing.cleaner_router import cleaner_router
from src.common.di_container import di
from src.integration.db_connection_provider import PGConnectionProvider
from src.service.generic.auth_middleware import JWTAuthMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    di.register_pg(PGConnectionProvider)
    yield
    await di.pg_connection_provider.close_connection_pool()
    di.unregister_resources()

app = FastAPI(title="Informational Security lab 1", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(JWTAuthMiddleware)  # noqa

app.include_router(auth_router)
app.include_router(crud_router, dependencies=[Depends(get_current_user)])
app.include_router(cleaner_router, dependencies=[Depends(get_current_user)])


@app.get("/", include_in_schema=False)
def redirect_to_redoc() -> RedirectResponse:
    """Redirect to ReDoc"""
    return RedirectResponse(url="/redoc", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/healthcheck")
def healthcheck() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "ok"}
