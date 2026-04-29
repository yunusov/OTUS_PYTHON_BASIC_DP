# src/api/project.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.core.dependencies import DbSession, ProjectRepo
from src.models.project import ProjectOrm
from src.repositories.project_repository import ProjectRepository
from src.schemas.project import Project
from src.utils.loguru_config import AppLogger


router = APIRouter(prefix="/projects", tags=["Projects"])
logger = AppLogger().get_logger()


@router.post("/")
def create_project(
    data: Project,
    repo: ProjectRepo,
) -> Project:
    logger.info("data")
    try:
        projectOrm = ProjectOrm(data)
        repo.create(projectOrm)
        repo.save()
        logger.info(f"Проект {data} создан")
        return Project.model_validate(projectOrm)
    except IntegrityError:
        logger.info("creator_id не существует")
        raise HTTPException(400, "creator_id не существует")


@router.get("/{project_id}", response_model=Project)
def get_project(
    project_id: int,
    repo: ProjectRepo,
) -> Project:
    project = repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project


@router.get("/", response_model=list[Project])
def get_projects(
    creator_id: int,
    repo: ProjectRepo,
) -> str:
    # projects = repo.get_all(creator_id=creator_id)
    return "projects"


@router.put("/{project_id}", response_model=Project)
def update_project(
    project_id: int,
    project_data: Project,
    repo: ProjectRepo,
) -> str:
    # project_data.id = project_id
    # project = repo.modify(project_data)
    # if not project:
    #     raise HTTPException(status_code=404, detail="Проект не найден")
    return "project"


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    repo: ProjectRepo,
) -> None:
    # if not repo.delete(project_id):
    #     raise HTTPException(status_code=404, detail="Проект не найден")
    ...