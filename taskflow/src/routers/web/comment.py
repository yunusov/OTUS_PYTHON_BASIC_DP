from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from src.core.auth.session_user import get_current_user_from_session
from src.core.dependencies import TaskRepo, CommentRepo
from src.utils.jinja_templates import templates
from src.schemas import (
    UserRead,
    CommentCreate,
    CommentUpdate,
)
from src.services import TaskService, CommentService
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()
router = APIRouter(prefix="/comments")
cs = CommentService()
ts = TaskService()


@router.post("/create", response_class=HTMLResponse)
def comment_create_post(
    request: Request,
    comment_repository: CommentRepo,
    task_repository: TaskRepo,
    content: str = Form(...),
    task_id: int = Form(...),
    user: UserRead = Depends(get_current_user_from_session),
):
    task = ts.get_by_id(task_id, task_repository)
    if not task:
        return RedirectResponse(url="/tasks/", status_code=302)

    comment_create = CommentCreate(
        content=content,
        task_id=task_id,
        creator_id=user.id,
    )
    cs.create(comment_create, comment_repository)
    return RedirectResponse(f"/tasks/{task_id}/", status_code=302)


@router.post("/{comment_id}/delete", response_class=HTMLResponse)
def comment_delete(
    request: Request,
    comment_repository: CommentRepo,
    comment_id: int,
    user: UserRead = Depends(get_current_user_from_session),
):
    """Удалить комментарий"""
    comment = cs.get_by_id(comment_id, comment_repository)

    # Проверка: только автор может удалять
    if user.id != comment.creator_id:
        return RedirectResponse(url="/comments/", status_code=302)

    cs.delete(comment_id, comment_repository)
    return RedirectResponse(url="/tasks/", status_code=302)


@router.post("/{comment_id}/edit-inline", response_class=HTMLResponse)
def comment_edit_inline(
    request: Request,
    comment_repository: CommentRepo,
    comment_id: int,
    content: str = Form(...),
    user: UserRead = Depends(get_current_user_from_session),
):
    """Inline-редактирование комментария (прямо на странице задачи)"""
    comment = cs.get_by_id(comment_id, comment_repository)

    # Проверка: только автор может редактировать
    if user.id != comment.creator_id:
        return RedirectResponse(url="/tasks/", status_code=302)

    comment_update = CommentUpdate(
        content=content,
        task_id=comment.task_id,
    )
    cs.modify(comment_id, comment_update, comment_repository)

    # Редирект на ту же задачу
    return RedirectResponse(f"/tasks/{comment.task_id}/", status_code=302)
