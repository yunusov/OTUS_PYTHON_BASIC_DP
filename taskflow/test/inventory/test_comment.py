from src.utils.loguru_config import AppLogger
from test.utils import assert_json_equal

logger = AppLogger().get_logger()


def test_create_comment(comment_json, comments_api_url, client, project_user, token):
    """Тест создания комментария"""
    test_comment = comment_json.copy()
    test_comment["creator_id"] = project_user["id"]

    resp = client.post(
        comments_api_url % "",
        json=test_comment,
        headers={"Authorization": f"Bearer {token}"},
    )
    status_code = resp.status_code
    comment = resp.json()
    logger.debug(f"STATUS: {status_code}, BODY: {comment}")

    assert status_code == 200
    assert comment["id"]
    assert comment["task_id"] == test_comment["task_id"]
    assert comment["creator_id"] == test_comment["creator_id"]


def test_get_comment(comments_api_url, client, comment, token):
    """Тест получения комментария по ID"""
    comment_id = comment["id"]

    resp = client.get(
        comments_api_url % comment_id,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == comment_id


def test_get_task_comments(comments_api_url, client, comment, token):
    """Тест получения всех комментариев к задаче"""
    task_id = comment["task_id"]

    resp = client.get(
        comments_api_url % f"task/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    comments = resp.json()
    assert len(comments) >= 1
    assert comments[0]["task_id"] == task_id


def test_update_comment(comments_api_url, client, comment, token):
    """Тест обновления комментария"""
    comment_id = comment["id"]
    update_json = {
        "content": "Updated comment content",
        "task_id": comment["task_id"],
    }
    resp = client.put(
        comments_api_url % comment_id,
        json=update_json,
        headers={"Authorization": f"Bearer {token}"},
    )
    logger.info(resp.json())
    assert resp.status_code == 200
    assert resp.json()["content"] == update_json["content"]


def test_delete_comment(comments_api_url, client, comment, token):
    """Тест удаления комментария"""
    comment_id = comment["id"]
    resp = client.delete(
        comments_api_url % comment_id,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


def test_get_comment_not_found(comments_api_url, client, token):
    """Тест получения несуществующего комментария"""
    resp = client.get(
        comments_api_url % 99999,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
