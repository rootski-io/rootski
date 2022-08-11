from rootski.services.database.dynamo.actions.verified_breakdown import (
    get_official_breakdown_by_word_id,
    is_verified,
)
from rootski.services.database.dynamo.db_service import DBService
from rootski.services.database.dynamo.models.breakdown import Breakdown
from rootski.services.database.dynamo.models.breakdown_item import make_dynamo_breakdown_item_from_dict
from tests.fixtures.seed_data import EXAMPLE_DATA, seed_data

# from  rootski_api.tests.fixtures.rootski_dynamo_table import rootski_dynamo_table, dynamo_db_service

# from rootski.services.database.dynamo.models2schemas.word import dynamo_to_pydantic__word
# from rootski.services.database.dynamo.actions.dynamo import get_item_from_dynamo_response, get_item_status_code
# from rootski import schemas

# Constants
BREAKDOWN_INDEX = 0
BREAKDOWN_VERIFIED_INDEX = 2
BREAKDOWN_ITEM_INDEX = 3
BREAKDOWN_ITEM_NULL_INDEX = 4


def test__breakdown_from_dict():

    breakdown = Breakdown.from_dict(breakdown_dict=EXAMPLE_DATA[BREAKDOWN_INDEX])

    assert breakdown.pk == EXAMPLE_DATA[BREAKDOWN_INDEX]["pk"]
    assert breakdown.sk == EXAMPLE_DATA[BREAKDOWN_INDEX]["sk"]
    assert breakdown.gsi1pk == EXAMPLE_DATA[BREAKDOWN_INDEX]["gsi1pk"]
    assert breakdown.gsi1sk == EXAMPLE_DATA[BREAKDOWN_INDEX]["gsi1sk"]
    assert breakdown.gsi2pk == EXAMPLE_DATA[BREAKDOWN_INDEX]["gsi2pk"]
    assert breakdown.gsi2sk == EXAMPLE_DATA[BREAKDOWN_INDEX]["gsi2sk"]
    assert breakdown.word == EXAMPLE_DATA[BREAKDOWN_INDEX]["word"]
    assert breakdown.word_id == EXAMPLE_DATA[BREAKDOWN_INDEX]["word_id"]
    assert breakdown.submitted_by_user_email == EXAMPLE_DATA[BREAKDOWN_INDEX]["submitted_by_user_email"]
    assert breakdown.is_verified == EXAMPLE_DATA[BREAKDOWN_INDEX]["is_verified"]
    assert breakdown.is_inference == EXAMPLE_DATA[BREAKDOWN_INDEX]["is_inference"]
    assert breakdown.date_submitted == EXAMPLE_DATA[BREAKDOWN_INDEX]["date_submitted"]
    assert breakdown.date_verified == EXAMPLE_DATA[BREAKDOWN_INDEX]["date_verified"]

    # Fix this test for the remaining breakdown items

    # breakdown_items = [
    #     make_dynamo_BreakdownItemItem_from_dict(breakdown_item)
    #     for breakdown_item in EXAMPLE_DATA[BREAKDOWN_INDEX]["breakdown_items"]
    # ]

    # assert breakdown.breakdown_items == breakdown_items


def test__breakdown_item_from_dict():
    # Null breakdown item
    null_breakdown_item = make_dynamo_breakdown_item_from_dict(
        breakdown_item_dict=EXAMPLE_DATA[BREAKDOWN_ITEM_NULL_INDEX]
    )
    assert null_breakdown_item.word_id == EXAMPLE_DATA[BREAKDOWN_ITEM_NULL_INDEX]["word_id"]
    assert null_breakdown_item.position == EXAMPLE_DATA[BREAKDOWN_ITEM_NULL_INDEX]["position"]
    assert null_breakdown_item.morpheme == EXAMPLE_DATA[BREAKDOWN_ITEM_NULL_INDEX]["morpheme"]
    assert (
        null_breakdown_item.submitted_by_user_email
        == EXAMPLE_DATA[BREAKDOWN_ITEM_NULL_INDEX]["submitted_by_user_email"]
    )

    # Breakdown Item
    breakdown_item = make_dynamo_breakdown_item_from_dict(
        breakdown_item_dict=EXAMPLE_DATA[BREAKDOWN_ITEM_INDEX]
    )
    assert breakdown_item.word_id == EXAMPLE_DATA[BREAKDOWN_ITEM_INDEX]["word_id"]
    assert breakdown_item.position == EXAMPLE_DATA[BREAKDOWN_ITEM_INDEX]["position"]
    assert breakdown_item.morpheme == EXAMPLE_DATA[BREAKDOWN_ITEM_INDEX]["morpheme"]
    assert (
        breakdown_item.submitted_by_user_email == EXAMPLE_DATA[BREAKDOWN_ITEM_INDEX]["submitted_by_user_email"]
    )
    assert breakdown_item.morpheme_id == EXAMPLE_DATA[BREAKDOWN_ITEM_INDEX]["morpheme_id"]
    assert breakdown_item.morpheme_family_id == EXAMPLE_DATA[BREAKDOWN_ITEM_INDEX]["morpheme_family_id"]
    assert breakdown_item.breakdown_id == EXAMPLE_DATA[BREAKDOWN_ITEM_INDEX]["breakdown_id"]


def test__get_official_breakdown_by_word_id(dynamo_db_service: DBService):
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    breakdown = get_official_breakdown_by_word_id(word_id="32", db=dynamo_db_service)
    assert breakdown.word == EXAMPLE_DATA[BREAKDOWN_INDEX]["word"]
    assert breakdown.is_verified == EXAMPLE_DATA[BREAKDOWN_INDEX]["is_verified"]


def test__is_verified(dynamo_db_service: DBService):
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    breakdown = get_official_breakdown_by_word_id(word_id="32", db=dynamo_db_service)
    assert is_verified(breakdown=breakdown) is False


# if __name__ == "__main__":
#     db = DBService("rootski-table")
#     db.init()
#     table = db.rootski_table
#     get_item_response = table.get_item(
#         Key={"pk": "WORD#771", "sk": "BREAKDOWN_ITEM#2213#0"}
#     )  # eric.riddoch@gmail.com"})
#     print(get_item_response["Item"])
