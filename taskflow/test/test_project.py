import requests
from src.utils.loguru_config import AppLogger
from test.utils import assert_json_equal
from src.schemas.project import ProjectType

logger = AppLogger().get_logger()


def test_create_project(
    project_json,
    server_url,
    client,
    created_user,
):
    test_project = project_json.copy()
    test_project["creator_id"] = created_user

    resp = client.post(f"{server_url}/projects/", json=test_project)
    print(f"STATUS: {resp.status_code}, BODY: {resp.json()}")

    assert resp.status_code in (200, 201)
    project = resp.json()

    # Проверяем ТОЛЬКО то, что мы отправили
    assert project["name"] == test_project["name"]  # Динамически!
    assert project["description"] == test_project["description"]
    assert project["creator_id"] == created_user
    assert project["project_type"] == "software"
    assert "id" in project

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