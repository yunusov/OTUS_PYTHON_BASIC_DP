"""create_access_tocken_table

Revision ID: 531d13d60870
Revises: a55fa878c4dd
Create Date: 2026-05-13 19:29:56.930939

"""

from typing import Sequence, Union

from alembic import op
import fastapi_users_db_sqlalchemy.generics
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "531d13d60870"
down_revision: Union[str, Sequence[str], None] = "a55fa878c4dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
