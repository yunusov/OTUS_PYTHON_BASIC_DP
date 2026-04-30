from fastapi import APIRouter, Depends, HTTPException
from src.core.dependencies import ProjectRepo
from src.schemas import Project, ProjectInDB
from src.services import ProjectService
from src.utils.loguru_config import AppLogger

router = APIRouter(prefix="/projects", tags=["Projects"])
logger = AppLogger().get_logger()


@router.post("/", response_model=Project)
def create_project(
        project: ProjectInDB,
        repository: ProjectRepo ,
) -> Project:
    """Создать проект"""
    return ProjectService().create(project, repository)


@router.put("/{project_id}", response_model=Project)
def modify_project(
        project_id: int,
        project: ProjectInDB,
        repository: ProjectRepo,
) -> Project:
    """Модифицировать проект"""
    if project.id != project_id:
        raise HTTPException(status_code=400, detail="ID в path не совпадает с body")
    return ProjectService().modify(project, repository)


@router.delete("/{project_id}")
def remove_project(
        project_id: int,
        repository: ProjectRepo ,
) -> bool:
    """Удалить проект"""
    return ProjectService().delete(project_id, repository)


@router.get("/{project_id}", response_model=Project)
def get_project(
        project_id: int,
        repository: ProjectRepo,
) -> Project:
    """Получить проект по ID"""
    project = repository.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return Project.model_validate(project)
