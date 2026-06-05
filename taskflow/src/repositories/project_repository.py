from sqlalchemy import select
from sqlalchemy.orm import joinedload


from .base import BaseRepository
from src.models import ProjectOrm, UserOrm
from src.schemas.project import ProjectRead
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


class ProjectRepository(BaseRepository):

    def get_by_id(self, id: int) -> ProjectOrm | None:
        """Проект по ИД"""
        result = self.session.execute(
            select(ProjectOrm)
            .options(joinedload(ProjectOrm.creator, innerjoin=True))
            .where(ProjectOrm.id == id)
        )
        project = result.scalar_one_or_none()
        return project

    def get_by_creator_id(self, creator_id: int) -> list[ProjectOrm]:
        """Проекты создателя"""
        result = self.session.execute(
            select(ProjectOrm)
            .options(joinedload(ProjectOrm.creator, innerjoin=True))
            .filter(ProjectOrm.creator_id == creator_id)
        )
        projects = result.scalars().all()
        return list(projects)

    def get_by_name(self, name: str) -> ProjectOrm | None:
        """Проект по названию"""
        result = self.session.execute(
            select(ProjectOrm).where(ProjectOrm.name == name),
        )
        return result.scalar_one_or_none()
