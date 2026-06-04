"""add_func_updated_at

Revision ID: b797acf9674a
Revises: 01cd98cef5d8
Create Date: 2026-06-04 13:04:06.111570

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.core.config import BASE_DIR

# revision identifiers, used by Alembic.
revision: str = "b797acf9674a"
down_revision: Union[str, Sequence[str], None] = "01cd98cef5d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sql_path = BASE_DIR / "migrations/scripts/func_update_updated_at_column.sql"
    try:
        sql_content = sql_path.read_text(encoding="utf-8")
        op.execute(sql_content)
    except Exception as e:
        op.execute("ROLLBACK")  # если внутри транзакции
        raise RuntimeError(f"Ошибка при применении миграции: {e}") from e


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP FUNCTION update_updated_at_column() CASCADE;")
