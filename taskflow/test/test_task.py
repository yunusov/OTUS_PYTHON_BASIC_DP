import requests
from src.schemas.task import TaskInDB, Task
from test.utils import assert_json_equal
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


def test_create_task(
    task_json,
    server_url,
    client,
    created_project,
    created_user,
):
    resp = client.post(f"{server_url}/tasks/", json=task_json)
    print(f"STATUS: {resp.status_code}, BODY: {resp.json()}")

    assert resp.status_code in (200, 201)
    task = resp.json()

    assert task["name"] == "Test Task"
    assert task["description"] == "Test task description"
    assert task["project_id"] == created_project
    assert task["creator_id"] == created_user
    assert task["status"] == "todo"
    assert task["priority"] == "medium"
    assert "id" in task
    assert "created_at" in task


def test_get_task(
    client: requests.Session,
    server_url: str,
    created_task: int,
):
    resp = client.get(f"{server_url}/tasks/{created_task}")
    assert resp.status_code == 200

    task = resp.json()
    assert task["id"] == created_task
    assert task["project_id"] == 1  # или use created_project
    assert task["name"] == "Test Task"


def test_modify_task(
    client,
    server_url,
    created_task,
    created_project,
    created_user,
):
    update_json = {
        "id": created_task,
        "name": "Updated Task",
        "description": "Updated desc",
        "project_id": created_project,
        "status": "in_progress",          # вместо "TODO", "IN_PROGRESS"
        "priority": "high",               # вместо "MEDIUM", "HIGH"
        "due_date": "2026-12-31T23:59:59Z",
        "creator_id": created_user,
        "assignee_id": created_user,
        "time_estimate": 120,
        "time_spent": 30,
        "created_at": "2026-04-30T12:00:00Z",  # если TaskInDB требует created_at
    }

    resp = client.put(
        f"{server_url}/tasks/{created_task}",
        json=update_json,
    )
    print("MODIFY RESP:", resp.status_code, resp.json())

    assert resp.status_code == 200
    task = resp.json()
    assert task["id"] == created_task
    assert task["name"] == "Updated Task"
    assert task["status"] == "in_progress"
    assert task["priority"] == "high"

def test_delete_task(
    client: requests.Session,
    server_url: str,
    created_task: int,
):
    resp = client.delete(f"{server_url}/tasks/{created_task}")
    assert resp.status_code == 200

    check_resp = client.get(f"{server_url}/tasks/{created_task}")
    assert check_resp.status_code == 404