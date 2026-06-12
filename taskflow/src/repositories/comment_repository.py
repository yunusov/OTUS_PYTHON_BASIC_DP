from sqlalchemy import select
from sqlalchemy.orm import joinedload


from .base import BaseRepository
from src.models import CommentOrm
from src.schemas.comment import CommentCreate
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


class CommentRepository(BaseRepository):

    def get_by_id(self, id: int) -> CommentOrm | None:
        """Комментарий по ИД"""
        result = self.session.execute(
            select(CommentOrm)
            .options(joinedload(CommentOrm.creator, innerjoin=True))
            .options(joinedload(CommentOrm.task, innerjoin=True))
            .where(CommentOrm.id == id)
        )
        comment = result.scalar_one_or_none()
        return comment

    def get_by_task_id(self, task_id: int) -> list[CommentOrm]:
        """Комментарии задачи"""
        result = self.session.execute(
            select(CommentOrm)
            .options(joinedload(CommentOrm.creator, innerjoin=True))
            .where(CommentOrm.task_id == task_id)
        )
        comments = result.scalars().all()
        return list(comments)

    def get_by_creator_id(self, creator_id: int) -> list[CommentOrm]:
        """Комментарии создателя"""
        result = self.session.execute(
            select(CommentOrm)
            .options(joinedload(CommentOrm.creator, innerjoin=True))
            .where(CommentOrm.creator_id == creator_id)
        )
        comments = result.scalars().all()
        return list(comments)

    def add_comment(self, comment: CommentCreate):
        """Добавление комментария"""
        self.create(**comment.model_dump())
