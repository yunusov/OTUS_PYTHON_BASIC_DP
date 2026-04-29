from sqlalchemy import select

from src.models import TaskOrm
from src.utils.loguru_config import AppLogger
from .base import BaseRepository

logger = AppLogger().get_logger()


class TaskRepository(BaseRepository):

    def get_by_id(self, task_id: int) -> TaskOrm | None:
        '''Задача по ИД'''
        result = self.session.execute(
            select(TaskOrm).where(TaskOrm.id == task_id)
        )
        return result.scalar_one_or_none()

    def get_by_project_id(self, project_id: int) -> list[TaskOrm]:
        '''Задачи по проекту'''
        result = self.session.execute(
            select(TaskOrm).where(TaskOrm.project_id == project_id)
        )
        return result.scalars().all()

