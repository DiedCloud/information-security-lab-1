from contextlib import asynccontextmanager

from apscheduler.schedulers.base import STATE_RUNNING  # type: ignore
from fastapi import Depends, FastAPI, status
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from src.background_tasks.sheduled_cleaner import scheduler
from src.common.di_container import di
from src.controller.routing.auth import auth_router, get_current_user
from src.controller.routing.cleaner_router import cleaner_router
from src.controller.routing.crud_router import crud_router
from src.integration.db_connection_provider import PGConnectionProvider
from src.service.generic.auth_middleware import JWTAuthMiddleware
from src.service.generic.logger import logger


@asynccontextmanager
async def lifespan(_app: FastAPI):
    di.register_pg(PGConnectionProvider)
    yield
    await di.pg_connection_provider.close_connection_pool()
    di.unregister_resources()

    try:
        if scheduler.state == STATE_RUNNING:
            scheduler.shutdown(wait=False)
    except Exception as e:
        logger.exception("Ошибка при shutdown scheduler", exc_info=e)


app = FastAPI(title="Information Security lab 1", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(JWTAuthMiddleware)

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
