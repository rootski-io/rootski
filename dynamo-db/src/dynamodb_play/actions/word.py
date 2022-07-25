from typing import Optional
from dynamodb_play.dynamo import get_rootski_dynamo_table
from dynamodb_play.models.word import Word

from mypy_boto3_dynamodb.service_resource import _Table


def get_word_by_id(word_id: str) -> Optional[dict]:
    table: _Table = get_rootski_dynamo_table()
    _word = Word(word_id=word_id)
    result = table.get_item(Key=_word.keys)

    if "Item" in result.keys():
        return result["Item"]

    return None
