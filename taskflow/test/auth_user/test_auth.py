import requests

from src.utils.loguru_config import AppLogger
from test.utils import assert_json_equal

logger = AppLogger().get_logger()


def test_register_user(user_json, register_url, client, excluded_list):
    # register user
    resp: requests.Response = client.post(register_url, json=user_json)
    assert resp.status_code == 201
    assert_json_equal(user_json, resp.json(), exclude=excluded_list)


def test_register_user_same_username(user_json, register_url, client):
    # try to register user
    resp: requests.Response = client.post(register_url, json=user_json)
    resp_json = resp.json()
    assert resp.status_code == 400
    assert "REGISTER_USER_ALREADY_EXISTS" in resp_json["detail"]


def test_reset_pwd(
    client,
    reset_password_url,
    reset_token,
    user_json,
):
    # reset token
    resp: requests.Response = client.post(
        reset_password_url,
        json={"token": reset_token, "password": "321"},
    )
    assert resp.status_code == 200
    user_json["password"] = "321"


def test_verify_user(client, verify_url, verify_token):
    # verify token
    resp: requests.Response = client.post(
        verify_url,
        json={"token": verify_token},
    )
    assert resp.status_code == 200
    assert resp.json()["is_verified"]


def test_wrong_authentication(login_url, client):
    # login user
    resp: requests.Response = client.post(
        login_url,
        data={
            "username": "wrong@user.com",
            "password": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 400
    resp_json = resp.json()
    assert "LOGIN_BAD_CREDENTIALS" in resp_json["detail"]


def test_authentication(user_json, login_url, users_url, client, excluded_list):
    # login user
    resp: requests.Response = client.post(
        login_url,
        data={
            "username": user_json["email"],  # username = email
            "password": user_json["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    # /me
    resp = client.get(
        users_url % "me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert_json_equal(user_json, resp.json(), exclude=excluded_list)

