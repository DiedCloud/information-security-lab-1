from typing import TYPE_CHECKING

from fastapi.middleware.cors import CORSMiddleware

if TYPE_CHECKING:
    from fastapi import FastAPI


def add_cors_middleware(app: "FastAPI"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
