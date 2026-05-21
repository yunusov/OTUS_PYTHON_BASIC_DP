from fastapi import APIRouter, Depends, HTTPException

from src.core.auth.fastapi_users import fastapi_users
from src.core.dependencies import ProjectRepo,get_project_repository
from src.core.config import settings
from src.models import UserOrm
from src.schemas import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    ProjectMembersAdd,
)
from src.services import ProjectService
from src.utils.loguru_config import AppLogger

# Получить текущего активного пользователя (любого авторизованного)
current_active_user = fastapi_users.current_user(active=True)

# Получить текущего суперпользователя
current_superuser = fastapi_users.current_user(active=True, superuser=True)

router = APIRouter(prefix=settings.api.v1.projects, tags=["Projects"])
logger = AppLogger().get_logger()


@router.post("/", response_model=ProjectRead)
def create_project(
    project: ProjectCreate,
    repository: ProjectRepo,
    user: UserOrm = Depends(current_active_user),
) -> ProjectRead:
    """Создать проект"""
    return ProjectService().create(project, repository)


@router.put("/{project_id}", response_model=ProjectRead)
def modify_project(
    project_id: int,
    project: ProjectUpdate,
    repository: ProjectRepo,
    user: UserOrm = Depends(current_active_user),
) -> ProjectRead:
    """Модифицировать проект"""
    return ProjectService().modify(project_id, project, repository)


@router.delete("/{project_id}")
def remove_project(
    project_id: int,
    repository: ProjectRepo,
    # user: UserOrm = Depends(current_superuser),  # ← только суперюзер
    user: UserOrm = Depends(current_active_user),
) -> bool:
    """Удалить проект"""
    return ProjectService().delete(project_id, repository)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    repository: ProjectRepo,
    user: UserOrm = Depends(current_active_user),
) -> ProjectRead:
    """Получить проект по ID"""
    project = repository.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return ProjectRead.model_validate(project)

@router.post("/{project_id}/members", response_model=ProjectRead)
def add_members(
    project_id: int,
    data: ProjectMembersAdd,
    repository: ProjectRepo,
):
    return ProjectService().add_members(project_id, data, repository)
