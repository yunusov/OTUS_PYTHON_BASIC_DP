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


@router.get("/", response_class=HTMLResponse, name="comments")
def index(
    request: Request,
    repository: CommentRepo,
    user: UserRead = Depends(get_current_user_from_session),
):
    comments = cs.get_user_comments(user.id, repository)
    context = {
        "request": request,
        "user": user,
        "comments": comments,
    }
    return templates.TemplateResponse(
        request,
        "comments.html",
        context,
    )


@router.get("/{comment_id}/edit", response_class=HTMLResponse)
def comment_edit_get(
    request: Request,
    comment_repository: CommentRepo,
    task_repository: TaskRepo,
    comment_id: int,
    user: UserRead = Depends(get_current_user_from_session),
):
    comment = cs.get_by_id(comment_id, comment_repository)
    tasks = ts.get_user_tasks(user.id, task_repository)
    context = {
        "comment": comment,
        "page_title": "Редактирование комментария",
        "form_action": f"/comments/{comment_id}/edit",
        "button_text": "Сохранить",
        "tasks": tasks,
        "user": user,
    }
    return templates.TemplateResponse(
        request,
        "comment_edit.html",
        context,
    )


@router.post("/{comment_id}/edit", response_class=HTMLResponse)
def comment_edit_post(
    request: Request,
    comment_repository: CommentRepo,
    comment_id: int,
    content: str = Form(...),
    task_id: int = Form(...),
    user: UserRead = Depends(get_current_user_from_session),
):
    comment_update = CommentUpdate(
        content=content,
        task_id=task_id,
    )
    cs.modify(comment_id, comment_update, comment_repository)
    return RedirectResponse(f"/tasks/{task_id}/", status_code=302)


@router.get("/create", response_class=HTMLResponse)
def comment_create_get(
    request: Request,
    task_repository: TaskRepo,
    user: UserRead = Depends(get_current_user_from_session),
):
    tasks = ts.get_user_tasks(user.id, task_repository)
    context = {
        "request": request,
        "user": user,
        "page_title": "Создание комментария",
        "form_action": f"/comments/create",
        "button_text": "Создать",
        "tasks": tasks,
    }
    return templates.TemplateResponse(
        request,
        "comment_edit.html",
        context,
    )


@router.post("/create", response_class=HTMLResponse)
def comment_create_post(
    request: Request,
    comment_repository: CommentRepo,
    task_repository: TaskRepo,
    content: str = Form(...),
    task_id: int = Form(...),
    user: UserRead = Depends(get_current_user_from_session),
):
    # Проверка задачи
    task = ts.get_by_id(task_id, task_repository)
    if not task:
        tasks = ts.get_user_tasks(user.id, task_repository)
        return templates.TemplateResponse(
            request,
            "comment_edit.html",
            {
                "request": request,
                "user": user,
                "page_title": "Создание комментария",
                "form_action": f"/comments/create",
                "button_text": "Создать",
                "tasks": tasks,
                "error": "Задача не найдена",
            },
            status_code=400,
        )

    comment_create = CommentCreate(
        content=content,
        task_id=task_id,
        creator_id=user.id,
    )
    comment = cs.create(comment_create, comment_repository)
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
