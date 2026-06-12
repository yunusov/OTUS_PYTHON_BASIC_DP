from sqlalchemy import and_, exists, or_, select, text, true
from sqlalchemy.orm import joinedload

from src.models import UserOrm, CommentOrm, TaskOrm
from src.utils.loguru_config import AppLogger
from .base import BaseRepository

logger = AppLogger().get_logger()


class UserRepository(BaseRepository):

    def get_by_id(self, user_id: int) -> UserOrm | None:
        """Пользователь по ИД"""
        result = self.session.execute(
            select(UserOrm).where(UserOrm.id == user_id),
        )
        return result.scalar_one_or_none()

    def get_by_email(self, email: str) -> UserOrm | None:
        """Пользователь по емейл"""
        result = self.session.execute(
            select(UserOrm).where(UserOrm.email == email),
        )
        return result.scalar_one_or_none()

    def get_by_username(self, username: str) -> UserOrm | None:
        """Пользователь по логину"""
        result = self.session.execute(
            select(UserOrm).where(UserOrm.username == username),
        )
        return result.scalar_one_or_none()

    def get_all(self) -> list[UserOrm]:
        """Получить всех пользователей"""
        result = self.session.execute(select(UserOrm))
        return list(result.scalars().all())

    def get_all_verified(self) -> list[UserOrm]:
        result = self.session.execute(
            select(UserOrm).where(UserOrm.is_verified == true())
        )
        return list(result.scalars().unique().all())

    def get_all_verified_by_project(self, project_id: int) -> list:
        result = self.session.execute(
            text("""
                select fullname,
                    id,
                    project_id assigned_project
                from
                (select
                    tu.fullname,
                    tu.id,
                    tup.project_id
                from
                    tf_users tu
                left join tf_user_project tup on
                    tu.id = tup.user_id
                where tu.is_verified = True and
                    tup.project_id = :project_id
                union
                select
                    tu.fullname,
                    tu.id,
                    max(tup.project_id) project_id
                from
                    tf_users tu
                left join tf_user_project tup on
                    tu.id = tup.user_id
                where tu.is_verified = True and
                    (tup.project_id != :project_id or tup.project_id is null)
                    and not exists(
                            select 1
                              from tf_user_project p
                            where tu.id = p.user_id
                 and p.project_id = :project_id)
                group by tu.fullname, tu.id)
                order by fullname"""),
            {"project_id": project_id},
        )
        return list(result.mappings().unique().all())

    def get_users_by_project(self, project_id) -> list[UserOrm]:
        result = self.session.execute(
            select(UserOrm)
            .options(joinedload(UserOrm.user_projects))
            .where(
                and_(
                    UserOrm.is_verified == true(),
                    UserOrm.user_projects.any(project_id=project_id),
                )
            )
        )
        return list(result.scalars().unique().all())

    def get_users_for_comment_email(
        self, comment_id: int, user_id: int
    ) -> list[UserOrm]:
        """Получить пользователей для отправки email"""
        q1 = select(CommentOrm.creator_id).where(CommentOrm.id == comment_id)
        task_subq = select(CommentOrm.task_id).where(CommentOrm.id == comment_id).scalar_subquery()
        q2 = select(CommentOrm.creator_id).where(CommentOrm.task_id == task_subq)
        q3 = select(TaskOrm.assignee_id).where(TaskOrm.id == task_subq)
        union_subq = q1.union_all(q2, q3).subquery()
        
        # Основной запрос
        result = self.session.execute(
            select(UserOrm)
            .where(
                and_(
                    UserOrm.id.in_(select(union_subq.c.creator_id)),
                    UserOrm.id != user_id,
                )
            )
        )
        return list(result.scalars().unique().all())
