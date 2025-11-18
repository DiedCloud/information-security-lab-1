from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

app = FastAPI(title="Informational Security lab 1")


@app.get("/", include_in_schema=False)
def redirect_to_redoc() -> RedirectResponse:
    """Redirect to ReDoc"""
    return RedirectResponse(url="/redoc", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/healthcheck")
def healthcheck() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "ok"}
