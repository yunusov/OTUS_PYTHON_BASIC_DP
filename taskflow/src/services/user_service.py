from fastapi import Request

from src.core import settings
from src.schemas.user import UserRead
from src.utils.loguru_config import AppLogger
from src.utils.request_utils import async_request


logger = AppLogger().get_logger()

class UserService:

    @classmethod
    def get_me(cls, request: Request, access_token: str):
        logger.info(f"get_user_by_token {settings.api.users_url=}")
        response = async_request(
            "GET",
            "/" + settings.api.users_url + "/me",
            request=request,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        logger.info(f"get_user_by_token {response=}")
        user = UserRead.model_validate(response)
        return user
