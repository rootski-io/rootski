from rootski.services.database.dynamo.actions.verified_breakdown import (
    get_official_breakdown_by_word_id,
    is_verified,
)
from rootski.services.database.dynamo.db_service import DBService
from rootski.services.database.dynamo.models.breakdown import Breakdown
from rootski.services.database.dynamo.models.breakdown_item import (
    make_dynamo_breakdown_item_from_dict,
    make_dynamo_BreakdownItemItem_from_dict,
)
from tests.fixtures.seed_data import seed_data

# from  rootski_api.tests.fixtures.rootski_dynamo_table import rootski_dynamo_table, dynamo_db_service

# from rootski.services.database.dynamo.models2schemas.word import dynamo_to_pydantic__word
# from rootski.services.database.dynamo.actions.dynamo import get_item_from_dynamo_response, get_item_status_code
# from rootski import schemas


def test__breakdown_from_dict():
    breakdown = Breakdown.from_dict(breakdown_dict=EXAMPLE_BREAKDOWN_2)

    assert breakdown.pk == EXAMPLE_BREAKDOWN_2["pk"]
    assert breakdown.sk == EXAMPLE_BREAKDOWN_2["sk"]
    assert breakdown.gsi1pk == EXAMPLE_BREAKDOWN_2["gsi1pk"]
    assert breakdown.gsi1sk == EXAMPLE_BREAKDOWN_2["gsi1sk"]
    assert breakdown.gsi2pk == EXAMPLE_BREAKDOWN_2["gsi2pk"]
    assert breakdown.gsi2sk == EXAMPLE_BREAKDOWN_2["gsi2sk"]
    assert breakdown.word == EXAMPLE_BREAKDOWN_2["word"]
    assert breakdown.word_id == EXAMPLE_BREAKDOWN_2["word_id"]
    assert breakdown.submitted_by_user_email == EXAMPLE_BREAKDOWN_2["submitted_by_user_email"]
    assert breakdown.is_verified == EXAMPLE_BREAKDOWN_2["is_verified"]
    assert breakdown.is_inference == EXAMPLE_BREAKDOWN_2["is_inference"]
    assert breakdown.date_submitted == EXAMPLE_BREAKDOWN_2["date_submitted"]
    assert breakdown.date_verified == EXAMPLE_BREAKDOWN_2["date_verified"]

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


def test__verified_breakdown_action():
    assert is_verified(EXAMPLE_BREAKDOWN) == False
    assert is_verified(EXAMPLE_VERIFiED_BREAKDOWN) == True


def test__get_official_breakdown_by_word_id(dynamo_db_service: DBService):
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    breakdown = get_official_breakdown_by_word_id(word_id="32", db=dynamo_db_service)
    print(breakdown)
    assert False


if __name__ == "__main__":
    db = DBService("rootski-table")
    db.init()
    table = db.rootski_table
    get_item_response = table.get_item(
        Key={"pk": "WORD#771", "sk": "BREAKDOWN_ITEM#2213#0"}
    )  # eric.riddoch@gmail.com"})
    print(get_item_response["Item"])
