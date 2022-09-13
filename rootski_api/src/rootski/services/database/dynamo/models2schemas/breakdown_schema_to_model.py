from datetime import datetime
from typing import Dict, List, Union

from rootski.schemas import breakdown as schemas
from rootski.services.database.dynamo.models.breakdown import Breakdown
from rootski.services.database.dynamo.models.breakdown_item import BreakdownItem, NullBreakdownItem
from rootski.services.database.dynamo.models.morpheme import Morpheme


def pydantic_to_dynamo__breakdown(
    user_breakdown: schemas.BreakdownUpsert,
    morpheme_data: Dict[str, Morpheme],
    user_email: str,
    word: str,
    is_admin: bool,
) -> Breakdown:

    breakdown_items: List[Union[NullBreakdownItem, BreakdownItem]] = [
        pydantic_to_dynamo__breakdown_item(
            breakdown_item=breakdown_item,
            morpheme_data_objs=morpheme_data,
            user_email=user_email,
            word_id=user_breakdown.word_id,
        )
        for breakdown_item in user_breakdown.breakdown_items
    ]

    if is_admin:
        return Breakdown(
            word=word,
            word_id=user_breakdown.word_id,
            is_verified=True,
            is_inference=False,
            submitted_by_user_email=user_email,
            date_submitted=datetime.now(),
            date_verified=datetime.now(),
            breakdown_items=breakdown_items,
        )

    return Breakdown(
        word=word,
        word_id=user_breakdown.word_id,
        is_verified=False,
        is_inference=False,
        submitted_by_user_email=user_email,
        date_submitted=datetime.now(),
        date_verified=None,
        breakdown_items=breakdown_items,
    )


def pydantic_to_dynamo__breakdown_item(
    breakdown_item: Union[schemas.NullMorphemeBreakdownItem, schemas.MorphemeBreakdownItemInRequest],
    morpheme_data_objs: Dict[str, Morpheme],
    user_email: str,
    word_id: str,
) -> Union[NullBreakdownItem, BreakdownItem]:
    DEPRECATED_BREAKDOWN_ID = -1

    if breakdown_item.morpheme_id is None:
        return NullBreakdownItem(
            word_id=word_id,
            position=breakdown_item.position,
            morpheme=breakdown_item.morpheme,
            submitted_by_user_email=user_email,
        )

    return BreakdownItem(
        word_id=word_id,
        position=breakdown_item.position,
        morpheme=morpheme_data_objs[str(breakdown_item.morpheme_id)].morpheme,
        morpheme_id=breakdown_item.morpheme_id,
        morpheme_family_id=morpheme_data_objs[str(breakdown_item.morpheme_id)].family_id,
        submitted_by_user_email=user_email,
        breakdown_id=DEPRECATED_BREAKDOWN_ID,
    )
