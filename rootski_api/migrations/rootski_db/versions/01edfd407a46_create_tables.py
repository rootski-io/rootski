"""
NOTE this revision depends on the rootski master data folder
with all required csv's present.

create_tables

Revision ID: 01edfd407a46
Revises: 6e442c999465
Create Date: 2020-10-17 12:36:10.641316

The first migration after the dummy (start) migration.
This creates all the tables in the data_models SQLAlchemy definitions.

"""
from alembic import op

from rootski_api.services.data_models import (  # noqa: 401
    Adjective,
    Base,
    Breakdown,
    BreakdownItem,
    Conjugation,
    Definition,
    DefinitionItem,
    Morpheme,
    MorphemeFamilyMeaning,
    Noun,
    Sentence,
    SentenceTranslation,
    User,
    VerbPair,
    Word,
    WordToSentence,
)

# revision identifiers, used by Alembic.
revision = "01edfd407a46"
down_revision = "6e442c999465"
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
