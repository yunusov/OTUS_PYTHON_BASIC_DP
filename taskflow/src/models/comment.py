from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    func,
    Text,
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

from src.models import BaseOrm


class CommentOrm(
    BaseOrm,
    IntIdPkMixin,
    DateCreateUpdateMixin,
):
    __tablename__ = "tf_comments"

    content: Mapped[str] = mapped_column(Text, nullable=False)

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tf_tasks.id"), nullable=False, index=True
    )
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("tf_users.id"), nullable=False, index=True
    )

    # ← ОДИН раз relationship, с foreign_keys:
    task: Mapped["TaskOrm"] = relationship(
        "TaskOrm",
        foreign_keys=[task_id],
        back_populates="comments",
    )

    creator: Mapped["UserOrm"] = relationship(
        "UserOrm",
        foreign_keys=[creator_id],
        back_populates="comments",
    )

    # проверки на длину
    __table_args__ = (
        CheckConstraint(
            func.length("content") <= 1000,
            name="comment_content_max_length",
        ),
    )

    def __str__(self) -> str:
        return self.content[:50] + "..." if len(self.content) > 50 else self.content
