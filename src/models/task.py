from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    func,
    Index,
    Text,
    String,
    DateTime,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import BaseOrm, created_at, updated_at
from .user import UserOrm
from .project import ProjectOrm

from enum import StrEnum
from sqlalchemy import Enum as SQLEnum


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

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        Text,
        server_default="",
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tf_projects.id"),
        index=True,
        nullable=True,
    )
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(
            TaskStatus,
            name="task_status_enum",
            values_callable=lambda x: [e.value for e in x],
            inherit_schema=True,
        ),
        default=TaskStatus.TODO,
        nullable=False,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(
            TaskPriority,
            name="task_priority_enum",
            values_callable=lambda x: [e.value for e in x],
            inherit_schema=True,
        ),
        default=TaskPriority.MEDIUM,
        nullable=False,
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("tf_users.id"),
        index=True,
        nullable=False,
    )
    assignee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tf_users.id"),
        index=True,
        nullable=True,
    )
    time_estimate: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # в часах
    time_spent: Mapped[Optional[int]] = mapped_column(
        Integer, default=0, nullable=True
    )

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    project: Mapped[Optional["ProjectOrm"]] = relationship(
        "ProjectOrm", back_populates="tasks"
    )
    creator: Mapped["UserOrm"] = relationship(
        "UserOrm", foreign_keys=[creator_id]
    )
    assignee: Mapped[Optional["UserOrm"]] = relationship(
        "UserOrm", foreign_keys=[assignee_id]
    )

    __table_args__ = (
        Index("ix_tf_tasks_project_id", "project_id"),
        Index("ix_tf_tasks_status", "status"),
        Index("ix_tf_tasks_priority", "priority"),
        Index("ix_tf_tasks_assignee_id", "assignee_id"),
        CheckConstraint(
            func.length(name) <= 255,
            name="task_name_max_length",
        ),
    )