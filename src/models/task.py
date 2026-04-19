from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, func, Index, Text, String, DateTime, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import BaseOrm
from .user import UserOrm
from .project import ProjectOrm


class TaskOrm(BaseOrm):
    __tablename__ = "tf_tasks"

    name: Mapped[str] = mapped_column(
        Text,
        server_default="",
        nullable=False,
    )


    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tf_projects.id"),
        index=True,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="todo",
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(50),
        default="medium",
        nullable=False
    )

    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    creator_id: Mapped[int] = mapped_column(
        ForeignKey("tf_users.id"),
        index=True,
        nullable=False
    )

    assignee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tf_users.id"),
        index=True,
        nullable=True
    )


    time_estimate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # в часах
    time_spent: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), index=True
    )


    project: Mapped["ProjectOrm"] = relationship("ProjectOrm", back_populates="tasks")
    creator: Mapped["UserOrm"] = relationship("UserOrm", foreign_keys=[creator_id])
    assignee: Mapped[Optional["UserOrm"]] = relationship("UserOrm", foreign_keys=[assignee_id])

    __table_args__ = (
        Index('ix_tf_tasks_project_id', 'project_id'),
        Index('ix_tf_tasks_status', 'status'),
        Index('ix_tf_tasks_priority', 'priority'),
        Index('ix_tf_tasks_assignee_id', 'assignee_id'),
        CheckConstraint(
            func.length(name) <= 255,
            name="task_name_max_length",
        ),
        CheckConstraint(
            status.in_(['todo', 'in_progress', 'review', 'done']),
            name="valid_task_status",
        ),
        CheckConstraint(
            priority.in_(['low', 'medium', 'high', 'critical']),
            name="valid_task_priority",
        ),
    )