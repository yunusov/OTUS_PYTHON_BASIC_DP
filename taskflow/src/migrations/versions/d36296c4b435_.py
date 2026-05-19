"""empty message

Revision ID: d36296c4b435
Revises: b71e0970ab9f
Create Date: 2026-05-19 13:45:45.768841
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "d36296c4b435"
down_revision: Union[str, Sequence[str], None] = "b71e0970ab9f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tf_accesstoken",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=43), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["tf_users.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("token"),
    )
    op.create_index(
        op.f("ix_tf_accesstoken_created_at"),
        "tf_accesstoken",
        ["created_at"],
        unique=False,
    )
    op.drop_index(op.f("ix_tf_user_project_project_id"), table_name="tf_user_project")
    op.drop_index(op.f("ix_tf_user_project_role"), table_name="tf_user_project")
    op.drop_index(op.f("ix_tf_user_project_user_id"), table_name="tf_user_project")
    op.drop_constraint(
        op.f("tf_user_project_user_id_project_id_key"),
        "tf_user_project",
        type_="unique",
    )
    op.drop_column("tf_user_project", "role")
    op.add_column(
        "tf_users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.add_column(
        "tf_users",
        sa.Column(
            "is_superuser",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "tf_users",
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.alter_column(
        "tf_users",
        "email",
        existing_type=sa.TEXT(),
        type_=sa.String(length=320),
        existing_nullable=False,
    )
    op.alter_column(
        "tf_users",
        "hashed_password",
        existing_type=sa.TEXT(),
        type_=sa.String(length=1024),
        existing_nullable=False,
    )
    op.drop_constraint(op.f("tf_users_email_key"), "tf_users", type_="unique")
    op.create_index(op.f("ix_tf_users_email"), "tf_users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_tf_users_email"), table_name="tf_users")
    op.create_unique_constraint(
        op.f("tf_users_email_key"),
        "tf_users",
        ["email"],
        postgresql_nulls_not_distinct=False,
    )
    op.alter_column(
        "tf_users",
        "hashed_password",
        existing_type=sa.String(length=1024),
        type_=sa.TEXT(),
        existing_nullable=False,
    )
    op.alter_column(
        "tf_users",
        "email",
        existing_type=sa.String(length=320),
        type_=sa.TEXT(),
        existing_nullable=False,
    )
    op.drop_column("tf_users", "is_verified")
    op.drop_column("tf_users", "is_superuser")
    op.drop_column("tf_users", "updated_at")
    op.add_column(
        "tf_user_project",
        sa.Column(
            "role",
            postgresql.ENUM("owner", "member", name="project_role_enum"),
            server_default=sa.text("'member'::project_role_enum"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.create_unique_constraint(
        op.f("tf_user_project_user_id_project_id_key"),
        "tf_user_project",
        ["user_id", "project_id"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_index(
        op.f("ix_tf_user_project_user_id"),
        "tf_user_project",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tf_user_project_role"),
        "tf_user_project",
        ["role"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tf_user_project_project_id"),
        "tf_user_project",
        ["project_id"],
        unique=False,
    )
    op.drop_index(op.f("ix_tf_accesstoken_created_at"), table_name="tf_accesstoken")
    op.drop_table("tf_accesstoken")
