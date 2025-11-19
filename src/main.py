from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from src.controller.routing.router import router
from src.common.di_container import di
from src.integration.db_connection_provider import PGConnectionProvider
from src.service.generic.cors import add_cors_middleware

@asynccontextmanager
async def lifespan(_app: FastAPI):
    di.register_pg(PGConnectionProvider)
    yield
    await di.pg_connection_provider.close_connection_pool()
    di.unregister_resources()

app = FastAPI(title="Informational Security lab 1", lifespan=lifespan)
add_cors_middleware(app)
app.include_router(router)


@app.get("/", include_in_schema=False)
def redirect_to_redoc() -> RedirectResponse:
    """Redirect to ReDoc"""
    return RedirectResponse(url="/redoc", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/healthcheck")
def healthcheck() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "ok"}
