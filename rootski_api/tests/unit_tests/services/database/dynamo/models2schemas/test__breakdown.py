from rootski.services.database.database import DBService
from rootski.services.database.dynamo.models.breakdown import Breakdown
from rootski.services.database.dynamo.models.breakdown_item import (
    make_dynamo_breakdown_item_from_dict,
    make_dynamo_BreakdownItemItem_from_dict,
)

# from  rootski_api.tests.fixtures.rootski_dynamo_table import rootski_dynamo_table, dynamo_db_service

# from rootski.services.database.dynamo.models2schemas.word import dynamo_to_pydantic__word
# from rootski.services.database.dynamo.actions.dynamo import get_item_from_dynamo_response, get_item_status_code
# from rootski import schemas


EXAMPLE_BREAKDOWN = {
    "pk": "WORD#32",
    "sk": "BREAKDOWN",
    "gsi1pk": "USER#anonymous",
    "gsi1sk": "WORD#32",
    "gsi2pk": "WORD#32",
    "gsi2sk": "USER#anonymous",
    "__type": "BREAKDOWN",
    "word": "мочь",
    "word_id": "32",
    "submitted_by_user_email": "anonymous",
    "is_verified": False,
    "is_inference": True,
    "date_submitted": "2022-02-15 05:45:18.740114",
    "date_verified": "None",
    "breakdown_items": [{"position": "0", "morpheme_id": None, "morpheme": "мочь", "morpheme_family_id": None}],
}

EXAMPLE_BREAKDOWN_ITEM_1 = {
    "pk": "WORD#136631",
    "sk": "BREAKDOWN_ITEM#1234#2",
    "gsi1pk": "MORPHEME_FAMILY#1234",
    "gsi1sk": "BREAKDOWN#None",
    "__type": "BREAKDOWN_ITEM",
    "word_id": "136631",
    "position": "2",
    "morpheme_family_id": "1234",
    "morpheme": "ка",
    "morpheme_id": "2031",
    "submitted_by_user_email": None,
    "breakdown_id": "5546",
}


EXAMPLE_BREAKDOWN_ITEM_2 = {
    "pk": "WORD#143572",
    "sk": "BREAKDOWN_ITEM#1225#0",
    "gsi1pk": "MORPHEME_FAMILY#1225",
    "gsi1sk": "BREAKDOWN#None",
    "__type": "BREAKDOWN_ITEM",
    "word_id": "143572",
    "morpheme_family_id": "1225",
    "morpheme": "румян",
    "morpheme_id": "1225",
    "submitted_by_user_email": None,
    "breakdown_id": "50547",
}


EXAMPLE_NULL_BREAKDOWN_ITEM_1 = {
    "pk": "WORD#41727",
    "sk": "BREAKDOWN_ITEM#1082#1",
    "gsi1pk": "MORPHEME_FAMILY#1082",
    "gsi1sk": "BREAKDOWN#None",
    "__type": "BREAKDOWN_ITEM",
    "word_id": "41727",
    "morpheme_family_id": "1082",
    "morpheme": "плам",
    "morpheme_id": "1082",
    "submitted_by_user_email": None,
    "breakdown_id": "38665",
}


def test__breakdown_from_dict():
    breakdown = Breakdown.from_dict(breakdown_dict=EXAMPLE_BREAKDOWN)

    assert breakdown.pk == EXAMPLE_BREAKDOWN["pk"]
    assert breakdown.sk == EXAMPLE_BREAKDOWN["sk"]
    assert breakdown.gsi1pk == EXAMPLE_BREAKDOWN["gsi1pk"]
    assert breakdown.gsi1sk == EXAMPLE_BREAKDOWN["gsi1sk"]
    assert breakdown.gsi2pk == EXAMPLE_BREAKDOWN["gsi2pk"]
    assert breakdown.gsi2sk == EXAMPLE_BREAKDOWN["gsi2sk"]
    assert breakdown.word == EXAMPLE_BREAKDOWN["word"]
    assert breakdown.word_id == EXAMPLE_BREAKDOWN["word_id"]
    assert breakdown.submitted_by_user_email == EXAMPLE_BREAKDOWN["submitted_by_user_email"]
    assert breakdown.is_verified == EXAMPLE_BREAKDOWN["is_verified"]
    assert breakdown.is_inference == EXAMPLE_BREAKDOWN["is_inference"]
    assert breakdown.date_submitted == EXAMPLE_BREAKDOWN["date_submitted"]
    assert breakdown.date_verified == EXAMPLE_BREAKDOWN["date_verified"]

    breakdown_items = [
        make_dynamo_BreakdownItemItem_from_dict(breakdown_item)
        for breakdown_item in EXAMPLE_BREAKDOWN["breakdown_items"]
    ]

    assert breakdown.breakdown_items == breakdown_items


def test__breakdown_item_from_dict():
    # Breakdown Item
    breakdown_item = make_dynamo_breakdown_item_from_dict(breakdown_item_dict=EXAMPLE_BREAKDOWN_ITEM_1)
    assert breakdown_item.word_id == EXAMPLE_BREAKDOWN_ITEM_1["word_id"]
    assert breakdown_item.position == EXAMPLE_BREAKDOWN_ITEM_1["position"]
    assert breakdown_item.morpheme == EXAMPLE_BREAKDOWN_ITEM_1["morpheme"]
    assert breakdown_item.submitted_by_user_email == EXAMPLE_BREAKDOWN_ITEM_1["submitted_by_user_email"]
    assert breakdown_item.morpheme_id == EXAMPLE_BREAKDOWN_ITEM_1["morpheme_id"]
    assert breakdown_item.morpheme_family_id == EXAMPLE_BREAKDOWN_ITEM_1["family_id"]
    assert breakdown_item.breakdown_id == EXAMPLE_BREAKDOWN_ITEM_1["breakdown_id"]

    # Null breakdown item
    null_breakdown_item = make_dynamo_breakdown_item_from_dict(
        breakdown_item_dict=EXAMPLE_NULL_BREAKDOWN_ITEM_1
    )
    assert null_breakdown_item.word_id == EXAMPLE_NULL_BREAKDOWN_ITEM_1["word_id"]
    assert null_breakdown_item.position == EXAMPLE_NULL_BREAKDOWN_ITEM_1["position"]
    assert null_breakdown_item.morpheme == EXAMPLE_NULL_BREAKDOWN_ITEM_1["morpheme"]
    assert (
        null_breakdown_item.submitted_by_user_email == EXAMPLE_NULL_BREAKDOWN_ITEM_1["submitted_by_user_email"]
    )


def test__verified_breakdown_action(word_id: int, db_service: DBService):

    ...
