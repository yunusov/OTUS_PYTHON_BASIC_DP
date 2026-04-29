from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    func,
    Text,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from src.core.database import BaseOrm
from src.models.user import UserOrm

from enum import StrEnum


class ProjectType(StrEnum):
    SOFTWARE = "software"
    BUSINESS = "business"
    SERVICE_DESK = "service_desk"


class ProjectOrm(BaseOrm):
    __tablename__ = "tf_projects"

    name: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    creator_id: Mapped[int] = mapped_column(
        ForeignKey("tf_users.id"), nullable=False, index=True
    )
    project_type: Mapped[ProjectType] = mapped_column(
        SQLEnum(ProjectType, name="project_type_enum", inherit_schema=True),
        default=ProjectType.SOFTWARE, nullable=False, index=True
    )

    creator: Mapped["UserOrm"] = relationship("UserOrm")
    tasks: Mapped[list["TaskOrm"]] = relationship(back_populates="project")

    __table_args__ = (
        CheckConstraint(func.length("name") <= 100, name="project_name_max_length"),
        CheckConstraint(func.length("description") <= 1000, name="project_description_max_length"),
    )