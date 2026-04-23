from sqlalchemy import select
from sqlalchemy.orm import Session

from .base import BaseRepository
from src.models import ProjectOrm
from src.utils.loguru_config import AppLogger
from .base import BaseRepository
from taskflow.src.models.project import ProjectOrm
from taskflow.src.schemas.project import Project, ProjectUpdate

logger = AppLogger().get_logger()

class ProjectRepository:
    def __init__(self, session: Session):
        self.session = session

class ProjectRepository(BaseRepository):

    def get_by_id(self, project_id: int) -> ProjectOrm | None:
        '''Проект по ИД'''
        result = self.session.execute(
            select(ProjectOrm).where(ProjectOrm.id == project_id)
        )
        return result.scalar_one_or_none()

    def get_by_creator_id(self, creator_id: int) -> list[ProjectOrm]:
        '''Проекты создателя'''
        result = self.session.execute(
            select(ProjectOrm).where(ProjectOrm.creator_id == creator_id)
        )
        return result.scalars().all()

    def get_by_name(self, name: str) -> ProjectOrm | None:
        '''Проект по названию'''
        result = self.session.execute(
            select(ProjectOrm).where(ProjectOrm.name == name)
        )
        return result.scalar_one_or_none()