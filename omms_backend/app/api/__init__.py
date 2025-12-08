from fastapi import APIRouter, Depends

from app.api.records import router as records_router
from app.api.auth import router as auth_router
from app.core.auth import require_auth


def get_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(auth_router)
    router.include_router(records_router, dependencies=[Depends(require_auth)])
    return router
