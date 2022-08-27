from typing import Dict, Union

import rootski.services.database.dynamo.models as dynamo
from rootski.schemas import breakdown as schemas
from rootski.schemas.morpheme import MorphemeFamily
from rootski.services.database.dynamo.models2schemas.breakdown_item import dynamo_to_pydantic__breakdown_item


def breakdown_item_item__to_dynamo__breakdown_item(
    breakdown_item_item: dynamo.BreakdownItemItem,
    word_id: str,
    submitted_by_user_email: str,
    breakdown_id: int,
) -> Union[dynamo.NullBreakdownItem, dynamo.BreakdownItem]:

    if breakdown_item_item["morpheme_id"] is None:
        return dynamo.NullBreakdownItem(
            position=breakdown_item_item["position"],
            morpheme=breakdown_item_item["morpheme"],
            word_id=word_id,
            submitted_by_user_email=submitted_by_user_email,
        )

    return dynamo.BreakdownItem(
        position=breakdown_item_item["position"],
        morpheme=breakdown_item_item["morpheme"],
        morpheme_id=breakdown_item_item["morpheme"],
        morpheme_family_id=breakdown_item_item["morpheme_family_id"],
        word_id=word_id,
        submitted_by_user_email=submitted_by_user_email,
        breakdown_id=breakdown_id,
    )


def dynamo_to_pydantic__breakdown(
    breakdown: dynamo.Breakdown, morhpeme_family_dict: Dict[str, MorphemeFamily]
) -> schemas.GetBreakdownResponse:
    return schemas.GetBreakdownResponse(
        word_id=breakdown.word_id,
        word=breakdown.word,
        is_verified=breakdown.is_verified,
        is_inference=breakdown.is_inference,
        date_submitted=breakdown.date_submitted,
        date_verified=breakdown.date_verified,
        submitted_by_current_user=breakdown.submitted_by_user_email,
        breakdown_items=[
            dynamo_to_pydantic__breakdown_item(breakdown_item) for breakdown_item in breakdown.breakdown_items
        ],
    )
