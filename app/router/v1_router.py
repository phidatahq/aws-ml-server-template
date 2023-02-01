from fastapi import APIRouter

from app.constants import API_V1_SUFFIX
from app.router.status_routes import status_router

v1_router = APIRouter(prefix=API_V1_SUFFIX)
v1_router.include_router(status_router)
