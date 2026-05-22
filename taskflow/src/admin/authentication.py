from fastapi import Request
from fastapi_users.password import PasswordHelper
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from starlette.responses import Response

from src.core import get_db_helper
from src.models import UserOrm
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()
password_helper = PasswordHelper()


class AdminAuth(AuthenticationBackend):
    """Authentication backend for SQLAdmin using fastapi-users model."""

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        if not email or not password:
            return False

        helper = get_db_helper()
        with helper.session_factory() as session:
            result = session.execute(select(UserOrm).where(UserOrm.email == email))
            user = result.scalar_one_or_none()

            if user is None:
                return False
            is_valid, _ = password_helper.verify_and_update(password, user.hashed_password)  # type: ignore[misc]
            if not is_valid:
                return False
            if not user.is_superuser:
                return False
        request.session.update({"user_id": str(user.id)})
        return True

    async def logout(self, request: Request) -> Response | bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Response | bool:
        user_id = request.session.get("user_id")
        if not user_id:
            return False
        return True
