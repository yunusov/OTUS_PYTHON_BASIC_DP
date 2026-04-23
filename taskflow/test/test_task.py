import pytest
from datetime import datetime
from taskflow.src.schemas.task import TaskStatus, TaskPriority


class TestTaskCRUD:
    """CRUD тесты для задач"""

    @pytest.mark.parametrize("name", ["", "a" * 256])
    def test_create_task_invalid_name(self, client, name):
        data = {"name": name, "creator_id": 1, "project_id": 1}
        resp = client.post("/tasks/", json=data)
        assert resp.status_code == 422
        assert "length" in str(resp.json())

    def test_create_task_success(self, client):
        data = {
            "name": "Test Task",
            "creator_id": 1,
            "project_id": 1,
            "status": TaskStatus.TODO.value,
            "priority": TaskPriority.HIGH.value
        }
        resp = client.post("/tasks/", json=data)
        assert resp.status_code == 201
        json_data = resp.json()
        assert json_data["name"] == "Test Task"
        assert json_data["status"] == "todo"
        assert "id" in json_data
        assert "created_at" in json_data

    def test_get_task_not_found(self, client):
        resp = client.get("/tasks/999")
        assert resp.status_code == 404

    def test_get_tasks_empty(self, client):
        resp = client.get("/tasks?project_id=999")
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    def test_update_task_partial(self, client):
        # Создаём задачу
        create_data = {"name": "Update Me", "creator_id": 1, "project_id": 1}
        create_resp = client.post("/tasks/", json=create_data)
        task_id = create_resp.json()["id"]

        # Частичное обновление
        update_data = {
            "status": "in_progress",
            "priority": "critical",
            "time_spent": 120
        }
        resp = client.put(f"/tasks/{task_id}/", json=update_data)
        assert resp.status_code == 200
        updated = resp.json()
        assert updated["status"] == "in_progress"
        assert updated["priority"] == "critical"
        assert updated["time_spent"] == 120

    def test_delete_task(self, client):
        # Создаём
        create_data = {"name": "Delete Me", "creator_id": 1, "project_id": 1}
        create_resp = client.post("/tasks/", json=create_data)
        task_id = create_resp.json()["id"]

        # Удаляем
        resp = client.delete(f"/tasks/{task_id}/")
        assert resp.status_code == 204

        # Проверяем удаление
        get_resp = client.get(f"/tasks/{task_id}")
        assert get_resp.status_code == 404