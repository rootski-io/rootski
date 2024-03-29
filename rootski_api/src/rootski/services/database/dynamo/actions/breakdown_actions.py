"""
These are the actions needed to query/post into the dynamo table for the breakdown endpoints.

Given a word_id for a single breakdown, retrieve the breakdown in the following order of priority:

(1) A breakdown whose "is_verified" attribute is true. Example: выглядеть.
(2) A breakdown submitted by the logged in user.
(3) A breakdown submitted by another user. # Example самоусовершенствование.
(4) The inferred breakdown submitted by "anonymous. Example выходить.
(5) No breakdown found.


Given a new breakdown to post by a user, perform the following actions in this order of priority:
(1) Check that breakdown is valid by
    (a) querying dynamo for word and morphemes
    (b) creating a valid breakdown object
(2) Check if the user is an admin
(3) Upsert the valid breakdown to dynamo

NOTE: Dynamodb cannot perform batch queries on global secondary indexes.
Therefore in get_morphemes() we will need to loop over the individual keys.

NOTE: Consider the following when using get_morpheme_families() function.
Dynamodb's batch_get_item() function is used to return a morpheme_family for each valid morpheme_family_id.
If a bad id is given, dynamodb skips that id and does alert the user an id was skipped/not found.
Therefore a user can tell an id was bad if they submit n ids, but only get m < n in return.
As of now, we assume no bad inputs are possible.
The function get_morpheme_family_ids_of_non_null_breakdown_items() is used to filter out Null Breakdown items.
"""


from typing import Dict, List, Union

from boto3.dynamodb.conditions import Key
from mypy_boto3_dynamodb.type_defs import (
    GetItemOutputTableTypeDef,
    KeysAndAttributesServiceResourceTypeDef,
    PutItemOutputTableTypeDef,
    QueryOutputTableTypeDef,
)
from rootski.schemas import breakdown as schemas
from rootski.services.database.dynamo.actions.dynamo import (
    batch_get_item_status_code,
    get_item_from_dynamo_response,
    get_item_status_code,
    get_items_from_dynamo_batch_get_items_response,
    get_items_from_dynamo_query_response,
)
from rootski.services.database.dynamo.db_service import DBService
from rootski.services.database.dynamo.errors import (
    BREAKDOWN_NOT_FOUND,
    MORPHEME_FAMILY_IDS_NOT_FOUND_MSG,
    USER_BREAKDOWN_NOT_FOUND,
    BreakdownNotFoundError,
    MorphemeFamilyNotFoundError,
    MorphemeNotFoundError,
    UserBreakdownNotFoundError,
)
from rootski.services.database.dynamo.models.breakdown import Breakdown
from rootski.services.database.dynamo.models.breakdown import make_keys as make_keys__breakdown
from rootski.services.database.dynamo.models.breakdown import make_unofficial_keys
from rootski.services.database.dynamo.models.morpheme import Morpheme
from rootski.services.database.dynamo.models.morpheme import make_gsi1_keys as make_gsi1_keys__morpheme
from rootski.services.database.dynamo.models.morpheme_family import MorphemeFamily
from rootski.services.database.dynamo.models.morpheme_family import make_keys as make_keys__morpheme_family


def get_official_breakdown_by_word_id(word_id: str, db: DBService) -> Breakdown:
    """Query a breakdown from Dynamo matching the ``word_id``.

    :raises BreakdownNotFoundError: raised if no breakdown exists for the given ``word``.
    """
    table = db.rootski_table
    breakdown_dynamo_keys: dict = make_keys__breakdown(word_id=word_id)

    get_item_response: GetItemOutputTableTypeDef = table.get_item(Key=breakdown_dynamo_keys)
    if get_item_status_code(item_output=get_item_response) == 404 or "Item" not in get_item_response.keys():
        raise BreakdownNotFoundError(BREAKDOWN_NOT_FOUND.format(word_id=word_id))
    item = get_item_from_dynamo_response(get_item_response)
    breakdown = Breakdown.from_dict(breakdown_dict=item)

    return breakdown


def is_breakdown_verified(breakdown: Breakdown) -> bool:
    """Returns the bool of breakdown.is_verified"""
    return breakdown.is_verified


def get_user_submitted_breakdown_by_user_email_and_word_id(
    word_id: str, user_email: str, db: DBService
) -> Breakdown:
    """Query a breakdown from Dynamo matching the ``word_id`` and ``user_email``."""
    table = db.rootski_table
    breakdown_dynamo_keys: dict = make_unofficial_keys(user_email=user_email, word_id=word_id)

    get_item_response = table.get_item(Key=breakdown_dynamo_keys)

    if get_item_status_code(item_output=get_item_response) == 404 or "Item" not in get_item_response.keys():
        raise UserBreakdownNotFoundError(
            USER_BREAKDOWN_NOT_FOUND.format(word_id=word_id, user_email=user_email)
        )
    item = get_item_from_dynamo_response(get_item_response)
    breakdown = Breakdown.from_dict(breakdown_dict=item)

    return breakdown


def get_official_breakdown_submitted_by_another_user(word_id: str, db: DBService) -> Breakdown:
    """Query a breakdown from Dynamo from another user."""
    table = db.rootski_table

    query_response: QueryOutputTableTypeDef = table.query(
        IndexName="gsi2",
        KeyConditionExpression=Key("gsi2pk").eq(f"WORD#{word_id}") & Key("gsi2sk").begins_with("USER#"),
    )

    items: List[dict] = get_items_from_dynamo_query_response(query_response)
    if len(items) == 0:
        raise BreakdownNotFoundError(f"No word with ID {word_id} was found in Dynamo.")

    breakdown = Breakdown.from_dict(breakdown_dict=items[0])

    return breakdown


def get_morpheme_families_for_breakdown(breakdown: Breakdown, db: DBService) -> Dict[str, MorphemeFamily]:
    """Batch query the needed morpheme families from Dynamo to enrich a breakdown object."""
    unique_morpheme_family_ids: List[str] = get_unique_morpheme_family_ids_of_non_null_breakdown_items(
        breakdown=breakdown
    )
    morpheme_family_data = get_morpheme_families(morpheme_family_ids=unique_morpheme_family_ids, db=db)
    return morpheme_family_data


def get_morpheme_families(morpheme_family_ids: List[str], db: DBService) -> Dict[str, MorphemeFamily]:
    dynamo = db.dynamo
    table = db.rootski_table

    unique_morpheme_family_ids: List[str] = list(set(morpheme_family_ids))

    # If there are only null_breakdown_items, then there is no reason to query dynamo.
    if len(unique_morpheme_family_ids) == 0:
        return {}

    unique_morpheme_family_keys__to_fetch: List[dict] = [
        make_keys__morpheme_family(morpheme_family_id=morpheme_family_id)
        for morpheme_family_id in unique_morpheme_family_ids
    ]

    get_response_items = dynamo.batch_get_item(
        RequestItems={
            table.name: KeysAndAttributesServiceResourceTypeDef(Keys=unique_morpheme_family_keys__to_fetch)
        },
    )

    items: List[dict] = get_items_from_dynamo_batch_get_items_response(
        item_output=get_response_items, table_name=table.name
    )

    # TODO: We do not expect this error to be thrown, so there are currently no unit-tests.
    if batch_get_item_status_code(item_output=get_response_items) == 404 or len(items) != len(
        unique_morpheme_family_keys__to_fetch
    ):
        raise MorphemeFamilyNotFoundError(
            MORPHEME_FAMILY_IDS_NOT_FOUND_MSG.format(not_found_ids=set(unique_morpheme_family_ids))
        )

    morpheme_family_data = make_id_morpheme_family_map(morpheme_family_data_objs=items)

    return morpheme_family_data


def get_morphemes(morpheme_ids: List[str], db: DBService) -> Dict[str, Morpheme]:
    db.dynamo
    table = db.rootski_table
    unique_morpheme_ids: List[str] = list(set(morpheme_ids))

    # If there are only null_breakdown_items, then there is no reason to query dynamo.
    if len(unique_morpheme_ids) == 0:
        return {}

    unique_morpheme_keys__to_fetch: List[dict] = [
        make_gsi1_keys__morpheme(morpheme_id=morpheme_id) for morpheme_id in unique_morpheme_ids
    ]

    items: List[dict] = []
    for morpheme_keys in unique_morpheme_keys__to_fetch:
        query_response: QueryOutputTableTypeDef = table.query(
            IndexName="gsi1",
            KeyConditionExpression=Key("gsi1pk").eq(morpheme_keys["gsi1pk"])
            & Key("gsi1sk").eq(morpheme_keys["gsi1sk"]),
        )
        if (
            get_item_status_code(item_output=query_response) != 200
            or "Items" not in query_response.keys()
            or len(query_response["Items"]) == 0
        ):
            raise MorphemeNotFoundError(
                MorphemeNotFoundError.make_error_message(morpheme_ids=unique_morpheme_ids)
            )
        item: List[dict] = get_items_from_dynamo_query_response(query_response)
        items.append(item[0])

    morpheme_data = make_id_morpheme_map(morpheme_data_objs=items)

    return morpheme_data


def upsert_breakdown(breakdown: Breakdown, is_official: bool, db: DBService) -> None:
    table = db.rootski_table
    breakdown_data: dict = breakdown.to_item(is_official=is_official)
    response: PutItemOutputTableTypeDef = table.put_item(Item=breakdown_data)


####################
# Helper Functions #
####################


def get_unique_morpheme_family_ids_of_non_null_breakdown_items(breakdown: Breakdown) -> List[str]:
    breakdown_items = breakdown.breakdown_items
    morpheme_family_ids = [
        breakdown_item["morpheme_family_id"]
        for breakdown_item in breakdown_items
        if breakdown_item["morpheme_family_id"] is not None
    ]

    # There may be duplicate id's in morpheme_family_ids, so we only return unique id's
    return list(set(morpheme_family_ids))


def make_id_morpheme_family_map(morpheme_family_data_objs: List[dict]) -> Dict[str, MorphemeFamily]:

    morpheme_families_data = {
        family_data["family_id"]: MorphemeFamily.from_dict(family_data)
        for family_data in morpheme_family_data_objs
    }

    return morpheme_families_data


def get_unique_morpheme_ids_of_non_null_breakdown_items(
    breakdown_items: List[Union[schemas.NullMorphemeBreakdownItem, schemas.MorphemeBreakdownItemInRequest]]
) -> List[str]:
    morpheme_ids = [
        str(breakdown_item.morpheme_id)
        for breakdown_item in breakdown_items
        if breakdown_item.morpheme_id is not None
    ]

    # There may be duplicate id's in morpheme_ids, so we only return unique id's
    return list(set(morpheme_ids))


def make_id_morpheme_map(morpheme_data_objs: List[dict]) -> Dict[str, Morpheme]:
    morpheme_data = {
        morpheme_data_obj["morpheme_id"]: Morpheme.from_dict(morpheme_data_obj)
        for morpheme_data_obj in morpheme_data_objs
    }

    return morpheme_data


def see_whether_breakdowns_are_overwritten(db: DBService):
    table = db.rootski_table
    get_items_response = table.query(
        IndexName="gsi2",
        KeyConditionExpression=Key("gsi2pk").eq("WORD#7") & Key("gsi2sk").eq("USER#email@gmail.com"),
    )

    items: List[dict] = get_items_from_dynamo_query_response(get_items_response)
    print(items)

    get_items_response = table.query(
        IndexName="gsi1",
        KeyConditionExpression=Key("gsi1pk").eq("USER#anonymous") & Key("gsi1sk").eq("WORD#7"),
    )
    items: List[dict] = get_items_from_dynamo_query_response(get_items_response)
    print(items)
