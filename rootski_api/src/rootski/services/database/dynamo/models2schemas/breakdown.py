from datetime import datetime
from typing import Dict

import rootski.services.database.dynamo.models as dynamo
from rootski.schemas import breakdown as schemas
from rootski.services.database.dynamo.models2schemas.breakdown_item import dynamo_to_pydantic__breakdown_item


def dynamo_to_pydantic__breakdown(
    breakdown: dynamo.Breakdown,
    ids_to_morpheme_families: Dict[str, dynamo.MorphemeFamily],
    user_email: str,
) -> schemas.GetBreakdownResponse:

    return schemas.GetBreakdownResponse(
        word_id=breakdown.word_id,
        word=breakdown.word,
        is_verified=breakdown.is_verified,
        is_inference=breakdown.is_inference,
        date_submitted=datetime.strptime(breakdown.date_submitted, "%Y-%m-%d %H:%M:%S.%f"),
        date_verified=None
        if breakdown.is_verified is False
        else datetime.strptime(breakdown.date_verified, "%Y-%m-%d %H:%M:%S.%f"),
        submitted_by_current_user=True
        if breakdown.submitted_by_user_email == user_email
        else False,  # check this not true
        breakdown_items=[
            dynamo_to_pydantic__breakdown_item(
                breakdown_item_item=breakdown_item,
                morpheme_family_data=ids_to_morpheme_families,
            )
            for breakdown_item in breakdown.breakdown_items
        ],
    )
