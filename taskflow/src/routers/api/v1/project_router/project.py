from fastapi import APIRouter, Depends, HTTPException
from src.core.dependencies import ProjectRepo,UserRepo
from src.schemas import Project, ProjectInDB
from src.services import ProjectService
from src.utils.loguru_config import AppLogger

router = APIRouter(prefix="/projects", tags=["Projects"])
logger = AppLogger().get_logger()


@router.post("/", response_model=Project)
def create_project(
        project: ProjectInDB,
        project_repo: ProjectRepo,
        user_repo: UserRepo, # Добавляем зависимость
) -> Project:
    return ProjectService().create(project, project_repo, user_repo)


@router.put("/{project_id}", response_model=Project)
def modify_project(
        project_id: int,
        project: ProjectInDB,
        repository: ProjectRepo,
        user_repo: UserRepo,  # Добавляем зависимость здесь
) -> Project:
    """Модифицировать проект"""
    if project.id != project_id:
        raise HTTPException(status_code=400, detail="ID в path не совпадает с body")

    # Теперь передаем user_repo
    return ProjectService().modify(project, repository, user_repo)


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
