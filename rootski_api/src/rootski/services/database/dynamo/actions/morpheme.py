from typing import Dict, List

from mypy_boto3_dynamodb.type_defs import KeysAndAttributesServiceResourceTypeDef
from rootski.services.database.dynamo.actions.dynamo import (
    get_items_from_dynamo_batch_get_items_response,
    batch_get_item_status_code,
)
from rootski.services.database.dynamo.db_service import DBService as DynamoDBService
from rootski.services.database.dynamo.models.morpheme_family import MorphemeFamily
from rootski.services.database.dynamo.models.morpheme import Morpheme, make_gsi1sk_keys


class MorphemeNotFoundError(Exception):
    """Error thrown if a Morpheme isn't found."""


class MorphemeFamilyNotFoundError(Exception):
    """Error thrown if a MorphemeFamily isn't found."""


def get_all_morphemes(db: DynamoDBService) -> List[Morpheme]:
    """Query all of the morpheme objects in dynamo."""
    dynamo = db.dynamo
    table = db.rootski_table

    morpheme_ids: List[str] = None

    batch_keys: List[dict] = [make_gsi1sk_keys(morpheme_id=morpheme_id) for morpheme_id in morpheme_ids]

    get_response_items = dynamo.batch_get_item(
        RequestItems={table.name: KeysAndAttributesServiceResourceTypeDef(Keys=batch_keys)},
    )

    items: List[dict] = get_items_from_dynamo_batch_get_items_response(
        item_output=get_response_items, table_name=table.name
    )

    # TODO: We do not expect this error to be thrown, so there are currently no unit-tests.
    if batch_get_item_status_code(item_output=get_response_items) == 404:
        raise MorphemeNotFoundError("One of your morpheme IDs was not found in Dynamo.")

    morpheme_family_dict = make_id_morpheme_family_map(dynamo_list_of_morpheme_families=items)

    return morpheme_family_dict


def make_id_morpheme_family_map(dynamo_list_of_morpheme_families: List[dict]) -> Dict[str, MorphemeFamily]:

    morpheme_families_dict = {
        family_dict["family_id"]: MorphemeFamily.from_dict(family_dict)
        for family_dict in dynamo_list_of_morpheme_families
    }

    return morpheme_families_dict


def get_morpheme_families(breakdown: , db: DynamoDBService) -> Dict[str, MorphemeFamily]:
    """Batch query the needed morpheme families from Dynamo to enrich a breakdown object."""
    dynamo = db.dynamo
    table = db.rootski_table

    morpheme_family_ids: List[str] = get_morpheme_family_ids_of_non_null_breakdown_items(breakdown=breakdown)

    # If there are only null_breakdown_items, then there is no reason to query dynamo.
    if len(morpheme_family_ids) == 0:
        return {}

    batch_keys: List[dict] = [
        make_keys__morpheme_family(morpheme_family_id=morpheme_family_id)
        for morpheme_family_id in morpheme_family_ids
    ]

    get_response_items = dynamo.batch_get_item(
        RequestItems={table.name: KeysAndAttributesServiceResourceTypeDef(Keys=batch_keys)},
    )

    items: List[dict] = get_items_from_dynamo_batch_get_items_response(
        item_output=get_response_items, table_name=table.name
    )

    # TODO: We do not expect this error to be thrown, so there are currently no unit-tests.
    if batch_get_item_status_code(item_output=get_response_items) == 404:
        raise MorphemeFamilyNotFoundError("One of your morpheme family IDs was not found in Dynamo.")

    morpheme_family_dict = make_id_morpheme_family_map(dynamo_list_of_morpheme_families=items)

    return morpheme_family_dict
