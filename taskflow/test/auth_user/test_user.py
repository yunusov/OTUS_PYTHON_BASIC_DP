import random

import requests
from sqlalchemy import select

from src.models.user import UserOrm
from src.utils.loguru_config import AppLogger
from test.utils import assert_json_equal

logger = AppLogger().get_logger()


def test_modify_user(
    users_url,
    modify_json,
    client,
    excluded_list,
    token,
):
    resp: requests.Response = client.patch(
        users_url % "me",
        json=modify_json,
        headers={"Authorization": f"Bearer {token}"},
    )
    resp_json = resp.json()
    assert resp.status_code == 200
    # assert_json_equal(modify_json, resp_json, exclude=excluded_list)


def test_login_constraint(modify_json, users_url, client, token):
    new_json = modify_json.copy()
    new_json["username"] = "x" * 33
    resp: requests.Response = client.patch(
        users_url % "me",
        json=new_json,
        headers={"Authorization": f"Bearer {token}"},
    )
    resp_json = resp.json()
    assert (
        "Логин должен быть от 3 до 32 символов в длину!"
        in resp_json["detail"][0]["msg"]
    )


def test_fullname_constraints(modify_json, users_url, client, token):
    new_json = modify_json.copy()
    new_json["fullname"] = "x" * 101
    resp: requests.Response = client.patch(
        users_url % "me",
        json=new_json,
        headers={"Authorization": f"Bearer {token}"},
    )
    resp_json = resp.json()
    assert (
        "Полное имя пользователя должно быть менее 100 символов в длину!"
        in resp_json["detail"][0]["msg"]
    )


def test_email_constraints(modify_json, users_url, client, token):
    new_json = modify_json.copy()
    new_json["email"] = "x" * 51 + "@ex.ru"
    resp: requests.Response = client.patch(
        users_url % "me",
        json=new_json,
        headers={"Authorization": f"Bearer {token}"},
    )
    resp_json = resp.json()
    assert (
        "Email должно быть менее 50 символов в длину!" in resp_json["detail"][0]["msg"]
    )

    new_json = modify_json.copy()
    new_json["email"] = "zzxczxc@"
    resp: requests.Response = client.patch(
        users_url % "me",
        json=new_json,
        headers={"Authorization": f"Bearer {token}"},
    )
    resp_json = resp.json()
    assert "value is not a valid email address" in resp_json["detail"][0]["msg"]


def test_delete_user(
    db_session,
    register_url,
    users_url,
    client,
    user_json,
    project_user,
    token,
):
    # make user great again
    user = db_session.execute(
        select(UserOrm).filter(UserOrm.email == project_user["email"]),
    ).scalar_one()
    user.is_superuser = True
    db_session.commit()
    db_session.refresh(user)

    # register user
    json = user_json.copy()
    json["username"] = "".join([json["username"], str(random.randint(1, 1000))])
    json["email"] = json["email"].replace("user", "u" + str(random.randint(1, 1000)))
    resp: requests.Response = client.post(register_url, json=json)
    assert resp.status_code == 201

    user_id = resp.json()["id"]
    # delete user
    resp: requests.Response = client.delete(
        users_url % user_id,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204
