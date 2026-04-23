from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from taskflow.src.utils.loguru_config import AppLogger
from taskflow.src.repositories.task_repository import TaskRepository
from taskflow.src.schemas.task import (
    TaskCreate, TaskUpdate, TaskOut,
)
from taskflow.src.core.database import DbSession, get_db_session

router = APIRouter(prefix="/tasks", tags=["Tasks"])
logger = AppLogger().get_logger()


def get_task_repository(session: DbSession):
    return TaskRepository(session)

TaskRepo = Annotated[TaskRepository, Depends(get_task_repository)]


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, repository: TaskRepo) -> TaskOut:
    """Создать новую задачу"""
    try:
        task_orm = repository.create(task)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="project_id или assignee_id/creator_id не существует"
        )

    logger.info(f"Задача создана: ID={task_orm.id}")
    return TaskOut.model_validate(task_orm)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, repository: TaskRepo) -> TaskOut:
    """Получить задачу по ID"""
    task = repository.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return TaskOut.model_validate(task)


@router.get("/", response_model=list[TaskOut])
def get_tasks(project_id: int, repository: TaskRepo) -> list[TaskOut]:
    """Получить все задачи проекта"""
    tasks = repository.get_by_project(project_id)
    return [TaskOut.model_validate(task) for task in tasks]


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    repository: TaskRepo
) -> TaskOut:
    """Обновить задачу"""
    task_orm = repository.update(task_id, task_data)
    if not task_orm:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return TaskOut.model_validate(task_orm)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, repository: TaskRepo) -> None:
    """Удалить задачу"""
    if not repository.delete(task_id):
        raise HTTPException(status_code=404, detail="Задача не найдена")