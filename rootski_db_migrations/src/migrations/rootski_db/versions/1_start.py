# pylint: disable=invalid-name
"""start

This is an empty revision. It's useful to start your database migration chain
with an empty revision so that migrating to the first revision results in an
empty database.

Revision ID: 6e442c999465
Revises:
Create Date: 2020-10-17 12:33:38.559290
"""  # noqa: D400

# revision identifiers, used by Alembic.
revision = "1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Do nothing (intentionally)."""


def downgrade():
    """Do nothing (intentionally)."""
