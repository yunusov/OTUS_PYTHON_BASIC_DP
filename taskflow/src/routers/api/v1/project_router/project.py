from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from taskflow.src.utils.loguru_config import AppLogger
from taskflow.src.repositories.project_repository import ProjectRepository
from taskflow.src.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectOut,
)
from taskflow.src.core.database import DbSession, get_db_session

router = APIRouter(prefix="/projects", tags=["Projects"])
logger = AppLogger().get_logger()


def get_project_repository(session: DbSession):
    return ProjectRepository(session)


ProjectRepo = Annotated[ProjectRepository, Depends(get_project_repository)]


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, repository: ProjectRepo) -> ProjectOut:
    """Создать новый проект"""
    try:
        project_orm = repository.create(project)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="creator_id не существует"
        )

    logger.info(f"Проект создан: ID={project_orm.id}")
    return ProjectOut.model_validate(project_orm)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, repository: ProjectRepo) -> ProjectOut:
    """Получить проект по ID"""
    project = repository.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return ProjectOut.model_validate(project)


@router.get("/creator/{creator_id}", response_model=list[ProjectOut])
def get_projects_by_creator(creator_id: int, repository: ProjectRepo) -> list[ProjectOut]:
    """Получить проекты создателя"""
    projects = repository.get_by_creator(creator_id)
    return [ProjectOut.model_validate(p) for p in projects]


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    repository: ProjectRepo
) -> ProjectOut:
    project = repository.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    project_orm = repository.update(project_id, project_data)
    if not project_orm:
        raise HTTPException(status_code=404, detail="Проект не найден")

    return ProjectOut.model_validate(project_orm)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, repository: ProjectRepo) -> None:
    """Удалить проект"""
    if not repository.delete(project_id):
        raise HTTPException(status_code=404, detail="Проект не найден")