from typing import List

import pytest
from fastapi.testclient import TestClient
from mypy_boto3_dynamodb.service_resource import _Table
from rootski.services.database.dynamo.models.word_for_search import WordForSearch

from rootski import schemas

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


@pytest.mark.parametrize(
    "disable_auth, act_as_admin",
    [
        (
            True,
            True,
        ),
        (
            True,
            False,
        ),
    ],
)
def test__search(dynamo_client: TestClient, seed_search_word_data: None):
    response = dynamo_client.get("/search/вы")
    search_results: List[schemas.SearchWord] = [schemas.SearchWord(**item) for item in response.json()["words"]]
    assert len(search_results) > 0
    for item in search_results:
        assert item.word.startswith("вы")


@pytest.mark.parametrize(
    "disable_auth, act_as_admin",
    [
        (
            True,
            True,
        ),
        (
            True,
            False,
        ),
    ],
)
def test__search__no_results(dynamo_client: TestClient, seed_search_word_data: None):
    response = dynamo_client.get("/search/bogus! ... heinous!! ... most *non* triumphant!")
    search_results = response.json()["words"]
    assert search_results == []
