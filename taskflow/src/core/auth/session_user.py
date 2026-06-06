from fastapi import Request
from fastapi.exceptions import HTTPException

from src.schemas.user import UserRead
from src.services.user_service import UserService
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


def get_current_user_from_session(
    request: Request,
) -> UserRead:
    access_token = request.session.get("access_token")
    logger.info(f"get_current_user_from_session {access_token=}")
    if not access_token:
        raise HTTPException(
            status_code=303, headers={"Location": str(request.url_for("login"))}
        )
    try:
        user = UserService.get_me(request)
        logger.info(f"get_current_user_from_session {user=}")
        if not user:
            request.session.pop("access_token", None)
            raise HTTPException(
                status_code=303, headers={"Location": str(request.url_for("login"))}
            )
        return user
    except Exception as e:
        logger.error(f"get_current_user_from_session failed: {e}")
        request.session.pop("access_token", None)
        raise HTTPException(
            status_code=303, headers={"Location": str(request.url_for("login"))}
        )
