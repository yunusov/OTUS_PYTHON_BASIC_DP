from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    func,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from .mixins import (
    DateCreateUpdateMixin,
    IntIdPkMixin,
)

if TYPE_CHECKING:
    from .task import TaskOrm
    from .user import UserOrm

from src.models import (
    BaseOrm,
    UserOrm,
)
from src.schemas import ProjectType


class ProjectOrm(
    BaseOrm,
    IntIdPkMixin,
    DateCreateUpdateMixin,
):
    __tablename__ = "tf_projects"

    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
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
    users: Mapped[list["UserOrm"]] = relationship(
        "UserOrm",
        secondary="tf_user_project",
        back_populates="projects",
        lazy="selectin",
    )

    # проверки на длину
    __table_args__ = (
        CheckConstraint(
            func.length("name") <= 100,
            name="project_name_max_length",
        ),
        CheckConstraint(
            func.length("description") <= 1000, name="project_description_max_length"
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
