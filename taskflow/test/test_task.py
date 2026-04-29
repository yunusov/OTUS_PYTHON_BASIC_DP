# tests/tasks/test_tasks.py

from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


# def test_create_task(task_json, server_url, client):
#     resp = client.post(
#         f"{server_url}/tasks/",
#         json=task_json,
#     )
#     assert resp.status_code == 200
#     resp_json = resp.json()
#     # сравниваем поля, кроме id/created_at
#     for key, val in task_json.items():
#         if key not in ("id", "created_at"):
#             assert resp_json[key] == val, f"Mismatch on {key}"
#     assert "id" in resp_json
#     assert "created_at" in resp_json


# def test_modify_task(task_json, server_url, client):
#     # 1. создаём задачу
#     resp = client.post(
#         f"{server_url}/tasks/",
#         json=task_json,
#     )
#     assert resp.status_code == 200
#     created = resp.json()

#     # 2. модифицируем
#     modified = task_json.copy()
#     modified["id"] = created["id"]
#     modified["title"] = "Updated task title"
#     modified["description"] = "Updated description"

#     resp = client.put(
#         f"{server_url}/tasks/{created['id']}",
#         json=modified,
#     )
#     assert resp.status_code == 200
#     resp_json = resp.json()
#     assert resp_json["title"] == "Updated task title"
#     assert resp_json["description"] == "Updated description"


# def test_modify_task_not_found(server_url, client):
#     invalid_id = 999999
#     data = {
#         "id": invalid_id,
#         "title": "Some task",
#         "description": "desc",
#     }
#     resp = client.put(
#         f"{server_url}/tasks/{invalid_id}",
#         json=data,
#     )
#     # у тебя в сервисе raise ValueError с "Задача с таким ID не существует!"
#     assert resp.status_code == 404  # или 400, если так настроено
#     resp_json = resp.json()
#     assert (
#         "Задача с таким ID не существует!" in resp_json["detail"]
#         or "not found" in resp_json["detail"].lower()
#     )


# def test_delete_task(task_json, server_url, client):
#     # 1. создаём
#     resp = client.post(
#         f"{server_url}/tasks/",
#         json=task_json,
#     )
#     assert resp.status_code == 200
#     created = resp.json()

#     # 2. удаляем
#     resp = client.delete(
#         f"{server_url}/tasks/{created['id']}",
#     )
#     assert resp.status_code == 200
#     resp_json = resp.json()
#     assert resp_json["success"]  # или {"deleted": True}, подправь под свой формат

#     # 3. проверяем, что больше не доступна
#     resp = client.get(
#         f"{server_url}/tasks/{created['id']}",
#     )
#     assert resp.status_code in (404, 400)  # как ты возвращаешь для несуществующей задачи


# def test_task_constraints(task_json, server_url, client):
#     # 1. слишком короткий title
#     bad_title = task_json.copy()
#     bad_title["title"] = "x"
#     resp = client.post(
#         f"{server_url}/tasks/",
#         json=bad_title,
#     )
#     assert resp.status_code == 422
#     resp_json = resp.json()
#     assert "title" in resp_json["detail"][0]["loc"]
#     assert "short" in resp_json["detail"][0]["msg"].lower()

#     # 2. слишком длинное description
#     long_desc = task_json.copy()
#     long_desc["title"] = "Valid title"
#     long_desc["description"] = "a" * 1001
#     resp = client.post(
#         f"{server_url}/tasks/",
#         json=long_desc,
#     )
#     assert resp.status_code == 422
#     resp_json = resp.json()
#     assert "description" in resp_json["detail"][0]["loc"]
#     assert "too long" in resp_json["detail"][0]["msg"].lower()

