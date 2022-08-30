from typing import Dict, List, Union

import rootski.services.database.dynamo.models as dynamo
from rootski.schemas import breakdown as schemas


def create_comma_separated_string_of_morphemes(morphemes_in_family: List[dynamo.MorphemeItem]) -> str:
    morphemes: List[str] = []
    for morpheme_item in morphemes_in_family:
        morphemes.append(morpheme_item["morpheme"])

    family_string: str = ",".join(morphemes)
    return family_string


def dynamo_to_pydantic__breakdown_item(
    breakdown_item_item: dynamo.BreakdownItemItem,
    morpheme_family_dict: Dict[str, dynamo.MorphemeFamily],
) -> Union[schemas.NullMorphemeBreakdownItem, schemas.MorphemeBreakdownItemInResponse]:

    # If the conditional is true, then dynamo_breakdown_item is a NullBreakdownItem
    if breakdown_item_item["morpheme_id"] is None:
        return schemas.NullMorphemeBreakdownItem(
            morpheme=breakdown_item_item["morpheme"],
            position=breakdown_item_item["position"],
            morpheme_id=None,
        )

    morpheme_family: dynamo.MorphemeFamily = morpheme_family_dict[breakdown_item_item["morpheme_family_id"]]

    return schemas.MorphemeBreakdownItemInResponse(
        position=breakdown_item_item["position"],
        morpheme=breakdown_item_item["morpheme"],
        morpheme_id=breakdown_item_item["morpheme_id"],
        family_id=breakdown_item_item["morpheme_family_id"],
        family=create_comma_separated_string_of_morphemes(morpheme_family.morphemes),
        family_meanings=[] if morpheme_family.family_meanings == [None] else morpheme_family.family_meanings,
        level=morpheme_family.level,
        type=morpheme_family.type,
        word_pos=morpheme_family.word_pos,
    )
