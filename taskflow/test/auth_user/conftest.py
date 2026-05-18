# test/auth_user/conftest.py

import pytest, requests

from src.core.auth.user_manager import UserManager
from src.core.config import settings
from src.utils.loguru_config import AppLogger


logger = AppLogger().get_logger()

@pytest.fixture(scope="module")
def forgot_password_url(server_url):
    return "".join([f"{server_url}", settings.api.auth_url, "/forgot-password"])


@pytest.fixture(scope="module")
def reset_password_url(server_url):
    return "".join([f"{server_url}", settings.api.auth_url, "/reset-password"])


@pytest.fixture(scope="module")
def users_url(server_url):
    return "".join([f"{server_url}", settings.api.users_url, "/%s"])


@pytest.fixture(scope="module")
def reset_token(client, forgot_password_url, user_json):
    original = UserManager.on_after_forgot_password
    captured = {}

    # monkeypath on_after_request_verify
    async def capture_token(self, user, token, request=None):
        captured["token"] = token
        return await original(self, user, token, request)

    UserManager.on_after_forgot_password = capture_token

    # request reset token
    requests.Response = client.post(
        forgot_password_url,
        json={
            "email": user_json["email"],
        },
    )
    yield captured["token"]

    UserManager.on_after_forgot_password = original


@pytest.fixture(scope="module")
def modify_json():
    # Данные для модификации
    return {
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": "admin",
        "fullname": "admin",
    }
