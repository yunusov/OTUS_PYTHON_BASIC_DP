import requests
from src.utils.loguru_config import AppLogger
from test.utils import assert_json_equal
from src.schemas.project import ProjectType

logger = AppLogger().get_logger()


def test_create_task(
    task_json,
    server_url,
    client,
    created_project,
    created_user,
):
    # 1. Убедимся, что user уже есть (created_user из фикстуры)
    # 2. Создаём task
    resp: requests.Response = client.post(
        f"{server_url}/tasks/",
        json=task_json,
    )
    print(f"STATUS: {resp.status_code}, BODY: {resp.json()}")  # отладка

    assert resp.status_code in (200, 201)
    task = resp.json()

    # 3. Проверяем данные
    assert task["name"] == "Test Task"
    assert task["description"] == "Test task description"
    assert task["project_id"] == created_project
    assert task["status"] == "todo"
    assert task["priority"] == "medium"
    assert task["creator_id"] == created_user
    assert "id" in task  # БД добавила!
    assert "created_at" in task


def test_get_project(server_url, client, created_project):
    project_id = created_project

    resp = client.get(f"{server_url}/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == project_id


def test_update_project(server_url, client, created_project):
    project_id = created_project

    update_json = {
        "id": project_id,
        "name": "Updated Project",
        "description": "Updated desc",
        "project_type": "software",
        "creator_id": 1
    }

    resp = client.put(f"{server_url}/projects/{project_id}", json=update_json)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Project"


def test_delete_project(server_url, client, created_project):
    project_id = created_project

    resp = client.delete(f"{server_url}/projects/{project_id}")
    assert resp.status_code == 200

    check_resp = client.get(f"{server_url}/projects/{project_id}")
    assert check_resp.status_code == 404