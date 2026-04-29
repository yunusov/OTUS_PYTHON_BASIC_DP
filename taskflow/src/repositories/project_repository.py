from sqlalchemy import select

from src.models import ProjectOrm
from src.utils.loguru_config import AppLogger
from .base import BaseRepository

logger = AppLogger().get_logger()


class ProjectRepository(BaseRepository):

    def get_by_id(self, project_id: int) -> ProjectOrm | None:
        '''Проект по ИД'''
        result = self.session.execute(
            select(ProjectOrm).where(ProjectOrm.id == project_id)
        )
        return result.scalar_one_or_none()

    def get_by_user_id(self, user_id: int) -> list[ProjectOrm]:
        '''Проекты пользователя'''
        result = self.session.execute(
            select(ProjectOrm).where(ProjectOrm.user_id == user_id)
        )
        return result.scalars().all()
