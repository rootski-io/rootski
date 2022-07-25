from functools import reduce
from typing import Generator, List

import rootski.services.database.models as orm
from dynamodb_play.dynamo import get_rootski_dynamo_table
from dynamodb_play.etl.db_service import get_dbservice
from dynamodb_play.models.morpheme import Morpheme
from dynamodb_play.models.morpheme_family import MorphemeFamily, MorphemeItem
from rich.pretty import pprint
from sqlalchemy.orm import joinedload


def make_dynamo_morpheme_family_from_orm(orm_family: orm.MorphemeFamily) -> MorphemeFamily:
    """
    Build a ``MorphemeFamily`` object from a SQLAlchemy ``orm.MorphemeFamily`` object.

    The resulting object has data organized in the way it is intended to end up in dynamo.
    """
    orm_morphemes: List[orm.Morpheme] = orm_family.morphemes
    orm_meanings: List[orm.MorphemeFamilyMeaning] = orm_family.meanings

    return MorphemeFamily(
        family_id=str(orm_family.id),
        level=orm_family.level,
        word_pos=orm_morphemes[0].word_pos,
        type=orm_morphemes[0].type,
        morphemes=[
            MorphemeItem(
                morpheme=m.morpheme,
                morpheme_id=str(m.morpheme_id),
            )
            for m in orm_morphemes
        ],
        family_meanings=[m.meaning for m in orm_meanings],
    )


def batch_etl_morphemes_from_postgres_to_dynamo():

    # query and serialize all MorphemeFamily and their Morpheme objects from postgres
    morpheme_items: List[dict] = query_morpheme_items_from_postgres()

    print("families")
    pprint(morpheme_items[:3])

    print("morphemes")
    pprint(morpheme_items[::-1][:3])

    # write 50 dicts at a time to dynamo
    table = get_rootski_dynamo_table()
    for batch_index, batch in enumerate(batchify(morpheme_items, batch_size=50)):
        print(f"Writing batch {batch_index} to dynamo")
        with table.batch_writer() as batch_writer:
            for item in batch:
                batch_writer.put_item(item)


def query_morpheme_items_from_postgres() -> List[dict]:

    # connect to an instance of the rootski postgres database running locally
    db_service = get_dbservice()
    session = db_service.get_sync_session()

    # query all of the MorphemeFamily rows from postgres, eagerloading the "morphemes" and "family_meanings"
    # with "LEFT OUTER JOIN"s on the query
    m_families_orm: List[orm.MorphemeFamily] = (
        session.query(orm.MorphemeFamily)
        .options(
            joinedload(orm.MorphemeFamily.morphemes),
            joinedload(orm.MorphemeFamily.meanings),
        )
        .all()
    )

    # convert the SQLAlchemy "orm.MorphemeFamily" models to dicts meant for dynamo
    m_families: List[MorphemeFamily] = [make_dynamo_morpheme_family_from_orm(f) for f in m_families_orm]
    m_family_items: List[dict] = [m.to_item() for m in m_families]

    # build a list of (dynamo) "Morpheme" objects from each (dynamo) "MorphemeFamily" object
    # so that later we can query for a morpheme family by morpheme id using dynamo
    morpheme_lists: List[List[Morpheme]] = [m.create_morphemes() for m in m_families]
    morphemes = reduce(lambda l1, l2: l1 + l2, morpheme_lists)
    morpheme_items = [m.to_item() for m in morphemes]

    # return all of these items in a single list so that we can write them to dynamo in batches
    items = m_family_items + morpheme_items

    return items


def batchify(lst: list, batch_size: int) -> Generator[list, None, None]:
    """Return a generator that returns sublists of up to ``batch_size`` at a time of ``lst``."""
    num_batches = len(lst) // batch_size
    for batch_index in range(num_batches + 1):
        batch_start_index = batch_index * batch_size
        batch_stop_index = batch_start_index + batch_size
        yield lst[batch_start_index:batch_stop_index]


if __name__ == "__main__":
    batch_etl_morphemes_from_postgres_to_dynamo()
