from typing import Dict, List, Union

import rootski.services.database.dynamo.models as dynamo
from rootski.schemas import breakdown as schemas
from rootski.services.database.dynamo.actions.breakdown_actions import get_morpheme_families
from rootski.services.database.dynamo.db_service import DBService
from rootski.services.database.dynamo.models2schemas.breakdown import dynamo_to_pydantic__breakdown
from rootski.services.database.dynamo.models2schemas.breakdown_item import (
    create_comma_separated_string_of_morphemes,
    dynamo_to_pydantic__breakdown_item,
)
from tests.fixtures.seed_data import (
    EXAMPLE_BREAKDOWN_W_MORPHEME_FAMILIES_IN_DB,
    EXAMPLE_MORPHEME_FAMILY_245,
    seed_data,
)


def test__create_comma_separated_string_of_morphemes():
    test_answer = "знай,зна"
    family_string = create_comma_separated_string_of_morphemes(EXAMPLE_MORPHEME_FAMILY_245["morphemes"])
    assert family_string == test_answer


def test__dynamo_to_pydantic__breakdown_item(dynamo_db_service: DBService):
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    TEST_DATA: dict = EXAMPLE_BREAKDOWN_W_MORPHEME_FAMILIES_IN_DB
    dynamo_breakdown_model = dynamo.Breakdown.from_dict(TEST_DATA)
    morpheme_family_dict: Dict[str, dynamo.MorphemeFamily] = get_morpheme_families(
        breakdown=dynamo_breakdown_model,
        db=dynamo_db_service,
    )
    breakdown_items: List[Union[schemas.NullMorphemeBreakdownItem, schemas.MorphemeBreakdownItemInResponse]] = [
        dynamo_to_pydantic__breakdown_item(
            breakdown_item_item=breakdown_item,
            morpheme_family_data=morpheme_family_dict,
        )
        for breakdown_item in dynamo_breakdown_model.breakdown_items
    ]
    breakdown_item: Union[
        schemas.NullMorphemeBreakdownItem, schemas.MorphemeBreakdownItemInResponse
    ] = breakdown_items[0]

    if breakdown_item.morpheme_id is None:
        assert breakdown_item.morpheme == dynamo_breakdown_model.breakdown_items[0].morpheme
        assert breakdown_item.position == dynamo_breakdown_model.breakdown_items[0].position
    else:
        morpheme_family_id: str = str(breakdown_item.family_id)
        morpheme_family: dynamo.MorphemeFamily = morpheme_family_dict[morpheme_family_id]

        assert breakdown_item.morpheme == dynamo_breakdown_model.breakdown_items[0]["morpheme"]
        assert breakdown_item.morpheme_id == int(dynamo_breakdown_model.breakdown_items[0]["morpheme_id"])
        assert breakdown_item.family_id == int(dynamo_breakdown_model.breakdown_items[0]["morpheme_family_id"])
        assert breakdown_item.position == dynamo_breakdown_model.breakdown_items[0]["position"]
        assert breakdown_item.level == morpheme_family.level
        assert breakdown_item.word_pos == morpheme_family.word_pos
        assert breakdown_item.type == morpheme_family.type
        assert breakdown_item.family_meanings == morpheme_family.family_meanings
        assert breakdown_item.family == create_comma_separated_string_of_morphemes(morpheme_family.morphemes)


def test__dynamo_to_pydantic__breakdown(dynamo_db_service: DBService):
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    TEST_DATA: dict = EXAMPLE_BREAKDOWN_W_MORPHEME_FAMILIES_IN_DB
    dynamo_breakdown_model: dynamo.Breakdown = dynamo.Breakdown.from_dict(TEST_DATA)
    morpheme_family_dict: Dict[str, dynamo.MorphemeFamily] = get_morpheme_families(
        breakdown=dynamo_breakdown_model,
        db=dynamo_db_service,
    )
    USER_EMAIL: str = "another_user@gmail.com"

    # pprint(datetime.isoformat())
    # pprint(datetime.strptime())
    pydantic_breakdown: schemas.GetBreakdownResponse = dynamo_to_pydantic__breakdown(
        breakdown=dynamo_breakdown_model,
        ids_to_morpheme_families=morpheme_family_dict,
        user_email=USER_EMAIL,
    )
    if dynamo_breakdown_model.is_inference is True:
        assert pydantic_breakdown.submitted_by_current_user is False
    assert pydantic_breakdown.word == dynamo_breakdown_model.word
    assert pydantic_breakdown.word_id == int(dynamo_breakdown_model.word_id)
    assert str(pydantic_breakdown.date_submitted) == dynamo_breakdown_model.date_submitted
    assert str(pydantic_breakdown.date_verified) == dynamo_breakdown_model.date_verified
    assert pydantic_breakdown.is_inference == dynamo_breakdown_model.is_inference
    assert pydantic_breakdown.is_verified == dynamo_breakdown_model.is_verified
