from __future__ import annotations

from typing import TYPE_CHECKING

from typing import Any

from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseUserTable,
    SQLAlchemyUserDatabase as SQLAlchemyUserDatabaseGeneric,
)

from sqlalchemy import CheckConstraint, Text, func, select
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

if TYPE_CHECKING:
    # from src.core.types.user_id import UserIdType
    from .access_token import AccessTokenOrm
    from .project import ProjectOrm
    from src.core.async_session_wrapper import AsyncSessionWrapper

from src.core.security import hash_password
from src.schemas import UserCreate
from .base import BaseOrm
from .mixins import (
    DateCreateUpdateMixin,
    IntIdPkMixin,
)


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

    def __repr__(self) -> str:
        return "".join(
            [
                f"UserOrm(id={self.id},",
                f"username={self.username},",
                f"fullname={self.fullname},",
                f"email={self.email},",
                f"is_active={self.is_active},",
                f"is_superuser={self.is_superuser},",
                f"is_verified={self.is_verified},",
                f"created_at={self.created_at}",
                f"update_at={self.updated_at})",
            ]
        )

    access_tokens: Mapped[list["AccessTokenOrm"]] = relationship(
        back_populates="user",
    )
    created_tasks: Mapped[list["TaskOrm"]] = relationship(
        "TaskOrm",
        foreign_keys="TaskOrm.creator_id",  # ← явно указываем creator_id
        back_populates="creator",
    )
    project: Mapped[list["ProjectOrm"]] = relationship(back_populates="creator")
    projects: Mapped[list["ProjectOrm"]] = relationship(
        "ProjectOrm",
        secondary="tf_user_project",  # Alembic создаст tf_user_project
        back_populates="users",
        lazy="selectin",
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
