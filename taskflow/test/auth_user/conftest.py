# test/auth_user/conftest.py

import pytest, requests

from src.core.auth.user_manager import UserManager
from src.core.config import settings
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()

@pytest.fixture(scope="module")
def token(client, login_url, user_json):
    # login user
    resp: requests.Response = client.post(
        login_url,
        data={
            "username": user_json["email"],  # username = email
            "password": user_json["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return resp.json()["access_token"]


@pytest.fixture(scope="module")
def login_url(server_url):
    return "".join([f"{server_url}", settings.api.auth_url, "/login"])


@pytest.fixture(scope="module")
def verify_url(server_url):
    return "".join([f"{server_url}", settings.api.auth_url, "/verify"])


@pytest.fixture(scope="module")
def request_verify_token_url(server_url):
    return "".join([f"{server_url}", settings.api.auth_url, "/request-verify-token"])


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
def verify_token(client, request_verify_token_url, user_json):
    original = UserManager.on_after_request_verify
    captured = {}

    # monkeypath on_after_request_verify
    async def capture_token(self, user, token, request=None):
        captured["token"] = token
        return await original(self, user, token, request)

    UserManager.on_after_request_verify = capture_token

    # request verify token
    requests.Response = client.post(
        request_verify_token_url,
        json={
            "email": user_json["email"],
        },
    )
    yield captured["token"]

    UserManager.on_after_request_verify = original

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
        "email": "admin@example.com",
        "password": "pwd",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": "admin",
        "fullname": "admin",
    }
