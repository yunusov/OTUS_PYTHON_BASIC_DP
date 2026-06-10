from __future__ import annotations
from typing import TYPE_CHECKING, Any
from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseUserTable,
    SQLAlchemyUserDatabase as SQLAlchemyUserDatabaseGeneric,
)

from sqlalchemy import CheckConstraint, Text, func, select
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from .mixins import (
    DateCreateUpdateMixin,
    IntIdPkMixin,
)
from src.models import BaseOrm

if TYPE_CHECKING:
    from .access_token import AccessTokenOrm
    from .project import ProjectOrm
    from .task import TaskOrm
    from .user_project import UserProjectOrm
    from src.core.async_session_wrapper import AsyncSessionWrapper


class SQLAlchemyUserDatabase(SQLAlchemyUserDatabaseGeneric):

    def get_users(self) -> list["UserOrm"]:
        statement = select(UserOrm).order_by(UserOrm.id)
        results = self.session.scalars(statement)
        return list(results.all())

    async def create(self, create_dict: dict[str, Any]) -> Any:
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.commit()
        return user

    async def update(self, user: Any, update_dict: dict[str, Any]) -> Any:
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        return user


class UserOrm(
    BaseOrm,
    IntIdPkMixin,
    DateCreateUpdateMixin,
    SQLAlchemyBaseUserTable,
):

    __tablename__ = "tf_users"

    fullname: Mapped[str] = mapped_column(
        Text,
        default="",
        server_default="",
    )
    username: Mapped[str] = mapped_column(Text, unique=True)

    @classmethod
    def get_db(cls, session: "AsyncSessionWrapper"):
        return SQLAlchemyUserDatabase(session, cls)  # type: ignore[arg-type]

    def __str__(self) -> str:
        return self.email

    access_tokens: Mapped[list["AccessTokenOrm"]] = relationship(
        back_populates="user",
    )
    created_tasks: Mapped[list["TaskOrm"]] = relationship(
        "TaskOrm",
        foreign_keys="TaskOrm.creator_id",  # ← явно указываем creator_id
        back_populates="creator",
    )
    project: Mapped[list["ProjectOrm"]] = relationship(back_populates="creator")
    user_projects: Mapped[list["UserProjectOrm"]] = relationship(
        "UserProjectOrm",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    comments: Mapped[list["CommentOrm"]] = relationship(
        "CommentOrm",
        foreign_keys="CommentOrm.creator_id",
        back_populates="creator",
    )

    @declared_attr
    def __table_args__(cls):
        return (
            CheckConstraint(
                func.length(cls.username) <= 32,
                name="username_max_length",
            ),
            CheckConstraint(
                func.length(cls.fullname) <= 100,
                name="full_name_max_length",
            ),
            CheckConstraint(
                func.length(cls.email) <= 320,
                name="email_max_length",
            ),
        )
