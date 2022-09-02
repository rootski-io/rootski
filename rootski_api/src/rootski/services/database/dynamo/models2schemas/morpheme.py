
import rootski.services.database.dynamo.models as dynamo
from rootski.schemas import morpheme as schemas


def dynamo_to_pydantic__complete_morpheme(dynamo_morpheme: dynamo.Morpheme) -> schemas.CompleteMorpheme:
    return schemas.CompleteMorpheme(
        morpheme_id=int(dynamo_morpheme.morpheme_id),
        morpheme=dynamo_morpheme.morpheme,
        family_id=int(dynamo_morpheme.family_id),
    )
