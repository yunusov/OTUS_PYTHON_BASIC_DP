from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from src.core import settings
from src.routers.api.v1.auth import router as auth_router
from src.routers.api.v1.project import router as project_router
from src.routers.api.v1.task import router as task_router
from src.routers.api.v1.users import router as users_router
from src.routers.api.v1.comment import router as comment_router
from src.routers.web.login import router as main_router
from src.routers.web.user_verify import router as verify_router
from src.routers.web.projects import router as projects_router
from src.routers.web.tasks import router as web_task_router
from src.routers.web.comment import router as web_comment_router

http_bearer = HTTPBearer(auto_error=False)

api_router = APIRouter(
    prefix=settings.api.v1.prefix,
    dependencies=[
        Depends(http_bearer),
    ],
)
web_router = APIRouter(
    prefix="",
    dependencies=[
        Depends(http_bearer),
    ],
)
api_router.include_router(router=auth_router)
api_router.include_router(router=users_router)
api_router.include_router(router=project_router)
api_router.include_router(router=task_router)
api_router.include_router(router=comment_router)

web_router.include_router(router=main_router)
web_router.include_router(router=verify_router)
web_router.include_router(router=projects_router)
web_router.include_router(router=web_task_router)
web_router.include_router(router=web_comment_router)
