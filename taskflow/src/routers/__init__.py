from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from src.core import settings
from src.routers.api.v1.auth import router as auth_router
from src.routers.api.v1.project import router as project_router
from src.routers.api.v1.task import router as task_router
from src.routers.api.v1.users import router as users_router

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix=settings.api.v1.prefix, dependencies=[Depends(http_bearer)])
router.include_router(router=auth_router)
router.include_router(router=users_router)
router.include_router(router=project_router)
router.include_router(router=task_router)
