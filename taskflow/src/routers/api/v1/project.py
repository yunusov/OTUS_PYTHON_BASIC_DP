from fastapi import APIRouter, HTTPException
from src.core.dependencies import ProjectRepo
from src.core.config import settings
from src.schemas import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)
from src.services import ProjectService
from src.utils.loguru_config import AppLogger

router = APIRouter(prefix=settings.api.v1.projects, tags=["Projects"])
logger = AppLogger().get_logger()


@router.post("/", response_model=ProjectRead)
def create_project(
    project: ProjectCreate,
    repository: ProjectRepo,
) -> ProjectRead:
    """Создать проект"""
    return ProjectService().create(project, repository)


@router.put("/{project_id}", response_model=ProjectRead)
def modify_project(
    project_id: int,
    project: ProjectUpdate,
    repository: ProjectRepo,
) -> ProjectRead:
    """Модифицировать проект"""
    return ProjectService().modify(project_id, project, repository)


@router.delete("/{project_id}")
def remove_project(
    project_id: int,
    repository: ProjectRepo,
) -> bool:
    """Удалить проект"""
    return ProjectService().delete(project_id, repository)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    repository: ProjectRepo,
) -> ProjectRead:
    """Получить проект по ID"""
    project = repository.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return ProjectRead.model_validate(project)
