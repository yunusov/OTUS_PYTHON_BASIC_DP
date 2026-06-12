from fastapi import APIRouter, Form, Request, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
from typing import Dict
import json

from src.core.auth.session_user import get_current_user_from_session
from src.core.dependencies import (
    ProjectRepo,
    TaskRepo,
    CommentRepo,
    UserRepo,
)
from src.utils.jinja_templates import templates
from src.schemas import (
    UserRead,
    TaskCreate,
    TaskUpdate,
    TaskStatus,
    TaskPriority,
)
from src.services import (
    ProjectService,
    TaskService,
    UserService,
    CommentService,
)
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()
router = APIRouter(prefix="/tasks")

# Глобальное хранение подключений WebSocket
connected_users: Dict[int, WebSocket] = {}

ps = ProjectService()
ts = TaskService()
us = UserService()
cs = CommentService()


@router.get("/", response_class=HTMLResponse, name="tasks")
def index(
    request: Request,
    task_repository: TaskRepo,
    user: UserRead = Depends(get_current_user_from_session),
):
    """
    Отображает список всех задач текущего пользователя.
    """
    tasks = ts.get_user_tasks(user.id, task_repository)
    context = {
        "request": request,
        "user": user,
        "page_title": "Задачи",
        "tasks": tasks,
        "info": f"Ваши задачи, {user.fullname}",
    }
    return templates.TemplateResponse(
        request,
        "tasks/tasks_get.html",
        context,
    )


@router.get("/{task_id}/", response_class=HTMLResponse)
def task_view(
    request: Request,
    task_repository: TaskRepo,
    comment_repository: CommentRepo,
    task_id: int,
    user: UserRead = Depends(get_current_user_from_session),
):
    """
    Отображает детальную информацию о задаче по ID.
    """
    task = ts.get_by_id(task_id, task_repository)
    comments = cs.get_by_task_id(task_id, comment_repository)
    context = {
        "task": task,
        "comments": comments,
        "user": user,
    }
    return templates.TemplateResponse(
        request,
        "tasks/task_detail.html",
        context,
    )


@router.get("/create", response_class=HTMLResponse)
def task_create_get(
    request: Request,
    project_repository: ProjectRepo,
    user_repository: UserRepo,
    user: UserRead = Depends(get_current_user_from_session),
):
    """
    Отображает форму создания новой задачи.
    """
    projects = ps.get_by_creator_id(user.id, project_repository)
    users = us.get_all(user_repository)

    context = {
        "request": request,
        "user": user,
        "page_title": "Создать задачу",
        "form_action": f"/tasks/create",
        "button_text": "Создать",
        "projects": projects,
        "users": users,
    }
    return templates.TemplateResponse(
        request,
        "tasks/tasks_create.html",
        context,
    )


@router.post("/create", response_class=HTMLResponse)
def task_create_post(
    request: Request,
    task_repository: TaskRepo,
    project_repository: ProjectRepo,
    user_repository: UserRepo,
    name: str = Form(...),
    project_id: int | None = Form(None),
    description: str = Form(""),
    assignee_id: int | None = Form(None),
    due_date: str | None = Form(None),
    time_estimate: float | None = Form(None),
    status: str = Form(...),
    priority: str = Form(...),
    user: UserRead = Depends(get_current_user_from_session),
):
    """
    Обрабатывает создание новой задачи из формы.
    """
    # Проверка проекта
    if project_id:
        project = ps.get_by_id(project_id, project_repository)
        if not project:
            projects = ps.get_by_creator_id(user.id, project_repository)
            users = us.get_all(user_repository)
            return templates.TemplateResponse(
                request,
                "tasks/tasks_create.html",
                {
                    "request": request,
                    "user": user,
                    "page_title": "Создать задачу",
                    "form_action": f"/tasks/create",
                    "button_text": "Создать",
                    "projects": projects,
                    "users": users,
                    "error": "Проект не найден",
                },
                status_code=400,
            )

    # Валидация статуса и приоритета
    try:
        status_enum = TaskStatus(status)
        priority_enum = TaskPriority(priority)
    except ValueError as e:
        projects = ps.get_by_creator_id(user.id, project_repository)
        users = us.get_all(user_repository)
        return templates.TemplateResponse(
            request,
            "tasks/tasks_create.html",
            {
                "request": request,
                "user": user,
                "page_title": "Создать задачу",
                "form_action": f"/tasks/create",
                "button_text": "Создать",
                "projects": projects,
                "users": users,
                "error": f"Некорректный статус или приоритет: {e}",
            },
            status_code=400,
        )

    # Валидация даты
    due_date_dt = None
    if due_date:
        try:
            due_date_dt = datetime.fromisoformat(due_date)
        except ValueError:
            projects = ps.get_by_creator_id(user.id, project_repository)
            users = us.get_all(user_repository)
            return templates.TemplateResponse(
                request,
                "tasks/tasks_create.html",
                {
                    "request": request,
                    "user": user,
                    "page_title": "Создать задачу",
                    "form_action": f"/tasks/create",
                    "button_text": "Создать",
                    "projects": projects,
                    "users": users,
                    "error": "Некорректная дата",
                },
                status_code=400,
            )

    task_data = TaskCreate(
        name=name,
        project_id=project_id,
        description=description,
        status=status_enum,
        priority=priority_enum,
        assignee_id=assignee_id,
        time_estimate=int(time_estimate) if time_estimate else None,
        due_date=due_date_dt,
        creator_id=user.id,
    )

    task = ts.create(task_data, task_repository)

    return RedirectResponse(
        url=f"/tasks/?notification=created&id={task.id}&name={name}", status_code=303
    )


@router.get("/{task_id}/edit", response_class=HTMLResponse)
def task_edit_get(
    request: Request,
    task_repository: TaskRepo,
    task_id: int,
    user: UserRead = Depends(get_current_user_from_session),
):
    """
    Отображает форму редактирования задачи по ID.
    """
    task = ts.get_by_id(task_id, task_repository)

    context = {
        "task": task,
        "page_title": "Редактирование задачи",
        "form_action": f"/tasks/{task_id}/edit",
        "button_text": "Сохранить",
        "user": user,
    }
    return templates.TemplateResponse(
        request,
        "tasks/task_edit.html",
        context,
    )


@router.post("/{task_id}/edit", response_class=HTMLResponse)
def task_edit_post(
    request: Request,
    task_repository: TaskRepo,
    task_id: int,
    name: str = Form(...),
    project_id: int | None = Form(None),
    description: str = Form(""),
    assignee_id: int | None = Form(None),
    due_date: str | None = Form(None),
    time_estimate: float | None = Form(None),
    status: str = Form(...),
    priority: str = Form(...),
    user: UserRead = Depends(get_current_user_from_session),
):
    """
    Обрабатывает сохранение изменений задачи из формы.
    """
    # Валидация
    try:
        status_enum = TaskStatus.__members__[status]
        priority_enum = TaskPriority.__members__[priority]
    except KeyError as e:
        task = ts.get_by_id(task_id, task_repository)
        return templates.TemplateResponse(
            request,
            "tasks/task_edit.html",
            {
                "request": request,
                "user": user,
                "task": task,
                "page_title": "Редактирование задачи",
                "form_action": f"/tasks/{task_id}/edit",
                "button_text": "Сохранить",
                "error": f"Некорректный статус или приоритет: {e}",
            },
            status_code=400,
        )

    task_update = TaskUpdate(
        name=name,
        project_id=project_id,
        description=description,
        status=status_enum,
        priority=priority_enum,
        assignee_id=assignee_id,
        time_estimate=int(time_estimate) if time_estimate else None,
        due_date=datetime.fromisoformat(due_date) if due_date else None,
    )

    ts.modify(task_id, task_update, task_repository)
    return RedirectResponse(url=request.url_for("tasks"), status_code=303)


# WebSocket удален (не нужен для простого уведомления)
