from fastapi import APIRouter

from src.router.object import router as object_router
from src.router.user import router as user_router

api_router = APIRouter()

api_router.include_router(user_router, tags=["User"])
api_router.include_router(object_router, tags=["Object"])
