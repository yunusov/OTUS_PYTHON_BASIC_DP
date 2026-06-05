from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
from typing import List
from sqlalchemy import select
import traceback

from src.core.dependencies import TaskRepo, ProjectRepo, DbSession
from src.core.database import get_db_helper
from src.models import UserOrm
from src.schemas import TaskCreate, TaskStatus, TaskPriority, UserRead
from src.schemas.project import ProjectRead
from src.services import TaskService, UserService
from src.utils.jinja_templates import templates
from src.utils.loguru_config import AppLogger
from src.utils.request_utils import async_request

logger = AppLogger().get_logger()
router = APIRouter()

db_helper = get_db_helper()


def get_current_user(request: Request):
    """Получить пользователя из сессии (как в login.py)"""
    access_token = request.session.get("access_token")
    if not access_token:
        return None

    try:
        user = UserService.get_me(request, access_token)
        return user
    except Exception as e:
        logger.error(f"get_current_user failed: {e}")
        return None


def get_projects_from_api(access_token: str, request: Request) -> list:
    """Загрузить проекты через API"""
    try:
        response = async_request(
            "GET",
            "/api/v1/projects/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            request=request,
        )
        return response if isinstance(response, list) else []
    except Exception as e:
        logger.error(f"get_projects_from_api failed: {e}")
        return []


def get_tasks_from_api(access_token: str, request: Request) -> list:
    """Загрузить задачи через API"""
    try:
        response = async_request(
            "GET",
            "/api/v1/tasks/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            request=request,
        )
        return response if isinstance(response, list) else []
    except Exception as e:
        logger.error(f"get_tasks_from_api failed: {e}")
        return []


@router.get("/tasks", response_class=HTMLResponse, name="tasks")
def tasks_page(request: Request):
    """Страница списка задач"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url=request.url_for("login"), status_code=303)

    access_token = request.session.get("access_token")
    projects = get_projects_from_api(access_token, request)
    tasks = get_tasks_from_api(access_token, request)

    return templates.TemplateResponse(
        request,
        "tasks/tasks_get.html",
        {
            "request": request,
            "user": user,
            "page_title": "Мои задачи",
            "projects": projects,
            "tasks": tasks,
        },
    )


@router.get("/tasks/create", response_class=HTMLResponse, name="create_task")
def create_task_page(
    request: Request,
    session: DbSession,
):
    """Страница создания задачи"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url=request.url_for("login"), status_code=303)

    access_token = request.session.get("access_token")
    projects = get_projects_from_api(access_token, request)

    # Получаем пользователей напрямую из БД
    users_db = session.execute(select(UserOrm).order_by(UserOrm.id)).scalars().all()
    users = [
        {"id": u.id, "username": u.username, "fullname": u.fullname} for u in users_db
    ]

    logger.info(f"create_task_page users: {users}")

    return templates.TemplateResponse(
        request,
        "tasks/tasks_create.html",
        {
            "request": request,
            "user": user,
            "page_title": "Создать задачу",
            "projects": projects,
            "users": users,
        },
    )


@router.post("/tasks/create", response_class=HTMLResponse)
def create_task_submit(
    request: Request,
    session: DbSession,
    name: str = Form(...),
    project_id: int | None = Form(None),
    description: str = Form(""),
    assignee_id: int | None = Form(None),
    due_date: str | None = Form(None),
    time_estimate: float | None = Form(None),
    status: str = Form(...),
    priority: str = Form(...),
):
    """Обработка создания задачи из веб-формы"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url=request.url_for("login"), status_code=303)

    access_token = request.session.get("access_token")

    # Получаем список пользователей для отображения при ошибках
    users_db = session.execute(select(UserOrm).order_by(UserOrm.id)).scalars().all()
    users = [
        {"id": u.id, "username": u.username, "fullname": u.fullname} for u in users_db
    ]

    logger.info(
        f"create_task_submit: name={name}, project_id={project_id}, assignee_id={assignee_id}"
    )

    if project_id:
        try:
            response = async_request(
                "GET",
                f"/api/v1/projects/{project_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
                request=request,
            )
            if response.get("detail") == "Project not found":
                projects = get_projects_from_api(access_token, request)
                return templates.TemplateResponse(
                    request,
                    "tasks/tasks_create.html",
                    {
                        "request": request,
                        "user": user,
                        "page_title": "Создать задачу",
                        "projects": projects,
                        "users": users,
                        "error": "Проект не найден",
                    },
                    status_code=400,
                )
        except Exception as e:
            logger.error(f"Check project failed: {e}")

    try:
        status_enum = TaskStatus(status)
        priority_enum = TaskPriority(priority)
    except ValueError as e:
        projects = get_projects_from_api(access_token, request)
        return templates.TemplateResponse(
            request,
            "tasks/tasks_create.html",
            {
                "request": request,
                "user": user,
                "page_title": "Создать задачу",
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
            projects = get_projects_from_api(access_token, request)
            return templates.TemplateResponse(
                request,
                "tasks/tasks_create.html",
                {
                    "request": request,
                    "user": user,
                    "page_title": "Создать задачу",
                    "projects": projects,
                    "users": users,
                    "error": "Некорректная дата срока выполнения",
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

    logger.info(f"task_data: {task_data.model_dump()}")

    try:
        response = async_request(
            "POST",
            "/api/v1/tasks/",
            data=task_data.model_dump_json(),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            request=request,
        )

        logger.info(f"Create task response: {response}")

        if detail := response.get("detail"):
            projects = get_projects_from_api(access_token, request)
            return templates.TemplateResponse(
                request,
                "tasks/tasks_create.html",
                {
                    "request": request,
                    "user": user,
                    "page_title": "Создать задачу",
                    "projects": projects,
                    "users": users,
                    "error": detail,
                },
                status_code=400,
            )

        logger.info(f"Task created successfully: {response}")
        return RedirectResponse(url=request.url_for("tasks"), status_code=303)

    except Exception as e:
        logger.error(f"Create task exception: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        projects = get_projects_from_api(access_token, request)
        return templates.TemplateResponse(
            request,
            "tasks/tasks_create.html",
            {
                "request": request,
                "user": user,
                "page_title": "Создать задачу",
                "projects": projects,
                "users": users,
                "error": "Ошибка при создании задачи",
            },
            status_code=500,
        )
