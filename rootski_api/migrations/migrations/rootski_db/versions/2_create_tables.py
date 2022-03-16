"""
create_tables

Revision ID: 2
Revises: 1
Create Date: 2020-10-17 12:36:10.641316
"""
from alembic import op
from initial_data.initial_models import Base

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
