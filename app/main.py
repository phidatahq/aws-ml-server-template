from typing import Tuple

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app import constants
from app.settings import AppSettings
from app.router.v1_router import v1_router


def create_app() -> Tuple[FastAPI, AppSettings]:
    """Create a FastAPI App

    Returns:
        FastAPI:
        AppSettings:
    """

    app_settings = AppSettings()

    # Create FastAPI App
    app: FastAPI = FastAPI(
        title=constants.TITLE,
        version=constants.VERSION,
        docs_url="/docs" if app_settings.docs_enabled else None,
        redoc_url="/redoc" if app_settings.docs_enabled else None,
        openapi_url="/openapi.json" if app_settings.docs_enabled else None,
    )
    # Add v1 router
    app.include_router(v1_router)

    # Add Middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app, app_settings


app, app_settings = create_app()
