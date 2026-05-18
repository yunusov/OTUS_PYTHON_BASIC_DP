from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseOrm
from src.schemas import TaskPriority

from .mixins import (
    DateCreateUpdateMixin,
    IntIdPkMixin,
)

if TYPE_CHECKING:
    from .project import ProjectOrm
    from .user import UserOrm

class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

class TaskOrm(
    BaseOrm,
    IntIdPkMixin,
    DateCreateUpdateMixin,
):
    __tablename__ = "tf_tasks"

    # Основные поля
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tf_projects.id"), nullable=True, index=True
    )

    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(
            TaskStatus,
            name="task_status_enum",
            values_callable=lambda x: [e.value for e in x],
            inherit_schema=True,
        ),
        default=TaskStatus.TODO.value,
        nullable=False,
        index=True,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(
            TaskPriority,
            name="task_priority_enum",
            values_callable=lambda x: [e.value for e in x],
            inherit_schema=True,
        ),
        default=TaskPriority.MEDIUM.value,
        nullable=False,
        index=True,
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    creator_id: Mapped[int] = mapped_column(
        ForeignKey("tf_users.id"), nullable=False, index=True
    )
    assignee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tf_users.id"), nullable=True, index=True
    )

    time_estimate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    time_spent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    project: Mapped["ProjectOrm"] = relationship("ProjectOrm", back_populates="tasks")
    creator: Mapped["UserOrm"] = relationship(
        "UserOrm",
        foreign_keys=[creator_id],
        back_populates="created_tasks",
    )
    assignee: Mapped[Optional["UserOrm"]] = relationship(
        "UserOrm",
        foreign_keys=[assignee_id],
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint(
            "length(name) <= 255",
            name="task_name_max_length",
        ),

    )
