from typing import List, Optional, Tuple

from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from rootski import schemas
from rootski.schemas import MORPHEME_TYPE_ENUM, MORPHEME_WORD_POS_ENUM
from rootski.schemas.morpheme import (
    MORPHEME_TYPE_PREFIX,
    MORPHEME_TYPE_ROOT,
    MORPHEME_TYPE_SUFFIX,
    MORPHEME_WORD_POS_VERB,
)
from rootski.services.database import DBService
from rootski.services.database import models as orm

##########################
# --- Helper Schemas --- #
##########################


class NonstrictMorphemeInDb(BaseModel):
    """
    Used in unit tests for forming requests.
    Not all morpheme information is needed when making a request.
    This class lets us instantiate morphemes without needing all of the fields.
    """

    morpheme: Optional[str]
    type: MORPHEME_TYPE_ENUM
    word_pos: Optional[MORPHEME_WORD_POS_ENUM]
    morpheme_id: Optional[int]
    family_id: Optional[int]
    # family: Optional[schemas.MorphemeFamilyInDb]

    class Config:
        use_enum_values = True
        orm_mode = True
        # arbitrary_types_allowed = True


def insert_test_objs(
    db: DBService, word: orm.Word, morphemes: List[orm.Morpheme]
) -> Tuple[schemas.WordInDb, List[schemas.MorphemeInDb]]:
    """
    Insert the word and morphemes into the database so that they have IDs
    and return the schema versions of those.
    """
    with db.get_sync_session() as session:
        session: Session
        session.add_all([word, *morphemes])
        session.commit()
        return get_schemas_from_models(word=word, morphemes=morphemes)


def get_breakdown_orm_objs() -> Tuple[orm.Word, List[orm.Morpheme]]:
    """Prepare ORM objects for 'приказать'."""
    word = orm.Word(word="приказать", accent="приказа'ть", pos="verb", frequency=1957)

    prefix_family_meaning = orm.MorphemeFamilyMeaning(meaning="Attachment; drawing close to something")
    prefix_family = orm.MorphemeFamily(level=1, family="при", meanings=[prefix_family_meaning])
    prefix = orm.Morpheme(
        morpheme="при",
        type=MORPHEME_TYPE_PREFIX,
        word_pos=MORPHEME_WORD_POS_VERB,
        family=prefix_family,
    )

    root_family_meaning = orm.MorphemeFamilyMeaning(meaning="Showing; communicating something by showing")
    root_family = orm.MorphemeFamily(level=1, family="каз", meanings=[root_family_meaning])
    root = orm.Morpheme(
        morpheme="каз",
        type=MORPHEME_TYPE_ROOT,
        word_pos=MORPHEME_WORD_POS_VERB,
        family=root_family,
    )

    suffix_family_meaning = orm.MorphemeFamilyMeaning(meaning="Basic verb ending")
    suffix_family = orm.MorphemeFamily(level=1, family="ать", meanings=[suffix_family_meaning])
    suffix = orm.Morpheme(
        morpheme="ать",
        type=MORPHEME_TYPE_SUFFIX,
        word_pos=MORPHEME_WORD_POS_VERB,
        family=suffix_family,
    )

    return word, [prefix, root, suffix]


def get_schemas_from_models(
    word: orm.Word, morphemes: List[orm.Morpheme]
) -> Tuple[schemas.WordInDb, List[NonstrictMorphemeInDb]]:
    """
    Return schema versions of the ORM models. They won't have IDs if
    the ORM models haven't been queried from/inserted into the database.
    """
    word_schema = schemas.WordInDb.from_orm(word)
    morpheme_schemas: List[NonstrictMorphemeInDb] = [NonstrictMorphemeInDb.from_orm(m) for m in morphemes]
    return word_schema, morpheme_schemas
