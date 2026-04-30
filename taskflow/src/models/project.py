from enum import StrEnum
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    func,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from src.core.database import BaseOrm, created_at
from src.models.user import UserOrm
from src.schemas.project import ProjectInDB, ProjectType


class ProjectOrm(BaseOrm):
    __tablename__ = "tf_projects"

    def __init__(self, project: ProjectInDB):
        super().__init__(
            name=project.name,
            description=project.description,
            creator_id=project.creator_id,

        )

    # обязательные поля
    name: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    creator_id: Mapped[int] = mapped_column(
        ForeignKey("tf_users.id"), nullable=False, index=True
    )
    project_type: Mapped[ProjectType] = mapped_column(
        SQLEnum(
            ProjectType,
            name="project_type_enum",
            values_callable=lambda x: [e.value for e in x],
            inherit_schema=True,
        ),
        default=ProjectType.SOFTWARE.value,
        nullable=False,
        index=True,
    )

    # связи
    creator: Mapped["UserOrm"] = relationship("UserOrm", back_populates="project")
    tasks: Mapped[list["TaskOrm"]] = relationship(back_populates="project")

    # id и created_at — как у User
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[created_at]

    # проверки на длину
    __table_args__ = (
        CheckConstraint(
            func.length("name") <= 100,
            name="project_name_max_length",
        ),
        CheckConstraint(
            func.length("description") <= 1000,
            name="project_description_max_length",
        ),
    )

    def __repr__(self) -> str:
        return "".join(
            [
                f"ProjectOrm(id={self.id},",
                f"name={self.name},",
                f"description={self.description},",
                f"project_type={self.project_type},",
                f"creator_id={self.creator_id},",
                f"created_at={self.created_at})",
            ]
        )
