from fastapi import FastAPI
from core.session import get_settings
from src.router.api_router import api_router


def get_application() -> FastAPI:
    application = FastAPI(root_path=get_settings().root_path)

    application.include_router(api_router)

    return application


app = get_application()