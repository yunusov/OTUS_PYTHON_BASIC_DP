# test/inventory/conftest.py

import random
import pytest

from src.core.config import settings
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


@pytest.fixture
def project(client, projects_api_url, project_json, token):
    """Создаёт проект и возвращает его ID"""
    json = project_json.copy()
    json["name"] = " ".join([json["name"], str(random.randint(1, 1000))])
    resp = client.post(
        projects_api_url % "",
        json=json,
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()


@pytest.fixture
def task(client, tasks_api_url, task_json, token):
    """Создаёт задачу и возвращает task_id"""
    resp = client.post(
        tasks_api_url % "",
        json=task_json,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    return resp.json()


@pytest.fixture
def comment(client, comments_api_url, comment_json, project_user, token):
    """Создаёт комментарий через POST запрос и возвращает его"""
    test_comment = comment_json.copy()
    test_comment["creator_id"] = project_user["id"]

    resp = client.post(
        comments_api_url % "",
        json=test_comment,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    return resp.json()


@pytest.fixture(scope="module")
def projects_api_url(server_url):
    return "".join([f"{server_url}", settings.api.projects_url, "/%s"])


@pytest.fixture(scope="module")
def comments_api_url(server_url):
    return "".join([f"{server_url}", settings.api.comments_url, "/%s"])


@pytest.fixture(scope="module")
def tasks_api_url(server_url):
    return "".join([f"{server_url}", settings.api.tasks_url, "/%s"])


@pytest.fixture
def project_json():
    return {
        "name": "New project",
        "description": "Test description",
        "project_type": "software",
        "creator_id": 1,
    }


@pytest.fixture
def task_json(project, project_user):
    """JSON для создания задачи (под TaskInDB/TaskOrm)"""
    return {
        "name": "Test Task",
        "description": "Test task description",
        "project_id": project["id"],
        "status": "todo",
        "priority": "medium",
        "due_date": "2026-05-01T12:00:00Z",
        "creator_id": project_user["id"],
        "assignee_id": project_user["id"],
        "time_estimate": 60,
        "time_spent": 0,
        "created_at": "2026-04-30T12:00:00Z",
    }


@pytest.fixture
def comment_json(task):
    """JSON для создания комментария (под CommentCreate)"""
    return {
        "content": "Test comment content",
        "task_id": task["id"],
    }
