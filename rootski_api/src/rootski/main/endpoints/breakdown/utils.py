from typing import Dict, List, Union

from sqlalchemy.orm import Session

from rootski import schemas
from rootski.main.endpoints.breakdown.errors import (
    MORPHEME_IDS_NOT_FOUND_MSG,
    PARTS_DONT_SUM_TO_WHOLE_WORD_MSG,
    BadBreakdownError,
    MorphemeNotFoundError,
)
from rootski.services.database import models as orm


def query_morphemes(
    db: Session,
    breakdown_items: List[Union[schemas.NullMorphemeBreakdownItem, schemas.MorphemeBreakdownItemInRequest]],
) -> Dict[int, str]:
    """
    :raises MorphemeNotFoundError: morphemes in the breakdown don't exist in the database
    """
    morpheme_breakdown_ids = [
        item.morpheme_id for item in breakdown_items if isinstance(item, schemas.MorphemeBreakdownItemInRequest)
    ]
    morphemes = db.query(orm.Morpheme).filter(orm.Morpheme.morpheme_id.in_(morpheme_breakdown_ids)).all()
    id_to_morpheme: Dict[int, str] = {m.morpheme_id: m.morpheme for m in morphemes}

    # make sure each morpheme id in the breakdown_items was present in the database
    if len(morphemes) != len(morpheme_breakdown_ids):
        not_found_ids = set(morpheme_breakdown_ids) - set(id_to_morpheme.keys())
        raise MorphemeNotFoundError(MORPHEME_IDS_NOT_FOUND_MSG.format(not_found_ids=str(not_found_ids)))

    return id_to_morpheme


def raise_exception_for_invalid_breakdown(
    db: Session,
    word: str,
    breakdown_items: List[Union[schemas.NullMorphemeBreakdownItem, schemas.MorphemeBreakdownItemInRequest]],
    id_to_morpheme: Dict[int, str],
):
    """
    :raises BadBreakdownError: The morphemes don't add up to the word
    """

    # make sure the morphemes add up to the word:
    # (1) get the morphemes in order
    sorted_breakdown_items = sorted(breakdown_items, key=lambda item: item.position)

    def get_morpheme(
        item: Union[schemas.NullMorphemeBreakdownItem, schemas.MorphemeBreakdownItemInRequest]
    ) -> str:
        if isinstance(item, schemas.NullMorphemeBreakdownItem):
            return item.morpheme
        else:
            return id_to_morpheme[item.morpheme_id]

    ordered_morpheme_strings = [get_morpheme(item) for item in sorted_breakdown_items]

    # (2) ensure that they match the word
    if "".join(ordered_morpheme_strings) != word:
        submitted_breakdown = "-".join(ordered_morpheme_strings)
        raise BadBreakdownError(
            PARTS_DONT_SUM_TO_WHOLE_WORD_MSG.format(submitted_breakdown=submitted_breakdown, word=word)
        )
