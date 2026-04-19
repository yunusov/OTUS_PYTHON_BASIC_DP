import requests


def test_create_user(user_json, server_url, client):
    resp: requests.Response = client.post(
        f"{server_url}/auth/register/", json=user_json
    )
    assert resp.status_code == 200
    resp_json = resp.json()
    created_at = resp_json.get("created_at")
    user_json["created_at"] = created_at
    assert resp_json == user_json


def test_modify_user(user_json, server_url, modify_json, client):
    created_at = user_json.get("created_at")
    modify_json["created_at"] = created_at

    resp: requests.Response = client.put(
        f"{server_url}/auth/register/", json=modify_json
    )
    resp_json = resp.json()
    resp_json["created_at"] = created_at
    assert resp_json == modify_json


def test_login_constraint(modify_json, server_url, client):
    modify_json["username"] = "x" * 33
    resp: requests.Response = client.put(
        f"{server_url}/auth/register/", json=modify_json
    )
    resp_json = resp.json()
    assert (
        "Логин должен быть от 3 до 32 символов в длину!"
        in resp_json["detail"][0]["msg"]
    )


def test_fullname_constraints(modify_json, server_url, client):
    modify_json["fullname"] = "x" * 101
    resp: requests.Response = client.put(
        f"{server_url}/auth/register/", json=modify_json
    )
    resp_json = resp.json()
    assert (
        "Полное имя пользователя должно быть менее 100 символов в длину!"
        in resp_json["detail"][0]["msg"]
    )


def test_email_constraints(modify_json, server_url, client):
    new_json = modify_json.copy()
    new_json["email"] = "x" * 51 + "@ex.ru"
    resp: requests.Response = client.put(f"{server_url}/auth/register/", json=new_json)
    resp_json = resp.json()
    assert (
        "Email должно быть менее 50 символов в длину!" in resp_json["detail"][0]["msg"]
    )

    new_json = modify_json.copy()
    new_json["email"] = "zzxczxc@"
    resp: requests.Response = client.put(f"{server_url}/auth/register/", json=new_json)
    resp_json = resp.json()
    assert "value is not a valid email address" in resp_json["detail"][0]["msg"]


def test_delete_user(server_url, client):
    resp: requests.Response = client.delete(
        f"{server_url}/auth/register/1",
    )
    assert resp.status_code == 200
    assert resp.content
