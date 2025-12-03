from fastapi import APIRouter

from app.api.records import router as records_router


def get_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(records_router)
    return router
