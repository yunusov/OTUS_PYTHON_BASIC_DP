from typing import TYPE_CHECKING, Any

from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTable,
)
from sqlalchemy import (
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .base import BaseOrm

if TYPE_CHECKING:
    from src.core.async_session_wrapper import AsyncSessionWrapper
    from src.models import UserOrm


class SQLAlchemyAccessTokenDatabaseOverride(SQLAlchemyAccessTokenDatabase):

    async def create(self, create_dict: dict[str, Any]) -> Any:
        access_token = self.access_token_table(**create_dict)
        self.session.add(access_token)
        await self.session.commit()
        return access_token

    async def update(self, access_token: Any, update_dict: dict[str, Any]) -> Any:
        for key, value in update_dict.items():
            setattr(access_token, key, value)
        self.session.add(access_token)
        await self.session.commit()
        return access_token


class AccessTokenOrm(
    BaseOrm,
    SQLAlchemyBaseAccessTokenTable[int],
):
    __tablename__ = "tf_accesstoken"

    user_id: Mapped[int] = mapped_column(  # type: ignore[override]
        ForeignKey("tf_users.id", ondelete="cascade"),
        nullable=False,
    )

    user: Mapped["UserOrm"] = relationship(
        back_populates="access_tokens",
    )

    @classmethod
    def get_db(cls, session: "AsyncSessionWrapper"):
        return SQLAlchemyAccessTokenDatabaseOverride(session, cls) # type: ignore[arg-type]

    def __str__(self) -> str:
        return self.token
