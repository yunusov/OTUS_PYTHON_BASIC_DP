from fastapi import APIRouter, Depends, HTTPException

from src.core.auth.fastapi_users import fastapi_users
from src.core.config import settings
from src.core.dependencies import CommentRepo, TaskRepo, UserRepo
from src.core.auth.user_manager import UserManager
from src.models.user import UserOrm
from src.routers.api.dependencies.auth.user_manager import get_user_manager
from src.schemas import (
    CommentCreate,
    CommentRead,
    CommentUpdate,
)
from src.services import CommentService
from src.utils.loguru_config import AppLogger

# Получить текущего активного пользователя (любого авторизованного)
current_active_user = fastapi_users.current_user(active=True)

# Получить текущего суперпользователя
current_superuser = fastapi_users.current_user(active=True, superuser=True)

logger = AppLogger().get_logger()
router = APIRouter(prefix=settings.api.v1.comments, tags=["Comments"])


@router.post("/", response_model=CommentRead)
async def create_comment(
    comment: CommentCreate,
    repository: CommentRepo,
    tr: TaskRepo,
    ur: UserRepo,
    user: UserOrm = Depends(current_active_user),  # ← только авторизированный
    user_manager: UserManager = Depends(get_user_manager),
) -> CommentRead:
    """Создать комментарий"""
    return await CommentService().create(comment, repository, user_manager, tr, ur)


@router.put("/{comment_id}", response_model=CommentRead)
def modify_comment(
    comment_id: int,
    comment: CommentUpdate,
    repository: CommentRepo,
    user: UserOrm = Depends(current_active_user),  # ← только авторизированный
) -> CommentRead:
    """Модифицировать комментарий"""
    return CommentService().modify(comment_id, comment, repository)


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    repository: CommentRepo,
    user: UserOrm = Depends(current_active_user),  # ← только авторизированный
) -> bool:
    """Удалить комментарий"""
    return CommentService().delete(comment_id, repository)


@router.get("/{comment_id}", response_model=CommentRead)
def get_comment(
    comment_id: int,
    repository: CommentRepo,
    user: UserOrm = Depends(current_active_user),  # ← только авторизированный
) -> CommentRead:
    """Получить комментарий по ID"""
    comment_orm = repository.get_by_id(comment_id)
    if not comment_orm:
        raise HTTPException(404, "Комментарий не найден")
    return CommentRead.model_validate(comment_orm)


@router.get("/task/{task_id}", response_model=list[CommentRead])
def get_task_comments(
    task_id: int,
    repository: CommentRepo,
    user: UserOrm = Depends(current_active_user),  # ← только авторизированный
) -> list[CommentRead]:
    """Получить все комментарии задачи"""
    comments = repository.get_by_task_id(task_id)
    return [CommentRead.model_validate(comment) for comment in comments]
