from fastapi import Request

from src.core import settings
from src.schemas.user import UserRead
from src.utils.loguru_config import AppLogger
from src.utils.request_utils import async_request


logger = AppLogger().get_logger()

class UserService:

    @classmethod
    def get_me(cls, request: Request, access_token: str) -> UserRead | None:
        response = async_request(
            "GET",
            "/" + settings.api.users_url + "/me",
            request=request,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        logger.info(f"get_user_by_token {response=}")
        if response.setdefault("detail", None) == "Unauthorized":
            request.session.clear()
            return None
        user = UserRead.model_validate(response)
        return user

    @classmethod
    def patch_me(cls, request: Request, access_token: str, params: dict) -> dict:
        response = async_request(
            "PATCH",
            "/" + settings.api.users_url + "/me",
            params=params,
            request=request,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        logger.info(f"get_user_by_token {response=}")
        detail = response.setdefault("detail", [])
        if detail == "Unauthorized":
            request.session.clear()
            return {"detail": "Session logout"}
        elif detail and (error:=detail[0].setdefault("msg", [])):
            return {"error": error}
        return {}
