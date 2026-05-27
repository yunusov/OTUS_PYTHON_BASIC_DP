from starlette.middleware.sessions import SessionMiddleware
import uvicorn


from create_app import create as fastapi_create_app
from src.core import settings
from src.routers import router as api_router
from src.utils.loguru_config import AppLogger
from src.routers.web.index import router as index_router
from fastapi.staticfiles import StaticFiles
from src.routers.web.login import router as login_pages_router

logger = AppLogger().get_logger()

main_app = fastapi_create_app()

main_app.mount("/images", StaticFiles(directory="src/images"), name="images")
main_app.include_router(router=api_router, prefix=settings.api.PREFIX)
main_app.include_router(router=index_router)
main_app.include_router(login_pages_router)
main_app.add_middleware(SessionMiddleware, secret_key=settings.run.SECRET_KEY)


if __name__ == "__main__":
    logger.info("APP started!!!")
    uvicorn.run(
        "main:main_app",
        host=settings.run.SERVER_IP,
        port=int(settings.run.SERVER_PORT),
        reload=True,
    )
