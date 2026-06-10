"""add tf_comments table

Revision ID: 2c6365d2e959
Revises: 3ffa77f1a6ee
Create Date: 2026-06-10 07:47:43.662527

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "2c6365d2e959"
down_revision: Union[str, Sequence[str], None] = "3ffa77f1a6ee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создать таблицу tf_comments"""
    op.create_table(
        "tf_comments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "task_id", sa.Integer(), sa.ForeignKey("tf_tasks.id"), nullable=False
        ),
        sa.Column(
            "creator_id", sa.Integer(), sa.ForeignKey("tf_users.id"), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.current_timestamp(),
            onupdate=sa.func.current_timestamp(),
        ),
        sa.CheckConstraint(
            sa.func.length("content") <= 1000, name="comment_content_max_length"
        ),
    )

    op.create_index("idx_comments_task_id", "tf_comments", ["task_id"])
    op.create_index("idx_comments_creator_id", "tf_comments", ["creator_id"])


def downgrade() -> None:
    """Удалить таблицу tf_comments"""
    op.drop_index("idx_comments_creator_id", "tf_comments")
    op.drop_index("idx_comments_task_id", "tf_comments")
    op.drop_table("tf_comments")
