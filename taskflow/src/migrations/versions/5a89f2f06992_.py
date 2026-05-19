"""restore missing migration"""

from alembic import op
import sqlalchemy as sa

revision = "5a89f2f06992"
down_revision = "531d13d60870"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
