from fastapi import APIRouter, Depends, HTTPException

from src.core.dependencies import TaskRepo
from src.schemas.task import Task, TaskInDB
from src.services.task_service import TaskService
from src.utils.loguru_config import AppLogger


router = APIRouter(prefix="/tasks", tags=["Tasks"])
logger = AppLogger().get_logger()


@router.post("/", response_model=Task)
def create_task(
    task: TaskInDB,
    repository: TaskRepo,
) -> Task:
    """Создать задачу"""
    return TaskService().create(task, repository)


@router.put("/{task_id}", response_model=Task)
def modify_task(
    task_id: int,
    task: TaskInDB,
    repository: TaskRepo,
) -> Task:
    """Модифицировать задачу"""
    if task.id != task_id:
        raise HTTPException(400, "ID в path не совпадает с body")
    return TaskService().modify(task, repository)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    repository: TaskRepo,
) -> bool:
    """Удалить задачу"""
    return TaskService().delete(task_id, repository)


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    repository: TaskRepo,
) -> Task:
    """Получить задачу по ID"""
    task_orm = repository.get_by_id(task_id)
    if not task_orm:
        raise HTTPException(404, "Task not found")
    return Task.model_validate(task_orm)