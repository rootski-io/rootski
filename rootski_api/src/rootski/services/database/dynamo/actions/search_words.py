from typing import List

from boto3.dynamodb.conditions import Key
from mypy_boto3_dynamodb.type_defs import QueryOutputTableTypeDef
from rootski.services.database.dynamo.actions.dynamo import get_items_from_dynamo_query_response
from rootski.services.database.dynamo.db_service import DBService
from rootski.services.database.dynamo.models import word_for_search


def search_words(query: str, limit: int, db: DBService) -> List[word_for_search.WordForSearch]:
    """Query a word from Dynamo matching the ``word_id``.

    :raises WordNotFoundError: raised if no word exists with the given ``word_id``.
    """
    table = db.rootski_table

    query_response: QueryOutputTableTypeDef = table.query(
        KeyConditionExpression=Key("pk").eq(word_for_search.make_pk()) & Key("sk").begins_with(query),
        Limit=limit,
    )
    # if get_item_status_code(item_output=get_item_response) == 404:
    #     raise WordNotFoundError(f"No word with ID {word_id} was found in Dynamo.")

    items: List[dict] = get_items_from_dynamo_query_response(query_response)
    search_results: List[word_for_search.WordForSearch] = [
        word_for_search.WordForSearch(
            frequency=item.get("frequency", -1),
            pos="deprecated",
            word_id=item["word_id"],
            word=item["word"],
        )
        for item in items
    ]

    return search_results
