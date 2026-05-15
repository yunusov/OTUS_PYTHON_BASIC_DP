from fastapi import APIRouter, Depends, HTTPException

from src.core.auth.fastapi_users import fastapi_users
from src.core.config import settings
from src.core.dependencies import TaskRepo
from src.models.user import UserOrm
from src.schemas import TaskRead, TaskCreate, TaskUpdate
from src.services import TaskService
from src.utils.loguru_config import AppLogger

# Получить текущего активного пользователя (любого авторизованного)
current_active_user = fastapi_users.current_user(active=True)

# Получить текущего суперпользователя
current_superuser = fastapi_users.current_user(active=True, superuser=True)

logger = AppLogger().get_logger()
router = APIRouter(prefix=settings.api.v1.tasks, tags=["Tasks"])


@router.post("/", response_model=TaskRead)
def create_task(
    task: TaskCreate,
    repository: TaskRepo,
    user: UserOrm = Depends(current_active_user),
) -> TaskRead:
    """Создать задачу"""
    return TaskService().create(task, repository)


@router.put("/{task_id}", response_model=TaskRead)
def modify_task(
    task_id: int,
    task: TaskUpdate,
    repository: TaskRepo,
    user: UserOrm = Depends(current_active_user),
) -> TaskRead:
    """Модифицировать задачу"""
    return TaskService().modify(task_id, task, repository)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    repository: TaskRepo,
    user: UserOrm = Depends(current_active_user),
) -> bool:
    """Удалить задачу"""
    return TaskService().delete(task_id, repository)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    repository: TaskRepo,
    user: UserOrm = Depends(current_active_user),
) -> TaskRead:
    """Получить задачу по ID"""
    task_orm = repository.get_by_id(task_id)
    if not task_orm:
        raise HTTPException(404, "Task not found")
    return TaskRead.model_validate(task_orm)
