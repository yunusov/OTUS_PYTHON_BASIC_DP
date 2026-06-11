from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from src.core.auth.session_user import get_current_user_from_session
from src.core.dependencies import ProjectRepo, TaskRepo, UserRepo
from src.utils.jinja_templates import templates
from src.schemas import (
    UserRead,
    ProjectCreate,
    ProjectType,
    ProjectUpdate,
    ProjectMembersAdd
)
from src.services import ProjectService, TaskService, UserService
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()
router = APIRouter(prefix="/projects")
ps = ProjectService()
ts = TaskService()
us = UserService()


@router.get("/", response_class=HTMLResponse, name="projects")
def index(
    request: Request,
    repository: ProjectRepo,
    user: UserRead = Depends(get_current_user_from_session),
):
    projects = ps.get_by_creator_id(user.id, repository)
    context = {
        "request": request,
        "user": user,
        "projects": projects,
    }
    return templates.TemplateResponse(
        request,
        "projects/projects.html",
        context,
    )


@router.get("/{project_id}/", response_class=HTMLResponse)
def project_view(
    request: Request,
    project_repository: ProjectRepo,
    user_repository: UserRepo,
    task_repository: TaskRepo,
    project_id: int,
    user: UserRead = Depends(get_current_user_from_session),
):
    project = ps.get_by_id(project_id, project_repository)
    tasks = ts.get_by_project_id(project_id, task_repository)
    project_users = us.get_users_by_project(project_id, user_repository)
    context = {
        "project": project,
        "tasks": tasks,
        "user": user,
        "project_users": project_users,
    }
    return templates.TemplateResponse(
        request,
        "projects/project_detail.html",
        context,
    )


@router.get("/{project_id}/edit", response_class=HTMLResponse)
def project_edit_get(
    request: Request,
    project_repository: ProjectRepo,
    user_repository: UserRepo,
    project_id: int,
    user: UserRead = Depends(get_current_user_from_session),
):
    project = ps.get_by_id(project_id, project_repository)
    verified_users = us.get_all_verified_by_project(user_repository, project_id)
    logger.info(f"{verified_users=}")
    context = {
        "project": project,
        "page_title": "Редактирование проекта",
        "form_action": f"/projects/{project_id}/edit",
        "button_text": "Сохранить",
        "user": user,
        "verified_users": verified_users,
    }
    return templates.TemplateResponse(
        request,
        "projects/project_edit.html",
        context,
    )


@router.post("/{project_id}/edit", response_class=HTMLResponse)
def project_edit_post(
    request: Request,
    project_repository: ProjectRepo,
    project_id: int,
    name: str = Form(...),
    description: str = Form(""),
    project_type: str = Form(...),
    assigned_users: list = Form(None),
    user: UserRead = Depends(get_current_user_from_session),
):
    logger.info(f"{assigned_users=}")
    project_update = ProjectUpdate(
        name=name,
        description=description,
        project_type=ProjectType(project_type),
    )
    ps.modify(project_id, project_update, project_repository)
    ps.add_members(project_id, ProjectMembersAdd(user_ids=assigned_users), project_repository)
    return RedirectResponse(f"/projects/{project_id}/", status_code=302)


@router.get("/create", response_class=HTMLResponse)
def project_create_get(
    request: Request,
    user_repository: UserRepo,
    user: UserRead = Depends(get_current_user_from_session),
):
    verified_users = us.get_all_verified(user_repository)
    context = {
        "page_title": "Создание проекта",
        "form_action": f"/projects/create",
        "button_text": "Создать",
        "user": user,
        "verified_users": verified_users,
    }
    return templates.TemplateResponse(
        request,
        "projects/project_edit.html",
        context,
    )


@router.post("/create", response_class=HTMLResponse)
def project_create_post(
    request: Request,
    project_repository: ProjectRepo,
    name: str = Form(...),
    description: str = Form(""),
    project_type: str = Form(...),
    user: UserRead = Depends(get_current_user_from_session),
    assigned_users: list = Form(None),
):
    project_update = ProjectCreate(
        name=name,
        description=description,
        project_type=ProjectType(project_type),
        creator_id=user.id,
    )
    project = ps.create(project_update, project_repository)
    ps.add_members(project.id, ProjectMembersAdd(user_ids=assigned_users), project_repository)
    return RedirectResponse(f"/projects/{project.id}/", status_code=302)
