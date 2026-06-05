from fastapi import Request

from src.core import settings
from src.schemas.user import UserRead
from src.utils.loguru_config import AppLogger
from src.utils.request_utils import async_request

logger = AppLogger().get_logger()


class UserService:

    @classmethod
    def get_me(cls, request: Request) -> UserRead | None:
        access_token = request.session.setdefault("access_token", None)
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
    def get_user_by_id(
        cls,
        request: Request,
        user_id: str,
    ) -> UserRead | None:
        access_token = request.session.setdefault("access_token", None)
        response = async_request(
            "GET",
            "/" + settings.api.users_url + "/" + user_id,
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
    def patch_me(cls, request: Request, params: dict) -> dict:
        access_token = request.session.setdefault("access_token", None)
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
        elif detail and (error := detail[0].setdefault("msg", [])):
            return {"error": error}
        return {}
