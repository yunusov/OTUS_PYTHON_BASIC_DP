from src.utils.loguru_config import AppLogger
from test.utils import assert_json_equal

logger = AppLogger().get_logger()


def test_create_task(
    task_json,
    tasks_api_url,
    client,
    excluded_list,
    token,
):
    resp = client.post(
        tasks_api_url % "",
        json=task_json,
        headers={"Authorization": f"Bearer {token}"},
    )
    logger.debug(f"STATUS: {resp.status_code}, BODY: {resp.json()}")

    assert resp.status_code == 200
    task = resp.json()

    assert_json_equal(task, task_json, exclude=excluded_list)
    assert task["id"]
    assert task["created_at"]


def test_get_task(
    client,
    tasks_api_url,
    task,
    excluded_list,
    token,
):
    resp = client.get(tasks_api_url % task["id"],
        headers={"Authorization": f"Bearer {token}"},)
    assert resp.status_code == 200

    json = resp.json()
    assert_json_equal(task, json, exclude=excluded_list)


def test_modify_task(
    client,
    tasks_api_url,
    task,
    project,
    project_user,
    excluded_list,
    token,
):
    # вместо TODO, "IN_PROGRESS", @MEDIUM", "HIGH"
    # если TaskInDB требует created_at

    update_json = {
        "name": "Updated Task",
        "description": "Updated desc",
        "project_id": project["id"],
        "status": "in_progress",
        "priority": "high",
        "due_date": "2026-12-31T23:59:59Z",
        "creator_id": project_user["id"],
        "assignee_id": project_user["id"],
        "time_estimate": 120,
        "time_spent": 30,
        "created_at": "2026-04-30T12:00:00Z",
    }

    resp = client.put(
        tasks_api_url % task["id"],
        json=update_json,
        headers={"Authorization": f"Bearer {token}"},
    )
    logger.debug("MODIFY RESP:", resp.status_code, resp.json())

    assert resp.status_code == 200
    task = resp.json()
    assert_json_equal(task, update_json, exclude=excluded_list)


def test_delete_task(
    client,
    tasks_api_url,
    task,
    token,
):
    resp = client.delete(
        tasks_api_url % task["id"],
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
