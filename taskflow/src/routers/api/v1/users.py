from fastapi import APIRouter

from src.core import settings
from src.core.auth.fastapi_users import fastapi_users
from src.schemas import (
    UserRead,
    UserUpdate,
)

router = APIRouter(
    prefix=settings.api.v1.users,
    tags=["Users"],
)

# /me
# /{id}
router.include_router(
    router=fastapi_users.get_users_router(
        UserRead,
        UserUpdate,
    )
)
