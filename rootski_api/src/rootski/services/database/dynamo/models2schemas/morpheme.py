from typing import Dict

import rootski.services.database.dynamo.models as dynamo
from rootski.schemas import morpheme as schemas


def dynamo_to_pydantic__complete_morpheme(
    dynamo_morpheme_obj: dynamo.Morpheme,
    ids_to_morpheme_families: Dict[str, dynamo.MorphemeFamily],
    morpheme_id: str,
) -> schemas.CompleteMorpheme:
    return schemas.CompleteMorpheme(
        morpheme_id=int(dynamo_morpheme_obj.morpheme_id),
        morpheme=dynamo_morpheme_obj.morpheme,
        family_id=int(dynamo_morpheme_obj.family_id),
        type=ids_to_morpheme_families[morpheme_id]["type"],
        word_pos=ids_to_morpheme_families[morpheme_id]["word_pos"],
        meanings=ids_to_morpheme_families[morpheme_id]["meanings"],
        level=ids_to_morpheme_families[morpheme_id]["level"],
        family=ids_to_morpheme_families[morpheme_id]["family"],
    )
