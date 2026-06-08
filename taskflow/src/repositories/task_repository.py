from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload

from src.models import TaskOrm
from src.utils.loguru_config import AppLogger
from .base import BaseRepository

logger = AppLogger().get_logger()


class TaskRepository(BaseRepository):

    def get_by_user(self, user_id: int) -> list[TaskOrm]:
        """Все задачи пользователя (как создатель или исполнитель)"""
        result = self.session.execute(
            select(TaskOrm)
            .options(joinedload(TaskOrm.assignee, innerjoin=True))
            .options(joinedload(TaskOrm.creator, innerjoin=True))
            .where(or_(TaskOrm.creator_id == user_id, TaskOrm.assignee_id == user_id))
        )
        return list(result.scalars().all())

    def get_by_project(self, project_id: int) -> list[TaskOrm]:
        """Задачи проекта"""
        result = self.session.execute(
            select(TaskOrm)
            .options(joinedload(TaskOrm.assignee, innerjoin=True))
            .options(joinedload(TaskOrm.creator, innerjoin=True))
            .where(TaskOrm.project_id == project_id)
        )
        return list(result.scalars().all())

    def get_by_assignee(self, assignee_id: int) -> list[TaskOrm]:
        """Задачи исполнителя"""
        result = self.session.execute(
            select(TaskOrm).where(TaskOrm.assignee_id == assignee_id)
        )
        return list(result.scalars().all())

    def get_by_id(self, id: int) -> TaskOrm | None:
        """Получить задачу по ID"""
        result = self.session.execute(
            select(TaskOrm)
            .options(joinedload(TaskOrm.creator))
            .options(joinedload(TaskOrm.assignee))
            .where(TaskOrm.id == id),
        )
        return result.scalar_one_or_none()
