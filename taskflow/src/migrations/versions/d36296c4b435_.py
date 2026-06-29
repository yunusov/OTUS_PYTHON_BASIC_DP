"""empty message

Revision ID: d36296c4b435
Revises: b71e0970ab9f
Create Date: 2026-05-19 13:45:45.768841
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy.generics
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

revision: str = "d36296c4b435"
down_revision: Union[str, Sequence[str], None] = "b71e0970ab9f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Создаём таблицу tf_accesstoken
    op.create_table(
        "tf_accesstoken",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=43), nullable=False),
        sa.Column(
            "created_at",
            fastapi_users_db_sqlalchemy.generics.TIMESTAMPAware(timezone=True),
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

    # 2. Удаляем индексы из tf_user_project (с проверкой!)
    conn = op.get_bind()
    inspector = inspect(conn)

    # Получаем список существующих индексов в таблице tf_user_project
    indexes = [idx["name"] for idx in inspector.get_indexes("tf_user_project")]

    # Удаляем индексы только если они существуют
    if "ix_tf_user_project_project_id" in indexes:
        op.drop_index(
            op.f("ix_tf_user_project_project_id"), table_name="tf_user_project"
        )
    else:
        print("⏭️ Index 'ix_tf_user_project_project_id' does not exist, skipping...")

    if "ix_tf_user_project_role" in indexes:
        op.drop_index(op.f("ix_tf_user_project_role"), table_name="tf_user_project")
    else:
        print("⏭️ Index 'ix_tf_user_project_role' does not exist, skipping...")

    if "ix_tf_user_project_user_id" in indexes:
        op.drop_index(op.f("ix_tf_user_project_user_id"), table_name="tf_user_project")
    else:
        print("⏭️ Index 'ix_tf_user_project_user_id' does not exist, skipping...")

    # 3. Удаляем constraint (тоже с проверкой)
    # Проверяем, существует ли constraint
    constraints = [
        const["name"] for const in inspector.get_unique_constraints("tf_user_project")
    ]
    if "tf_user_project_user_id_project_id_key" in constraints:
        op.drop_constraint(
            op.f("tf_user_project_user_id_project_id_key"),
            "tf_user_project",
            type_="unique",
        )
    else:
        print(
            "⏭️ Constraint 'tf_user_project_user_id_project_id_key' does not exist, skipping..."
        )

    # 4. Удаляем колонку role (с проверкой)
    columns = [col["name"] for col in inspector.get_columns("tf_user_project")]
    if "role" in columns:
        op.drop_column("tf_user_project", "role")
    else:
        print("⏭️ Column 'role' does not exist in tf_user_project, skipping...")

    # 5. Добавляем колонки в tf_users (с проверкой)
    user_columns = [col["name"] for col in inspector.get_columns("tf_users")]

    if "updated_at" not in user_columns:
        op.add_column(
            "tf_users",
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
        )
    else:
        print("⏭️ Column 'updated_at' already exists in tf_users, skipping...")

    if "is_superuser" not in user_columns:
        op.add_column(
            "tf_users",
            sa.Column(
                "is_superuser",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
    else:
        print("⏭️ Column 'is_superuser' already exists in tf_users, skipping...")

    if "is_verified" not in user_columns:
        op.add_column(
            "tf_users",
            sa.Column(
                "is_verified",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
    else:
        print("⏭️ Column 'is_verified' already exists in tf_users, skipping...")

    # 6. Изменяем колонки (с проверкой типа)
    # Здесь сложнее проверить тип, поэтому просто выполняем
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

    # 7. Удаляем constraint и создаём индекс (с проверкой)
    constraints = [
        const["name"] for const in inspector.get_unique_constraints("tf_users")
    ]
    if "tf_users_email_key" in constraints:
        op.drop_constraint(op.f("tf_users_email_key"), "tf_users", type_="unique")
    else:
        print("⏭️ Constraint 'tf_users_email_key' does not exist, skipping...")

    # Проверяем, существует ли индекс
    user_indexes = [idx["name"] for idx in inspector.get_indexes("tf_users")]
    if "ix_tf_users_email" not in user_indexes:
        op.create_index(op.f("ix_tf_users_email"), "tf_users", ["email"], unique=True)
    else:
        print("⏭️ Index 'ix_tf_users_email' already exists, skipping...")


def downgrade() -> None:
    # Аналогично для downgrade добавляем проверки
    conn = op.get_bind()
    inspector = inspect(conn)

    # Проверяем индексы перед удалением
    user_indexes = [idx["name"] for idx in inspector.get_indexes("tf_users")]
    if "ix_tf_users_email" in user_indexes:
        op.drop_index(op.f("ix_tf_users_email"), table_name="tf_users")
    else:
        print("⏭️ Index 'ix_tf_users_email' does not exist, skipping...")

    # Создаём constraint только если его нет
    constraints = [
        const["name"] for const in inspector.get_unique_constraints("tf_users")
    ]
    if "tf_users_email_key" not in constraints:
        op.create_unique_constraint(
            op.f("tf_users_email_key"),
            "tf_users",
            ["email"],
            postgresql_nulls_not_distinct=False,
        )
    else:
        print("⏭️ Constraint 'tf_users_email_key' already exists, skipping...")

    # Восстанавливаем типы колонок
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

    # Удаляем колонки (с проверкой)
    user_columns = [col["name"] for col in inspector.get_columns("tf_users")]

    if "is_verified" in user_columns:
        op.drop_column("tf_users", "is_verified")
    else:
        print("⏭️ Column 'is_verified' does not exist in tf_users, skipping...")

    if "is_superuser" in user_columns:
        op.drop_column("tf_users", "is_superuser")
    else:
        print("⏭️ Column 'is_superuser' does not exist in tf_users, skipping...")

    if "updated_at" in user_columns:
        op.drop_column("tf_users", "updated_at")
    else:
        print("⏭️ Column 'updated_at' does not exist in tf_users, skipping...")

    # Восстанавливаем колонку role (с проверкой)
    project_columns = [col["name"] for col in inspector.get_columns("tf_user_project")]
    if "role" not in project_columns:
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
    else:
        print("⏭️ Column 'role' already exists in tf_user_project, skipping...")

    # Создаём constraint (с проверкой)
    constraints = [
        const["name"] for const in inspector.get_unique_constraints("tf_user_project")
    ]
    if "tf_user_project_user_id_project_id_key" not in constraints:
        op.create_unique_constraint(
            op.f("tf_user_project_user_id_project_id_key"),
            "tf_user_project",
            ["user_id", "project_id"],
            postgresql_nulls_not_distinct=False,
        )
    else:
        print(
            "⏭️ Constraint 'tf_user_project_user_id_project_id_key' already exists, skipping..."
        )

    # Восстанавливаем индексы (с проверкой)
    indexes = [idx["name"] for idx in inspector.get_indexes("tf_user_project")]

    if "ix_tf_user_project_user_id" not in indexes:
        op.create_index(
            op.f("ix_tf_user_project_user_id"),
            "tf_user_project",
            ["user_id"],
            unique=False,
        )
    else:
        print("⏭️ Index 'ix_tf_user_project_user_id' already exists, skipping...")

    if "ix_tf_user_project_role" not in indexes:
        op.create_index(
            op.f("ix_tf_user_project_role"),
            "tf_user_project",
            ["role"],
            unique=False,
        )
    else:
        print("⏭️ Index 'ix_tf_user_project_role' already exists, skipping...")

    if "ix_tf_user_project_project_id" not in indexes:
        op.create_index(
            op.f("ix_tf_user_project_project_id"),
            "tf_user_project",
            ["project_id"],
            unique=False,
        )
    else:
        print("⏭️ Index 'ix_tf_user_project_project_id' already exists, skipping...")

    # Удаляем индекс из tf_accesstoken (с проверкой)
    token_indexes = [idx["name"] for idx in inspector.get_indexes("tf_accesstoken")]
    if "ix_tf_accesstoken_created_at" in token_indexes:
        op.drop_index(op.f("ix_tf_accesstoken_created_at"), table_name="tf_accesstoken")
    else:
        print("⏭️ Index 'ix_tf_accesstoken_created_at' does not exist, skipping...")

    op.drop_table("tf_accesstoken")
