import pytest
from taskflow.src.schemas.project import ProjectType


class TestProjectCRUD:
    """CRUD тесты для проектов"""

    @pytest.mark.parametrize("name", ["ab", "a" * 101])
    def test_create_project_invalid_name(self, client, name):
        data = {"name": name, "creator_id": 1}
        resp = client.post("/projects/", json=data)
        assert resp.status_code == 422
        assert "length" in str(resp.json())

    def test_create_project_success(self, client):
        data = {
            "name": "Test Project",
            "creator_id": 1,
            "description": "Test desc",
            "project_type": ProjectType.BUSINESS.value
        }
        resp = client.post("/projects/", json=data)
        assert resp.status_code == 201
        json_data = resp.json()
        assert json_data["name"] == "Test Project"
        assert json_data["project_type"] == "business"
        assert "id" in json_data

    def test_get_projects_creator_empty(self, client):
        resp = client.get("/projects/creator/999")
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    def test_update_project_partial(self, client):
        # Создаём
        create_data = {"name": "Update Project", "creator_id": 1}
        create_resp = client.post("/projects/", json=create_data)
        project_id = create_resp.json()["id"]

        # Обновляем
        update_data = {
            "name": "Updated Project",
            "project_type": "service_desk"
        }
        resp = client.put(f"/projects/{project_id}/", json=update_data)
        assert resp.status_code == 200
        updated = resp.json()
        assert updated["name"] == "Updated Project"
        assert updated["project_type"] == "service_desk"

    def test_delete_project(self, client):
        # Создаём
        create_data = {"name": "Delete Project", "creator_id": 1}
        create_resp = client.post("/projects/", json=create_data)
        project_id = create_resp.json()["id"]

        # Удаляем
        resp = client.delete(f"/projects/{project_id}/")
        assert resp.status_code == 204

        # Проверяем
        get_resp = client.get(f"/projects/{project_id}")
        assert get_resp.status_code == 404