"""
These are the actions needed to query the dynamo table for the breakdown endpoint.

For a word_id, retrieve a single breakdown in the following order of priority:

(1) A breakdown whose "is_verified" attribute is true.
(2) A breakdown submitted by the logged in user.
(3) A breakdown submitted by another user.
(4) The inferred breakdown submitted by "anonymous:.
(5) No breakdown found.
"""

from typing import List

from boto3.dynamodb.conditions import Key
from rootski.services.database.dynamo.actions.dynamo import (
    get_item_from_dynamo_response,
    get_item_status_code,
    get_items_from_dynamo_query_response,
)
from rootski.services.database.dynamo.db_service import DBService
from rootski.services.database.dynamo.models.breakdown import Breakdown, make_gsi1_keys, make_keys
from rootski.services.database.dynamo.models.morpheme_family import MorphemeFamily


class BreakdownNotFoundError(Exception):
    """Error thrown if a Breakdown isn't found."""


class MorphemeFamilyNotFoundError(Exception):
    """Error thrown if a MorphemeFamily isn't found."""


def get_official_breakdown_by_word_id(word_id: str, db: DBService) -> Breakdown:
    """Query a breakdown from Dynamo matching the ``word_id``.

    :raises BreakdownNotFoundError: raised if no breakdown exists for the given ``word``.
    """
    table = db.rootski_table
    breakdown_dynamo_keys: dict = make_keys(word_id=word_id)

    get_item_response = table.get_item(Key=breakdown_dynamo_keys)
    if get_item_status_code(item_output=get_item_response) == 404:
        raise BreakdownNotFoundError(f"No word with ID {word_id} was found in Dynamo.")

    item = get_item_from_dynamo_response(get_item_response)
    breakdown = Breakdown.from_dict(breakdown_dict=item)

    return breakdown


def is_breakdown_verified(breakdown: Breakdown) -> bool:
    """Returns the bool of breakdown.is_verified"""
    return breakdown.is_verified


def get_breakdown_submitted_by_user_email_and_word_id(
    word_id: str, user_email: str, db: DBService
) -> Breakdown:
    """Query a breakdown from Dynamo matching the ``word_id`` and ``user_email``."""
    table = db.rootski_table
    breakdown_dynamo_keys: dict = make_gsi1_keys(submitted_by_user_email=user_email, word_id=word_id)

    get_items_response = table.query(
        IndexName="gsi1",
        KeyConditionExpression=Key("gsi1pk").eq(breakdown_dynamo_keys["gsi1pk"])
        & Key("gsi1sk").eq(breakdown_dynamo_keys["gsi1sk"]),
    )

    items: List[dict] = get_items_from_dynamo_query_response(get_items_response)
    if len(items) == 0:
        raise BreakdownNotFoundError(f"No word with ID {word_id} was found in Dynamo for user {user_email}.")

    breakdown = Breakdown.from_dict(breakdown_dict=items[0])

    return breakdown


def get_official_breakdown_submitted_by_another_user(word_id: str, db: DBService) -> Breakdown:
    """Query a breakdown from Dynamo from another user."""
    table = db.rootski_table
    breakdown_dynamo_keys: dict = make_keys(word_id=word_id)

    get_items_response = table.query(
        KeyConditionExpression=Key("pk").eq(breakdown_dynamo_keys["pk"])
        & Key("sk").eq(breakdown_dynamo_keys["sk"]),
    )

    items: List[dict] = get_items_from_dynamo_query_response(get_items_response)
    if len(items) == 0:
        raise BreakdownNotFoundError(f"No word with ID {word_id} was found in Dynamo.")

    breakdown = Breakdown.from_dict(breakdown_dict=items[0])

    return breakdown


def get_morpheme_family(morpheme_family_id: str, db: DBService) -> MorphemeFamily:
    """Query a morpheme_family from Dynamo."""
    table = db.rootski_table
    get_items_response = table.query(
        KeyConditionExpression=Key("pk").eq(f"MORPHEME_FAMILY#{morpheme_family_id}")
        & Key("sk").eq(f"MORPHEME_FAMILY#{morpheme_family_id}"),
    )

    items: List[dict] = get_items_from_dynamo_query_response(get_items_response)
    if len(items) == 0:
        raise MorphemeFamilyNotFoundError(
            f"No morpheme family with ID {morpheme_family_id} was found in Dynamo."
        )
    # pprint(items)
    morpheme_family = MorphemeFamily.from_dict(morpheme_family_dict=items[0])

    return morpheme_family


# if __name__ == "__main__":
#     db = DBService("rootski-table")
#     db.init()
#     table = db.rootski_table
#     get_item_response = table.get_item(
#         Key={"pk": "MORPHEME_FAMILY#1385", "sk": "MORPHEME_FAMILY#1385"}
#     )  # eric.riddoch@gmail.com"})
#     print(get_item_response["Item"])
