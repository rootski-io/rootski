from rootski.services.database.dynamo.actions.breakdown_actions import (
    get_breakdown_submitted_by_user_email_and_word_id,
    get_morpheme_family,
    get_official_breakdown_by_word_id,
    get_official_breakdown_submitted_by_another_user,
    is_breakdown_verified,
)
from rootski.services.database.dynamo.db_service import DBService
from rootski.services.database.dynamo.models.breakdown import Breakdown
from rootski.services.database.dynamo.models.breakdown_item import make_dynamo_breakdown_item_from_dict
from rootski.services.database.dynamo.models.morpheme_family import MorphemeFamily
from tests.fixtures.seed_data import (
    EXAMPLE_BREAKDOWN,
    EXAMPLE_BREAKDOWN_57,
    EXAMPLE_BREAKDOWN_ANOTHER_USER,
    EXAMPLE_BREAKDOWN_ERIC_USER,
    EXAMPLE_BREAKDOWN_ITEM_1,
    EXAMPLE_DATA,
    EXAMPLE_MORPHEME_FAMILY_245,
    EXAMPLE_MORPHEME_FAMILY_1385,
    EXAMPLE_NULL_BREAKDOWN_ITEM_1,
    seed_data,
)

# from rootski_api.tests.fixtures.rootski_dynamo_table import rootski_dynamo_table, dynamo_db_service
# from rootski.services.database.dynamo.models2schemas.word import dynamo_to_pydantic__word
# from rootski.services.database.dynamo.actions.dynamo import get_item_from_dynamo_response, get_item_status_code
# from rootski import schemas


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

    # Fix this test for the remaining breakdown items

    # breakdown_items = [
    #     make_dynamo_BreakdownItemItem_from_dict(breakdown_item)
    #     for breakdown_item in EXAMPLE_DATA[BREAKDOWN_INDEX]["breakdown_items"]
    # ]

    # assert breakdown.breakdown_items == breakdown_items


def test__breakdown_item_from_dict():
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

    # Breakdown Item
    breakdown_item = make_dynamo_breakdown_item_from_dict(breakdown_item_dict=EXAMPLE_BREAKDOWN_ITEM_1)
    assert breakdown_item.word_id == EXAMPLE_BREAKDOWN_ITEM_1["word_id"]
    assert breakdown_item.position == EXAMPLE_BREAKDOWN_ITEM_1["position"]
    assert breakdown_item.morpheme == EXAMPLE_BREAKDOWN_ITEM_1["morpheme"]
    assert breakdown_item.submitted_by_user_email == EXAMPLE_BREAKDOWN_ITEM_1["submitted_by_user_email"]
    assert breakdown_item.morpheme_id == EXAMPLE_BREAKDOWN_ITEM_1["morpheme_id"]
    assert breakdown_item.morpheme_family_id == EXAMPLE_BREAKDOWN_ITEM_1["morpheme_family_id"]
    assert breakdown_item.breakdown_id == EXAMPLE_BREAKDOWN_ITEM_1["breakdown_id"]


def test__get_official_breakdown_by_word_id(dynamo_db_service: DBService):
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    word_id = "32"

    breakdown: Breakdown = get_official_breakdown_by_word_id(word_id=word_id, db=dynamo_db_service)
    assert breakdown.word == EXAMPLE_BREAKDOWN["word"]
    assert breakdown.is_verified == EXAMPLE_BREAKDOWN["is_verified"]


def test__is_breakdown_verified(dynamo_db_service: DBService):
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    word_id = "32"

    breakdown: Breakdown = get_official_breakdown_by_word_id(word_id=word_id, db=dynamo_db_service)
    assert is_breakdown_verified(breakdown=breakdown) is False


def test__get_breakdown_submitted_by_user_email_and_word_id(dynamo_db_service: DBService):
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    user_email = "eric.riddoch@gmail.com"
    word_id = "5"

    breakdown: Breakdown = get_breakdown_submitted_by_user_email_and_word_id(
        user_email=user_email, word_id=word_id, db=dynamo_db_service
    )
    assert breakdown.word_id == EXAMPLE_BREAKDOWN_ERIC_USER["word_id"]
    assert breakdown.submitted_by_user_email == user_email
    assert breakdown.submitted_by_user_email != "anonymous"
    assert breakdown.submitted_by_user_email != "another_user@gmail.com"


def test__get_official_breakdown_submitted_by_another_user(dynamo_db_service: DBService) -> Breakdown:
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    word_id = "10"
    user_email = "eric.riddoch@gmail.com"

    breakdown: Breakdown = get_official_breakdown_submitted_by_another_user(
        word_id=word_id, db=dynamo_db_service
    )
    assert breakdown.submitted_by_user_email == EXAMPLE_BREAKDOWN_ANOTHER_USER["submitted_by_user_email"]
    assert breakdown.submitted_by_user_email != user_email
    assert breakdown.submitted_by_user_email != "anonymous"
    assert breakdown.submitted_by_user_email != "null"


def test__get_morpheme_family(dynamo_db_service: DBService) -> MorphemeFamily:
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    morpheme_family_id = "245"

    morpheme_family: MorphemeFamily = get_morpheme_family(
        morpheme_family_id=morpheme_family_id, db=dynamo_db_service
    )

    assert morpheme_family.family_id == morpheme_family_id
    assert morpheme_family.family_meanings == EXAMPLE_MORPHEME_FAMILY_245["family_meanings"]
