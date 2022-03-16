"""seed_database

Revision ID: c312f8c10ddd
Revises: 01edfd407a46
Create Date: 2021-01-17 22:28:29.335445

"""

from alembic import op
from initial_data.gather_data import load_base_tables
from initial_data.initial_models import Base
from sqlalchemy.engine import Connection

# revision identifiers, used by Alembic.
revision = "3"
down_revision = "2"
branch_labels = None
depends_on = None


def upgrade():
    try:
        connection = op.get_bind()
        load_base_tables(seeding_db=True, connection=connection)
    except Exception as e:
        error_msg = str(e)
        with open("/Users/eric/Desktop/rootski/rootski/rootski_api/migrations/error.py", "w") as file:
            file.write(error_msg)
        raise e


def downgrade():
    connection: Connection = op.get_bind()
    Base.metadata.drop_all(bind=connection)
    Base.metadata.create_all(bind=connection)
