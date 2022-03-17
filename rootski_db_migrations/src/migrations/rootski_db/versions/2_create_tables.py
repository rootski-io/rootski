# pylint: disable=invalid-name
"""
create_tables

Use the version of the SQLAlchemy models in
initial_data/ to create the tables and columns in the database
as they should have been on March 13, 2022. Those SQLAlchemy models
should not be modified for future migrations.

Instead, add, rename, or remove only the exact columns/tables
that a migration calls for.

Revision ID: 2
Revises: 1
Create Date: 2020-10-17 12:36:10.641316
"""
from alembic import op
from migrations.initial_data.initial_models import Base

# revision identifiers, used by Alembic.
revision = "2"
down_revision = "1"
branch_labels = None
depends_on = None


def upgrade():
    # create all of the tables in data_models in the target db
    connection = op.get_bind()
    Base.metadata.create_all(bind=connection)


def downgrade():
    # drop any of the tables in data_models that exist in the target db
    connection = op.get_bind()
    Base.metadata.drop_all(bind=connection)
