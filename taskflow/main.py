from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

from create_app import create as fastapi_create_app
from src.core import settings
from src.core import get_db_helper, settings
from src.routers import api_router, web_router
from src.utils.loguru_config import AppLogger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await get_db_helper().dispose()


logger = AppLogger().get_logger()

main_app = fastapi_create_app()

main_app.mount("/images", StaticFiles(directory="src/images"), name="images")
main_app.include_router(router=api_router, prefix=settings.api.PREFIX)
main_app.include_router(router=web_router)
main_app.add_middleware(SessionMiddleware, secret_key=settings.run.SECRET_KEY)


if __name__ == "__main__":
    logger.info("APP started!!!")
    uvicorn.run(
        "main:main_app",
        host=settings.run.SERVER_IP,
        port=int(settings.run.SERVER_PORT),
        reload=True,
    )
