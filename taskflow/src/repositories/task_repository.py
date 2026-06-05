from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .base import BaseRepository
from src.models import TaskOrm
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


class TaskRepository(BaseRepository):
    model = TaskOrm

    def get_by_project(self, project_id: int) -> list[TaskOrm]:
        """Задачи проекта"""
        result = self.session.execute(
            select(self.model)
            .options(joinedload(self.model.assignee, innerjoin=True))
            .options(joinedload(self.model.creator, innerjoin=True))
            .where(self.model.project_id == project_id)
        )
        return list(result.scalars().all())

    def get_by_assignee(self, assignee_id: int) -> list[TaskOrm]:
        """Задачи исполнителя"""
        result = self.session.execute(
            select(self.model).where(self.model.assignee_id == assignee_id)
        )
        return list(result.scalars().all())

    def get_by_id(self, id: int) -> TaskOrm | None:
        """Получить задачу по ID"""
        result = self.session.execute(
            select(self.model).where(self.model.id == id),
        )
        return result.scalar_one_or_none()
