from typing import List, Union

import rootski.services.database.dynamo.models as dynamo
from rootski.schemas import breakdown as schemas
from rootski.services.database.dynamo.actions.breakdown_actions import get_morpheme_families


def create_comma_separated_string_of_morphemes(morphemes_in_family: List[dict]):
    morphemes: List[str] = []
    for morpheme_item in morphemes_in_family:
        morphemes.append(morpheme_item["morpheme"])

    family_string = ",".join(morphemes)
    return family_string


def dynamo_to_pydantic__breakdown_item(
    dynamo_breakdown_item: Union[dynamo.NullBreakdownItem, dynamo.BreakdownItem]
) -> Union[schemas.NullMorphemeBreakdownItem, schemas.MorphemeBreakdownItemInResponse]:

    # If the conditional is true, then dynamo_breakdown_item is a NullBreakdownItem
    if dynamo_breakdown_item.morpheme_id is None:
        return schemas.NullMorphemeBreakdownItem(
            morpheme=dynamo_breakdown_item.morpheme,
            position=dynamo_breakdown_item.position,
            morpheme_id=None,
        )

    morpheme_family: dynamo.MorphemeFamily = get_morpheme_families(
        morpheme_family_id=dynamo_breakdown_item.morpheme_family_id,
        # db=
    )

    return schemas.MorphemeBreakdownItemInResponse(
        position=dynamo_breakdown_item["position"],
        morpheme=dynamo_breakdown_item["morpheme"],
        morpheme_id=dynamo_breakdown_item["morpheme_id"],
        family_id=dynamo_breakdown_item["morpheme_family_id"],
        family=create_comma_separated_string_of_morphemes(morpheme_family["morphemes"]),
        family_meanings=morpheme_family["family_meanings"],
        level=morpheme_family["level"],
        type=morpheme_family["type"],
        word_pos=morpheme_family["word_pos"],
    )


def dynamo_to_pydantic__null_breakdown_item(
    null_breakdown_item: dynamo.NullBreakdownItem,
) -> schemas.NullMorphemeBreakdownItem:
    return schemas.NullMorphemeBreakdownItem(
        morpheme=null_breakdown_item.morpheme,
        position=null_breakdown_item.position,
        morpheme_id=None,
    )


def dynamo_to_pydantic__breakdown_item(
    breakdown_item: dict,
    morpheme_family: dict,
) -> schemas.MorphemeBreakdownItemInResponse:
    return schemas.MorphemeBreakdownItemInResponse(
        position=breakdown_item["position"],
        morpheme=breakdown_item["morpheme"],
        morpheme_id=breakdown_item["morpheme_id"],
        family_id=breakdown_item["morpheme_family_id"],
        family=create_comma_separated_string_of_morphemes(morpheme_family["morphemes"]),
        family_meanings=morpheme_family["family_meanings"],
        level=morpheme_family["level"],
        type=morpheme_family["type"],
        word_pos=morpheme_family["word_pos"],
    )
