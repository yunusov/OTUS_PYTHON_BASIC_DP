from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseOrm

if TYPE_CHECKING:
    from .user import UserOrm
    from .project import ProjectOrm


class UserProjectOrm(BaseOrm):
    __tablename__ = "tf_user_project"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("tf_users.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("tf_projects.id"), nullable=False
    )

    user: Mapped["UserOrm"] = relationship(back_populates="user_projects")
    project: Mapped["ProjectOrm"] = relationship(back_populates="user_projects")

    def __repr__(self) -> str:
        return f"UserProjectOrm(id={self.id}, user_id={self.user_id}, project_id={self.project_id})"
