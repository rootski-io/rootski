import rootski.schemas.search as schemas
from rootski.services.database.dynamo.models.word_for_search import WordForSearch


def dynamo_to_pydantic__word_for_search(model: WordForSearch) -> schemas.SearchWord:
    return schemas.SearchWord(
        frequency=model.frequency,
        pos=model.pos,
        word_id=model.word_id,
        word=model.word,
    )
