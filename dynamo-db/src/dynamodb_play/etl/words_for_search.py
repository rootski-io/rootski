from typing import List

import rootski.services.database.models as orm
from dynamodb_play.etl.db_service import get_dbservice
from dynamodb_play.etl.utils import batch_load_into_dynamo
from dynamodb_play.models.word_for_search import WordForSearch
from rich.pretty import pprint


def extract() -> List[orm.Word]:

    db_service = get_dbservice()
    session = db_service.get_sync_session()
    words: List[orm.Word] = session.query(orm.Word).all()

    return words


def transform(words: List[orm.Word]) -> List[dict]:
    return [
        WordForSearch(
            word=word.word,
            word_id=str(word.id),
            pos=word.pos,
            frequency=word.frequency,
        ).to_item()
        for word in words
    ]


def load(dynamo_words: List[WordForSearch], batch_size: int):
    batch_load_into_dynamo(items=dynamo_words, batch_size=batch_size)


def etl():
    orm_words: List[orm.Word] = extract()
    dynamo_words: List[WordForSearch] = transform(words=orm_words)

    pprint(dynamo_words[:3])
    load(dynamo_words=dynamo_words, batch_size=500)


if __name__ == "__main__":
    etl()
