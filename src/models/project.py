from sqlalchemy import CheckConstraint, ForeignKey, func, Index, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import BaseOrm, created_at
from .user import UserOrm
from datetime import datetime

class ProjectOrm(BaseOrm):
    __tablename__ = "tf_projects"

    name: Mapped[str] = mapped_column(
        Text,
        server_default="",
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text,
        default="",
        server_default="",
        nullable=False
    )
    created_at: Mapped[created_at]


    creator_id: Mapped[int] = mapped_column(
        ForeignKey('tf_users.id'),  # замените 'tf_users' на вашу таблицу пользователей
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        index=True
    )
    project_type: Mapped[str] = mapped_column(
        String(50),
        default='software',
        nullable=False
    )


    creator: Mapped["UserOrm"] = relationship("UserOrm")

    __table_args__ = (
        Index('ix_tf_projects_creator_id', 'creator_id'),
        Index('ix_tf_projects_project_type', 'project_type'),
        CheckConstraint(
            func.length(name) <= 100,
            name="project_name_max_length",
        ),
        CheckConstraint(
            func.length(description) <= 1000,
            name="project_description_max_length",
        ),
        CheckConstraint(
            project_type.in_(['software', 'business', 'service_desk']),
            name="valid_project_type",
        ),
    )