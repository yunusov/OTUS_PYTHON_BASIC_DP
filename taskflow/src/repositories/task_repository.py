from sqlalchemy import select
from typing import List
from src.models import TaskOrm
from src.utils.loguru_config import AppLogger
from .base import BaseRepository


logger = AppLogger().get_logger()


class TaskRepository(BaseRepository):
    model = TaskOrm

    def get_by_project(self, project_id: int) -> List[TaskOrm]:
        """Задачи проекта"""
        result = self.session.execute(
            select(self.model).where(self.model.project_id == project_id)
        )
        return result.scalars().all()

    def get_by_assignee(self, assignee_id: int) -> List[TaskOrm]:
        """Задачи исполнителя"""
        result = self.session.execute(
            select(self.model).where(self.model.assignee_id == assignee_id)
        )
        return result.scalars().all()

    def get_by_id(self, id_: int) -> TaskOrm | None:
        """Получить задачу по ID"""
        result = self.session.execute(
            select(self.model).where(self.model.id == id_)
        )
        return result.scalar_one_or_none()