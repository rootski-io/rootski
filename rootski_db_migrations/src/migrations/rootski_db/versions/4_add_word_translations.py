# pylint: disable=invalid-name
# noqa: D400
"""add_translation_column_to_words_table

Revision ID: 4
Revises: 3
Create Date: 2022-03-20 21:16:47.804931

"""
import json

import pandas as pd
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4"
down_revision = "3"
branch_labels = None
depends_on = None


def upgrade():
    # Create the column
    op.add_column(
        table_name="words",
        column=sa.Column(
            "translation",
            sa.String(512),
            nullable=True,
            comment="a rough english translation for searching english words",
        ),
    )

    # Empty the words table
    # Allows us to empty the words table by bypassing the foreign key constraints
    op.execute("SET session_replication_role = 'replica';")
    op.execute("DELETE FROM WORDS;")

    # Get the words data including translations
    words_df = pd.read_csv("migrations/initial_data/data/words_with_translations.csv")
    words_rows = list(json.loads(words_df.to_json(orient="records")))

    # Get the table object
    meta = sa.MetaData(bind=op.get_bind())
    meta.reflect(only=("words",))
    words_table = sa.Table("words", meta)

    # Insert the data data with translations into the table
    op.bulk_insert(table=words_table, rows=words_rows)


def downgrade():
    """Drop the translations column from the words table and create an empty one."""
    op.drop_column(table_name="words", column_name="translation")
