"""merge heads

Revision ID: b71e0970ab9f
Revises: 40c91e15b21e, 5a89f2f06992
Create Date: 2026-05-19 11:44:15.379183

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b71e0970ab9f"
down_revision: Union[str, Sequence[str], None] = (
    "40c91e15b21e",
    "5a89f2f06992",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
