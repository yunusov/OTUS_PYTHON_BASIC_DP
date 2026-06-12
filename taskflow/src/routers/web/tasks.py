from fastapi import (
    APIRouter,
    Form,
    Query,
    Request,
    Depends,
)
from fastapi import APIRouter, Form, Query, Request, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime

from src.core.ws_manager import ws_manager

from src.core.auth.session_user import get_current_user_from_session
from src.core.auth.user_manager import UserManager
from src.core.dependencies import (
    ProjectRepo,
    TaskRepo,
    CommentRepo,
    UserRepo,
)
from src.routers.api.dependencies.auth.user_manager import get_user_manager
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
from src.utils.jinja_templates import templates
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()
router = APIRouter(prefix="/tasks")


ps = ProjectService()
ts = TaskService()
us = UserService()
cs = CommentService()


@router.get("/", response_class=HTMLResponse, name="tasks")
def index(
    request: Request,
    task_repository: TaskRepo,
    sort_by: str = Query("name"),
    sort_dir: str = Query("asc"),
    user: UserRead = Depends(get_current_user_from_session),
):
    """
    Отображает список всех задач текущего пользователя.
    """
    tasks = ts.get_user_tasks(
        user.id,
        task_repository,
        sort_by,
        sort_dir,
    )
    context = {
        "request": request,
        "user": user,
        "page_title": "Задачи",
        "tasks": tasks,
        "show_tab_all": False,
        "current_sort": sort_by,
        "current_dir": sort_dir,
        "info": f"Ваши задачи, {user.fullname}",
        "show_tab_all": False,
        "current_sort": sort_by,
        "current_dir": sort_dir,
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
    project_repository: ProjectRepo,
    task_id: int,
    user: UserRead = Depends(get_current_user_from_session),
):
    """
    Отображает детальную информацию о задаче по ID.
    """
    task = ts.get_by_id(task_id, task_repository)
    project = None
    if task and task.project_id:
        project = ps.get_by_id(task.project_id, project_repository)
    comments = cs.get_by_task_id(task_id, comment_repository)
    context = {
        "task": task,
        "comments": comments,
        "project": project,
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
    return task_create_form(request, project_repository, user_repository, None, user)


@router.get("/create/{project_id}", response_class=HTMLResponse)
def task_project_create_get(
    request: Request,
    project_repository: ProjectRepo,
    user_repository: UserRepo,
    project_id: int | None = None,
    user: UserRead = Depends(get_current_user_from_session),
):
    """
    Отображает форму создания новой задачи.
    """
    return task_create_form(
        request, project_repository, user_repository, project_id, user
    )


def task_create_form(
    request: Request,
    project_repository: ProjectRepo,
    user_repository: UserRepo,
    project_id: int | None = None,
    user: UserRead = Depends(get_current_user_from_session),
):
    projects = ps.get_by_creator_id(project_repository, user.id)
    users = us.get_all(user_repository)

    context = {
        "request": request,
        "user": user,
        "page_title": "Создать задачу",
        "form_action": f"/tasks/create",
        "button_text": "Создать",
        "project_id": project_id,
        "projects": projects,
        "users": users,
    }
    return templates.TemplateResponse(
        request,
        "tasks/tasks_create.html",
        context,
    )


@router.post("/create", response_class=HTMLResponse)
async def task_create_post(
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
    user_manager: UserManager = Depends(get_user_manager),
):
    if project_id:
        project = ps.get_by_id(project_id, project_repository)
        if not project:
            projects = ps.get_by_creator_id(project_repository, user.id)
            users = us.get_all(user_repository)
            return templates.TemplateResponse(
                request,
                "tasks/tasks_create.html",
                {
                    "request": request,
                    "user": user,
                    "page_title": "Создать задачу",
                    "form_action": "/tasks/create",
                    "button_text": "Создать",
                    "projects": projects,
                    "users": users,
                    "error": "Проект не найден",
                },
                status_code=400,
            )

    try:
        status_enum = TaskStatus(status)
        priority_enum = TaskPriority(priority)
    except ValueError as e:
        projects = ps.get_by_creator_id(project_repository, user.id)
        users = us.get_all(user_repository)
        return templates.TemplateResponse(
            request,
            "tasks/tasks_create.html",
            {
                "request": request,
                "user": user,
                "page_title": "Создать задачу",
                "form_action": "/tasks/create",
                "button_text": "Создать",
                "projects": projects,
                "users": users,
                "error": f"Некорректный статус или приоритет: {e}",
            },
            status_code=400,
        )

    due_date_dt = None
    if due_date:
        try:
            due_date_dt = datetime.fromisoformat(due_date)
        except ValueError:
            projects = ps.get_by_creator_id(project_repository, user.id)
            users = us.get_all(user_repository)
            return templates.TemplateResponse(
                request,
                "tasks/tasks_create.html",
                {
                    "request": request,
                    "user": user,
                    "page_title": "Создать задачу",
                    "form_action": "/tasks/create",
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

    task = await ts.create(task_data, task_repository, user_manager)
    return RedirectResponse(url=f"{task.id}", status_code=302)

    await ws_manager.send_personal(
        user.id,
        {
            "type": "task_created",
            "title": "Задача создана",
            "message": f"Вы создали задачу: {task.name}",
            "task_id": task.id,
            "url": f"/tasks/{task.id}/",
        },
    )

    if task.assignee_id:
        await ws_manager.send_personal(
            task.assignee_id,
            {
                "type": "task_assigned",
                "title": "Новая задача",
                "message": f"Вам назначена задача: {task.name}",
                "task_id": task.id,
                "url": f"/tasks/{task.id}/",
            },
        )

    return RedirectResponse(
        url=f"/tasks/?notification=created&id={task.id}&name={name}",
        status_code=303,
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
async def task_edit_post(
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
    user_manager: UserManager = Depends(get_user_manager),
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

    await ts.modify(task_id, task_update, task_repository, user_manager)
    return RedirectResponse(url=request.url_for("tasks"), status_code=303)
