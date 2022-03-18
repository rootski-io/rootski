# pylint: disable=invalid-name
"""seed_database

Revision ID: c312f8c10ddd
Revises: 01edfd407a46
Create Date: 2021-01-17 22:28:29.335445

"""  # noqa: D400

from alembic import op
from migrations.initial_data.gather_data import load_base_tables
from migrations.initial_data.initial_models import Base
from sqlalchemy.engine import Connection, Engine

# revision identifiers, used by Alembic.
revision = "3"
down_revision = "2"
branch_labels = None
depends_on = None


def upgrade():
    """Load all of the initial_data/ into the database."""
    connection: Connection = op.get_bind()
    engine: Engine = connection.engine
    load_base_tables(engine_override=engine, verbose=True)


def downgrade():
    """Drop the tables associated with the initial data."""
    connection: Connection = op.get_bind()
    Base.metadata.drop_all(bind=connection)
    Base.metadata.create_all(bind=connection)
