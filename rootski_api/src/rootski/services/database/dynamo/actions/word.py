from rootski.services.database.dynamo.actions.dynamo import get_item_from_dynamo_response, get_item_status_code
from rootski.services.database.dynamo.db_service import DBService
from rootski.services.database.dynamo.models import word


class WordNotFoundError(Exception):
    """Error thrown if a word isn't found."""


def get_word_by_id(word_id: str, db: DBService) -> word.Word:
    """Query a word from Dynamo matching the ``word_id``.

    :raises WordNotFoundError: raised if no word exists with the given ``word_id``.
    """
    table = db.rootski_table
    word_dynamo_keys: dict = word.make_keys(word_id=word_id)

    get_item_response = table.get_item(Key=word_dynamo_keys)
    if get_item_status_code(item_output=get_item_response) == 404:
        raise WordNotFoundError(f"No word with ID {word_id} was found in Dynamo.")

    item = get_item_from_dynamo_response(get_item_response)
    word_ = word.Word(data=item)
    return word_
