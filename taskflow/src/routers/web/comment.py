from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from src.core.auth.session_user import get_current_user_from_session
from src.core.auth.user_manager import UserManager
from src.core.dependencies import TaskRepo, CommentRepo, UserRepo
from src.routers.api.dependencies.auth.user_manager import get_user_manager
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


@router.get("/{comment_id}", response_class=HTMLResponse)
def comment_view(
    comment_id: int,
    comment_repository: CommentRepo,
):
    comment = cs.get_by_id(comment_id, comment_repository)
    if not comment:
        return RedirectResponse(f"/tasks/", status_code=302)
    return RedirectResponse(f"/tasks/{comment.task_id}/#comment-{comment_id}", status_code=302)


@router.post("/create", response_class=HTMLResponse)
async def comment_create_post(
    request: Request,
    comment_repository: CommentRepo,
    task_repository: TaskRepo,
    ur: UserRepo,
    content: str = Form(...),
    task_id: int = Form(...),
    user: UserRead = Depends(get_current_user_from_session),
    user_manager: UserManager = Depends(get_user_manager),
):
    task = ts.get_by_id(task_id, task_repository)
    if not task:
        return RedirectResponse(url="/tasks/", status_code=302)

    comment_create = CommentCreate(
        content=content,
        task_id=task_id,
        creator_id=user.id,
    )
    await cs.create(comment_create, comment_repository, user_manager, task_repository, ur)
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
    if not comment:
        return RedirectResponse(f"/tasks/", status_code=302)

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

    if not comment:
        return RedirectResponse(f"/tasks/", status_code=302)
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
