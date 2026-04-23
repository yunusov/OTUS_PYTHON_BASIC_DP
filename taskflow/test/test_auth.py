import requests
from src.utils.loguru_config import AppLogger
from src.services.auth_service import AuthService
from test.utils import assert_json_equal

logger = AppLogger().get_logger()


def test_register_user(user_json, server_url, client):
    resp: requests.Response = client.post(
        f"{server_url}/auth/register/", json=user_json
    )
    assert resp.status_code == 200
    resp_json = resp.json()
    assert_json_equal(
        user_json, resp_json, exclude=["created_at", "id", "hashed_password"]
    )


def test_register_user_same_username(user_json, server_url, client):
    requests.Response = client.post(f"{server_url}/auth/register/", json=user_json)
    try:
        requests.Response = client.post(f"{server_url}/auth/register/", json=user_json)
        assert 1 == 2
    except ValueError as e:
        assert (
            "Пользователь с таким емейлом или именем уже зарегистрирован!" in e.args[0]
        )


def test_authentication(user_json, server_url, client):
    resp: requests.Response = client.post(
        f"{server_url}/auth/register/", json=user_json
    )
    assert resp.status_code == 200
    resp: requests.Response = client.post(f"{server_url}/auth/", json=user_json)
    assert resp.status_code == 200
    resp_json = resp.json()
    assert_json_equal(
        user_json, resp_json, exclude=["created_at", "id", "hashed_password"]
    )
    hashed_password = user_json["hashed_password"]
    user_json["hashed_password"] = "123"
    resp: requests.Response = client.post(f"{server_url}/auth/", json=user_json)
    assert resp.status_code == 200
    resp_json = resp.json()
    assert resp_json is None

    user_json["hashed_password"] = hashed_password
    user_json["username"] = "123123"
    resp: requests.Response = client.post(f"{server_url}/auth/", json=user_json)
    assert resp.status_code == 200
    resp_json = resp.json()
    assert resp_json is None
