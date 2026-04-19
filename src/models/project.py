from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    func,
    Index,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import BaseOrm, created_at, updated_at
from .user import UserOrm

from enum import StrEnum
from sqlalchemy import Enum as SQLEnum


class ProjectType(StrEnum):
    SOFTWARE = "software"
    BUSINESS = "business"
    SERVICE_DESK = "service_desk"


class ProjectOrm(BaseOrm):
    __tablename__ = "tf_projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, server_default="", nullable=False)
    description: Mapped[str] = mapped_column(
        Text, default="", server_default="", nullable=False
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    creator_id: Mapped[int] = mapped_column(
        ForeignKey("tf_users.id"),
        nullable=False,
        index=True,
    )

    project_type: Mapped[ProjectType] = mapped_column(
        SQLEnum(
            ProjectType,
            name="project_type_enum",
            values_callable=lambda x: [e.value for e in x],
            inherit_schema=True,
        ),
        default=ProjectType.SOFTWARE,
        nullable=False,
    )

    creator: Mapped["UserOrm"] = relationship("UserOrm")

    __table_args__ = (
        Index("ix_tf_projects_creator_id", "creator_id"),
        Index("ix_tf_projects_project_type", "project_type"),
        CheckConstraint(
            func.length(name) <= 100,
            name="project_name_max_length",
        ),
        CheckConstraint(
            func.length(description) <= 1000,
            name="project_description_max_length",
        ),
    )
