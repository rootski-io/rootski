from rootski.services.database.dynamo.models.breakdown import Breakdown
from rootski.services.database.dynamo.models.breakdown_item import make_dynamo_BreakdownItemItem_from_dict

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


EXAMPLE_BREAKDOWN_ITEM = {
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
    "pk": "WORD#162142",
    "sk": "BREAKDOWN_ITEM#37605e0f-3b37-4ead-a20e-7c8dbd167cfb#2",
    "__type": "BREAKDOWN_ITEM_NULL",
    "word_id": "162142",
    "position": "2",
    "morpheme": "тал",
    "morpheme_id": None,
    "family_id": None,
    "submitted_by_user_email": None,
}


EXAMPLE_NULL_BREAKDOWN_ITEM_2 = {
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


def test__verified_breakdown_action():
    ...
