from src.utils.loguru_config import AppLogger
from test.utils import assert_json_equal

logger = AppLogger().get_logger()


def test_create_project(
    project_json,
    projects_api_url,
    client,
    project_user,
    excluded_list,
):
    test_project = project_json.copy()
    test_project["creator_id"] = project_user["id"]

    resp = client.post(projects_api_url % "", json=test_project)
    status_code = resp.status_code
    project = resp.json()
    logger.debug(f"STATUS: {status_code}, BODY: {project}")

    assert status_code == 200
    assert_json_equal(test_project, project, exclude=excluded_list)
    assert project["id"]


def test_get_project(projects_api_url, client, project):
    project_id = project["id"]

    resp = client.get(projects_api_url % project_id)
    assert resp.status_code == 200
    assert resp.json()["id"] == project_id


def test_update_project(projects_api_url, client, project):
    project_id = project["id"]
    update_json = {
        "name": "Updated Project",
        "description": "Updated desc",
        "project_type": "software",
        "creator_id": 1,
    }
    resp = client.put(projects_api_url % project_id, json=update_json)
    logger.info(resp.json())
    assert resp.status_code == 200
    assert resp.json()["name"] == update_json["name"]


def test_delete_project(projects_api_url, client, project):
    project_id = project["id"]
    resp = client.delete(projects_api_url % project_id)
    assert resp.status_code == 200
