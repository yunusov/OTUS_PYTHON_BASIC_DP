"""Fixes

Revision ID: 40c91e15b21e
Revises: 531d13d60870
Create Date: 2026-05-17 23:19:52.732468

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "40c91e15b21e"
down_revision: Union[str, Sequence[str], None] = "531d13d60870"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = inspect(conn)

    # === tf_tasks.created_at ===
    columns = [col["name"] for col in inspector.get_columns("tf_tasks")]

    if "created_at" not in columns:
        op.add_column(
            "tf_tasks",
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
        )
        print("✅ Column 'created_at' added to tf_tasks")
    else:
        # Проверяем, есть ли DEFAULT
        col_info = next(
            (c for c in inspector.get_columns("tf_tasks") if c["name"] == "created_at"),
            None,
        )
        if col_info and col_info.get("default") is None:
            op.execute(
                "ALTER TABLE tf_tasks ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;"
            )
            print("✅ DEFAULT added to created_at in tf_tasks")
        else:
            print("⏭️ Column 'created_at' already exists with DEFAULT, skipping...")

    # === tf_tasks.updated_at ===
    if "updated_at" not in columns:
        op.add_column(
            "tf_tasks",
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
        )
        print("✅ Column 'updated_at' added to tf_tasks")
    else:
        col_info = next(
            (c for c in inspector.get_columns("tf_tasks") if c["name"] == "updated_at"),
            None,
        )
        if col_info and col_info.get("default") is None:
            op.execute(
                "ALTER TABLE tf_tasks ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;"
            )
            print("✅ DEFAULT added to updated_at in tf_tasks")
        else:
            print("⏭️ Column 'updated_at' already exists with DEFAULT, skipping...")

    # === tf_projects.updated_at ===
    project_columns = [col["name"] for col in inspector.get_columns("tf_projects")]

    if "updated_at" not in project_columns:
        op.add_column(
            "tf_projects",
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
        )
        print("✅ Column 'updated_at' added to tf_projects")
    else:
        col_info = next(
            (
                c
                for c in inspector.get_columns("tf_projects")
                if c["name"] == "updated_at"
            ),
            None,
        )
        if col_info and col_info.get("default") is None:
            op.execute(
                "ALTER TABLE tf_projects ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;"
            )
            print("✅ DEFAULT added to updated_at in tf_projects")
        else:
            print("⏭️ Column 'updated_at' already exists with DEFAULT, skipping...")

    # === tf_tasks.created_at (для tf_tasks уже обработано выше) ===
    # tf_projects.created_at тоже должен быть
    if "created_at" not in project_columns:
        op.add_column(
            "tf_projects",
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
        )
        print("✅ Column 'created_at' added to tf_projects")
    else:
        col_info = next(
            (
                c
                for c in inspector.get_columns("tf_projects")
                if c["name"] == "created_at"
            ),
            None,
        )
        if col_info and col_info.get("default") is None:
            op.execute(
                "ALTER TABLE tf_projects ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;"
            )
            print("✅ DEFAULT added to created_at in tf_projects")
        else:
            print("⏭️ Column 'created_at' already exists with DEFAULT, skipping...")

    # Создаем индекс
    op.create_index(
        op.f("ix_tf_tasks_creator_id"),
        "tf_tasks",
        ["creator_id"],
        unique=False,
        if_not_exists=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_tf_tasks_creator_id"), table_name="tf_tasks")
    op.drop_column("tf_tasks", "created_at")
    op.drop_column("tf_tasks", "updated_at")
    op.drop_column("tf_projects", "created_at")
    op.drop_column("tf_projects", "updated_at")
