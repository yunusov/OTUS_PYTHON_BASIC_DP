from sqlalchemy import exists, or_, select
from sqlalchemy.orm import joinedload, selectinload


from .base import BaseRepository
from src.models import ProjectOrm, UserProjectOrm
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

    def get_by_creator_id(self, creator_id: int | None) -> list[ProjectOrm]:
        """Проекты создателя"""
        query = (
            select(ProjectOrm)
            .options(joinedload(ProjectOrm.creator, innerjoin=True))
            .options(selectinload(ProjectOrm.user_projects))
        )
        if creator_id:
            query = query.filter(
                or_(
                    ProjectOrm.creator_id == creator_id,
                    ProjectOrm.user_projects.any(UserProjectOrm.user_id == creator_id),
                )
            )
        result = self.session.execute(query)
        projects = result.scalars().all()
        return list(projects)

    def get_by_name(self, name: str) -> ProjectOrm | None:
        """Проект по названию"""
        result = self.session.execute(
            select(ProjectOrm).where(ProjectOrm.name == name),
        )
        return result.scalar_one_or_none()

    def remove_members(self, project_id: int, user_ids: set[int]) -> int:
        """Удалить участников проекта."""
        from src.models import UserProjectOrm

        result = (
            self.session.query(UserProjectOrm)
            .filter(
                UserProjectOrm.project_id == project_id,
                UserProjectOrm.user_id.in_(user_ids),
            )
            .delete(synchronize_session="fetch")
        )
        return result
