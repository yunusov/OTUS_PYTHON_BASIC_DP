from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    func,
    Text,
    DateTime,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from src.core.database import BaseOrm
from src.models.user import UserOrm

from enum import StrEnum


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskOrm(BaseOrm):
    __tablename__ = "tf_tasks"

    name: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tf_projects.id"), nullable=True, index=True
    )
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name="task_status_enum", inherit_schema=True),
        default=TaskStatus.TODO, nullable=False, index=True
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(TaskPriority, name="task_priority_enum", inherit_schema=True),
        default=TaskPriority.MEDIUM, nullable=False, index=True
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("tf_users.id"), nullable=False, index=True
    )
    assignee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tf_users.id"), nullable=True, index=True
    )
    time_estimate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    time_spent: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)

    # Правильные relationships
    project: Mapped[Optional["ProjectOrm"]] = relationship(back_populates="tasks")
    creator: Mapped["UserOrm"] = relationship(foreign_keys=[creator_id])
    assignee: Mapped[Optional["UserOrm"]] = relationship(foreign_keys=[assignee_id])

    __table_args__ = (
        CheckConstraint(func.length("name") <= 255, name="task_name_max_length"),
    )