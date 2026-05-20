from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

from src.utils.loguru_config import AppLogger
from src.core import get_db_helper, settings
from src.routers import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await get_db_helper().dispose()


logger = AppLogger().get_logger()

main_app = FastAPI(
    lifespan=lifespan,
)
app.include_router(router=task_router)
app.include_router(router=project_router)



main_app.include_router(router=api_router, prefix=settings.api.PREFIX)
main_app.add_middleware(SessionMiddleware, secret_key=settings.run.SECRET_KEY)

if __name__ == "__main__":
    logger.info("APP started!!!")
    uvicorn.run(
        "main:main_app",
        host=settings.run.SERVER_IP,
        port=int(settings.run.SERVER_PORT),
        reload=True,
    )
