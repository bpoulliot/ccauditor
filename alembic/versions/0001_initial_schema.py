from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade():

    pass