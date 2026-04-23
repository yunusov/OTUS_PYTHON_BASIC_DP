from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    func,
    Index,
    Text,
    DateTime,
    Integer,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from taskflow.src.core.database import BaseOrm
from taskflow.src.models.user import UserOrm

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

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        Text,
        server_default="",
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tf_projects.id"),
        index=False,
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
        index=False,
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
        index=False,
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("tf_users.id"),
        index=False,
        nullable=False,
    )
    assignee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tf_users.id"),
        index=False,
        nullable=True,
    )
    time_estimate: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # в часах
    time_spent: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )

    project: Mapped[Optional["ProjectOrm"]] = relationship(
        "ProjectOrm", back_populates="task"
    )
    creator: Mapped["UserOrm"] = relationship("UserOrm", foreign_keys=[creator_id])
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