from datetime import datetime
from typing import Optional
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    func,
    Index,
    Text,
    DateTime,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from taskflow.src.core.database import BaseOrm
from taskflow.src.models.user import UserOrm
from taskflow.src.models.task import TaskOrm
from enum import StrEnum


class ProjectType(StrEnum):
    SOFTWARE = "software"
    BUSINESS = "business"
    SERVICE_DESK = "service_desk"


class ProjectOrm(BaseOrm):
    __tablename__ = "tf_projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, server_default="", nullable=False)


    description: Mapped[Optional[str]] = mapped_column(
        Text,
        default="",
        server_default="",
        nullable=True
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    creator_id: Mapped[int] = mapped_column(
        ForeignKey("tf_users.id"),
        nullable=False,
        index=False,
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
        index=False,
    )

    creator: Mapped["UserOrm"] = relationship("UserOrm")
    task: Mapped[list["TaskOrm"]] = relationship(back_populates="project")

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