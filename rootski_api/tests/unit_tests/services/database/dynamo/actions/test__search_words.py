from typing import List

import pytest
from mypy_boto3_dynamodb.service_resource import _Table
from rootski.services.database.dynamo.actions.search_words import search_words
from rootski.services.database.dynamo.db_service import DBService as DynamoDBService
from rootski.services.database.dynamo.models.word_for_search import WordForSearch

SEARCH_WORD_SEED_DATA = [
    {
        "sk": "вывернуть",
        "word": "вывернуть",
        "__type": "WORD_FOR_SEARCH",
        "word_id": "10506",
        "pk": "WORD",
    },
    {
        "sk": "выдернуть",
        "word": "выдернуть",
        "__type": "WORD_FOR_SEARCH",
        "word_id": "10891",
        "pk": "WORD",
    },
    {
        "sk": "выдвигаться",
        "word": "выдвигаться",
        "word_id": "11171",
        "__type": "WORD_FOR_SEARCH",
        "pk": "WORD",
    },
    {
        "sk": "dummy-word-1",
        "word": "dummy-word-1",
        "__type": "WORD_FOR_SEARCH",
        "word_id": "11257",
        "pk": "WORD",
    },
    {
        "sk": "dummy-word-2",
        "word": "dummy-word-2",
        "__type": "WORD_FOR_SEARCH",
        "word_id": "11283",
        "pk": "WORD",
    },
]


def fuzzy_equals(item: dict, model: WordForSearch) -> bool:
    from rich.pretty import pprint

    pprint(model)
    for field in ["pk", "sk", "word_id", "word", "__type"]:
        if item[field] != model.to_item()[field]:
            return False
    return True


@pytest.fixture
def seed_search_word_data(rootski_dynamo_table: _Table) -> None:
    for item in SEARCH_WORD_SEED_DATA:
        rootski_dynamo_table.put_item(Item=item)


def test__search_words(dynamo_db_service: DynamoDBService, seed_search_word_data: None):
    search_results: List[WordForSearch] = search_words(query="вы", limit=2, db=dynamo_db_service)
    assert len(search_results) == 2
    for word_for_search in search_results:
        assert word_for_search.word.startswith("вы")


def test__search_words__no_results(dynamo_db_service: DynamoDBService):
    search_results: List[WordForSearch] = search_words(query="вы", limit=2, db=dynamo_db_service)
    assert search_results == []
