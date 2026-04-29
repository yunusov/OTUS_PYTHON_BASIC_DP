# test/test_project.py

# import pytest
from src.utils.loguru_config import AppLogger
# from src.schemas.project import ProjectType

logger = AppLogger().get_logger()






def test_create_project(project_json, server_url, client):
    logger.info(project_json)
    resp = client.post(
        f"{server_url}/projects/",
        json=project_json,
    )
    logger.info(resp.json())  # для дебага
    assert resp.status_code in (200, 201)  # или 200, если хочешь
    resp_json = resp.json()
    for key in ("name", "description", "project_type", "creator_id"):
        if key in project_json:
            assert resp_json[key] == project_json[key]
    assert "id" in resp_json