# from rootski.services.database.dynamo.db_service import DBService
from rootski.schemas import breakdown as schemas
from rootski.services.database.dynamo.actions.breakdown_actions import get_morpheme_families
from rootski.services.database.dynamo.db_service import DBService
from rootski.services.database.dynamo.models2schemas.breakdown_item import (
    create_comma_separated_string_of_morphemes,
    dynamo_to_pydantic__breakdown_item,
    dynamo_to_pydantic__null_breakdown_item,
)
from rootski.services.database.dynamo.models.breakdown import Breakdown
from tests.fixtures.seed_data import (
    EXAMPLE_BREAKDOWN,
    EXAMPLE_BREAKDOWN_2,
    EXAMPLE_BREAKDOWN_57,
    EXAMPLE_BREAKDOWN_ANOTHER_USER,
    EXAMPLE_BREAKDOWN_ERIC_USER,
    EXAMPLE_BREAKDOWN_ITEM,
    EXAMPLE_MORPHEME_FAMILY_245,
    EXAMPLE_MORPHEME_FAMILY_1385,
    EXAMPLE_NULL_BREAKDOWN_ITEM,
    seed_data,
)


def test__create_comma_separated_string_of_morphemes():
    test_answer = "знай,зна"
    family_string = create_comma_separated_string_of_morphemes(EXAMPLE_MORPHEME_FAMILY_245["morphemes"])
    assert family_string == test_answer


# def test__dynamo_to_pydantic__null_breakdown_item() -> schemas.NullMorphemeBreakdownItem:
#     null_breakdown_item = dynamo_to_pydantic__null_breakdown_item(EXAMPLE_NULL_BREAKDOWN_ITEM)
#     assert null_breakdown_item.position == EXAMPLE_NULL_BREAKDOWN_ITEM["position"]
#     assert null_breakdown_item.morpheme == EXAMPLE_NULL_BREAKDOWN_ITEM["morpheme"]
#     assert null_breakdown_item.morpheme_id == EXAMPLE_NULL_BREAKDOWN_ITEM["morpheme_id"]


def test__dynamo_to_pydantic__breakdown_item() -> schemas.MorphemeBreakdownItemInResponse:
    breakdown_item = EXAMPLE_BREAKDOWN_ITEM
    morpheme_family = EXAMPLE_MORPHEME_FAMILY_245

    breakdown_item_response = dynamo_to_pydantic__breakdown_item(
        breakdown_item=breakdown_item, morpheme_family=morpheme_family
    )

    assert breakdown_item_response.position == EXAMPLE_BREAKDOWN_ITEM["position"]
    assert breakdown_item_response.morpheme == EXAMPLE_BREAKDOWN_ITEM["morpheme"]
    assert breakdown_item_response.morpheme_id == int(EXAMPLE_BREAKDOWN_ITEM["morpheme_id"])
    assert breakdown_item_response.family_id == int(EXAMPLE_BREAKDOWN_ITEM["morpheme_family_id"])
    assert breakdown_item_response.family == create_comma_separated_string_of_morphemes(
        EXAMPLE_MORPHEME_FAMILY_245["morphemes"]
    )
    assert breakdown_item_response.family_meanings == EXAMPLE_MORPHEME_FAMILY_245["family_meanings"]
    assert breakdown_item_response.level == EXAMPLE_MORPHEME_FAMILY_245["level"]
    assert breakdown_item_response.word_pos == EXAMPLE_MORPHEME_FAMILY_245["word_pos"]


def test__dynamo_to_pydantic__breakdown(dynamo_db_service: DBService):
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    dynamo_breakdown_model = Breakdown.from_dict(EXAMPLE_BREAKDOWN_57)
    morpheme_family_dict = get_morpheme_families(
        breakdown=dynamo_breakdown_model,
        db=dynamo_db_service,
    )
