"""add_triggers_updated_at

Revision ID: 3ffa77f1a6ee
Revises: b797acf9674a
Create Date: 2026-06-04 17:59:44.026450

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.core.config import BASE_DIR

# revision identifiers, used by Alembic.
revision: str = "3ffa77f1a6ee"
down_revision: Union[str, Sequence[str], None] = "b797acf9674a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sql_path = BASE_DIR / "migrations/scripts/trigger_update_table.sql"
    try:
        sql_content = sql_path.read_text(encoding="utf-8")
        op.execute(sql_content)
    except Exception as e:
        op.execute("ROLLBACK")  # если внутри транзакции
        raise RuntimeError(f"Ошибка при применении миграции: {e}") from e


def downgrade() -> None:
    """Downgrade schema."""
    pass
