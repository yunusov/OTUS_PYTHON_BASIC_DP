from fastapi import APIRouter

from src.core.auth.fastapi_users import fastapi_users
from src.core.config import settings
from src.routers.api.dependencies.auth.backend import authentification_backend
from src.schemas import (
    UserRead,
    UserCreate,
)

router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)

# /login
# /logout
router.include_router(
    router=fastapi_users.get_auth_router(
        authentification_backend,
        requires_verification=True,
    ),
)
# /register
router.include_router(
    router=fastapi_users.get_register_router(
        UserRead,
        UserCreate,
    ),
)

# /request-verify-token
# /verify
router.include_router(
    router=fastapi_users.get_verify_router(
        UserRead,
    ),
)

# /forgot-password
# /reset-password
router.include_router(
    router=fastapi_users.get_reset_password_router()
)