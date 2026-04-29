from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

from src.utils.loguru_config import AppLogger
from src.core.config import settings
from src.routers import router as auth_router
from src.routers.api.v1.task_router.task import router as task_router
from src.routers.api.v1.project_router.project import router as project_router


logger = AppLogger().get_logger()
app = FastAPI()

app.include_router(router=auth_router)
app.include_router(router=task_router)
app.include_router(router=project_router)


app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

if __name__ == "__main__":
    logger.info("APP started!!!")
    uvicorn.run("main:app", host=settings.SERVER_IP, port=int(settings.SERVER_PORT), reload=True)
