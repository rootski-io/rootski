from rootski.services.database.dynamo.actions.breakdown_actions import (
    get_breakdown_submitted_by_user_email_and_word_id,
    get_morpheme_families,
    get_official_breakdown_by_word_id,
    get_official_breakdown_submitted_by_another_user,
    is_breakdown_verified,
)
from rootski.services.database.dynamo.db_service import DBService
from rootski.services.database.dynamo.models.breakdown import Breakdown
from rootski.services.database.dynamo.models.breakdown_item import make_dynamo_breakdown_item_from_dict
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


def test__breakdown_from_dict():
    SEED_BREAKDOWN = EXAMPLE_BREAKDOWN_2
    breakdown = Breakdown.from_dict(breakdown_dict=SEED_BREAKDOWN)

    assert breakdown.pk == SEED_BREAKDOWN["pk"]
    assert breakdown.sk == SEED_BREAKDOWN["sk"]
    assert breakdown.gsi1pk == SEED_BREAKDOWN["gsi1pk"]
    assert breakdown.gsi1sk == SEED_BREAKDOWN["gsi1sk"]
    assert breakdown.gsi2pk == SEED_BREAKDOWN["gsi2pk"]
    assert breakdown.gsi2sk == SEED_BREAKDOWN["gsi2sk"]
    assert breakdown.word == SEED_BREAKDOWN["word"]
    assert breakdown.word_id == SEED_BREAKDOWN["word_id"]
    assert breakdown.submitted_by_user_email == SEED_BREAKDOWN["submitted_by_user_email"]
    assert breakdown.is_verified == SEED_BREAKDOWN["is_verified"]
    assert breakdown.is_inference == SEED_BREAKDOWN["is_inference"]
    assert breakdown.date_submitted == SEED_BREAKDOWN["date_submitted"]
    assert breakdown.date_verified == SEED_BREAKDOWN["date_verified"]

    for index, breakdown_item in enumerate(breakdown.breakdown_items):
        assert breakdown_item == SEED_BREAKDOWN["breakdown_items"][index]


def test__breakdown_item_from_dict():
    # Null breakdown item
    null_breakdown_item = make_dynamo_breakdown_item_from_dict(breakdown_item_dict=EXAMPLE_NULL_BREAKDOWN_ITEM)
    assert null_breakdown_item.word_id == EXAMPLE_NULL_BREAKDOWN_ITEM["word_id"]
    assert null_breakdown_item.position == EXAMPLE_NULL_BREAKDOWN_ITEM["position"]
    assert null_breakdown_item.morpheme == EXAMPLE_NULL_BREAKDOWN_ITEM["morpheme"]
    assert null_breakdown_item.submitted_by_user_email == EXAMPLE_NULL_BREAKDOWN_ITEM["submitted_by_user_email"]

    # Breakdown Item
    breakdown_item = make_dynamo_breakdown_item_from_dict(breakdown_item_dict=EXAMPLE_BREAKDOWN_ITEM)
    assert breakdown_item.word_id == EXAMPLE_BREAKDOWN_ITEM["word_id"]
    assert breakdown_item.position == EXAMPLE_BREAKDOWN_ITEM["position"]
    assert breakdown_item.morpheme == EXAMPLE_BREAKDOWN_ITEM["morpheme"]
    assert breakdown_item.submitted_by_user_email == EXAMPLE_BREAKDOWN_ITEM["submitted_by_user_email"]
    assert breakdown_item.morpheme_id == EXAMPLE_BREAKDOWN_ITEM["morpheme_id"]
    assert breakdown_item.morpheme_family_id == EXAMPLE_BREAKDOWN_ITEM["morpheme_family_id"]
    assert breakdown_item.breakdown_id == EXAMPLE_BREAKDOWN_ITEM["breakdown_id"]


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


def test__get_official_breakdown_submitted_by_another_user(dynamo_db_service: DBService):
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


def test__get_morpheme_families(dynamo_db_service: DBService):
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    dynamo_breakdown_model = Breakdown.from_dict(EXAMPLE_BREAKDOWN_57)
    morpheme_family_dict = get_morpheme_families(
        breakdown=dynamo_breakdown_model,
        db=dynamo_db_service,
    )
    assert morpheme_family_dict["245"].family_id == EXAMPLE_MORPHEME_FAMILY_245["family_id"]
    assert morpheme_family_dict["1385"].family_id == EXAMPLE_MORPHEME_FAMILY_1385["family_id"]
