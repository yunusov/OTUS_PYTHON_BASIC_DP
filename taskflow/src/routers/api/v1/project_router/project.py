# src/api/project.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.utils.loguru_config import AppLogger
from src.core.dependencies import DbSession
from src.repositories.project_repository import ProjectRepository
from src.schemas.project import Project


router = APIRouter(prefix="/projects", tags=["Projects"])
logger = AppLogger().get_logger()


def get_project_repo(session: Session = Depends(DbSession)):
    return ProjectRepository(session)


@router.post("/",  status_code=status.HTTP_201_CREATED)
def create_project(
    data: Project,
    repo: ProjectRepository = Depends(get_project_repo),
) -> None:
    try:
        repo.create(data)
        return None
    except IntegrityError:
        raise HTTPException(400, "creator_id не существует")


@router.get("/{project_id}", response_model=Project)
def get_project(
    project_id: int,
    repo: ProjectRepository = Depends(get_project_repo),
) -> Project:
    project = repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project


@router.get("/", response_model=list[Project])
def get_projects(
    creator_id: int | None = None,
    repo: ProjectRepository = Depends(get_project_repo),
) -> list[Project]:
    projects = repo.get_all(creator_id=creator_id)
    return projects


@router.put("/{project_id}", response_model=Project)
def update_project(
    project_id: int,
    project_data: Project,
    repo: ProjectRepository = Depends(get_project_repo),
) -> Project:
    project_data.id = project_id
    project = repo.modify(project_data)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    repo: ProjectRepository = Depends(get_project_repo),
) -> None:
    if not repo.delete(project_id):
        raise HTTPException(status_code=404, detail="Проект не найден")