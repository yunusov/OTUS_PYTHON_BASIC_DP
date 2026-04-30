from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from src.core.database import BaseOrm
from src.models.project import ProjectOrm
from src.models.user import UserOrm
from src.schemas.task import Task, TaskStatus, TaskPriority

from datetime import datetime
from typing import Optional


class TaskOrm(BaseOrm):
    __tablename__ = "tf_tasks"

    def __init__(self, task: Task):
        super().__init__(
            name=task.name,
            description=task.description,
            project_id=task.project_id,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            creator_id=task.creator_id,
            assignee_id=task.assignee_id,
            time_estimate=task.time_estimate,
            time_spent=task.time_spent,
        )

    # Основные поля
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tf_projects.id"), nullable=True, index=True
    )

    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name="task_status_enum", inherit_schema=True),
        nullable=False,
        index=True,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(TaskPriority, name="task_priority_enum", inherit_schema=True),
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

    # Технические поля
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    # Relationships
    project: Mapped["ProjectOrm"] = relationship(back_populates="tasks")
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