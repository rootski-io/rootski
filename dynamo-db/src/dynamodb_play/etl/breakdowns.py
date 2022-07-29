"""
NOTE: remember to cast all IDs to strings
"""


from typing import List, Union

import rootski.services.database.models as orm
from dynamodb_play.etl.db_service import get_dbservice
from dynamodb_play.models.breakdown import Breakdown
from dynamodb_play.models.breakdown_item import BreakdownItem, NullBreakdownItem
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


def make_dynamo_breakdown_item_dict_from_orm(
    orm_breakdown_item: orm.BreakdownItem,
) -> Union[BreakdownItem, NullBreakdownItem]:
    """Build a ```BreakdownItem``` or ```NullBreakdownItem``` object from a SQLAlchemy ```orm.BreakdownItem``` object.

    The resulting object has data organized in the way it is intended to end up in dynamo.
    """
    if orm.BreakdownItem.morpheme_id is None:
        return NullBreakdownItem(
            word_id=str(orm_breakdown_item),
            position=str(orm_breakdown_item.position),
            morpheme=str(orm_breakdown_item.morpheme),
            submitted_by_user_email=orm_breakdown_item.breakdown.submitted_by_user.email,
        )
    else:
        return BreakdownItem(
            word_id=str(orm_breakdown_item.breakdown.word_id),
            position=str(orm_breakdown_item.position),
            morpheme_family_id=orm_breakdown_item.morpheme_.family_id,
            morpheme=str(orm_breakdown_item.morpheme),
            morpheme_id=str(orm_breakdown_item.morpheme_id),
            submitted_by_user_email=orm_breakdown_item.breakdown.submitted_by_user.email,
            breakdown_id=str(orm_breakdown_item.breakdown_id),
        )


def make_dynamo_breakdown_dict_from_orm(orm_breakdown: orm.Breakdown) -> Breakdown:
    """
    Build a ``Breakdown`` object from a SQLAlchemy ``orm.Breakdown`` object.

    The resulting object has data organized in the way it is intended to end up in dynamo.
    """
    breakdown_items: List[orm.BreakdownItem] = orm_breakdown.breakdown_items

    return Breakdown(
        word=str(orm_breakdown.word),
        word_id=str(orm_breakdown.word_id),
        submitted_by_user_email=str(orm_breakdown.submitted_by_user_email),
        is_verified=orm_breakdown.is_verified,
        is_inference=orm_breakdown.is_inference,
        date_submitted=str(orm_breakdown.date_submitted),
        date_verified=str(orm_breakdown.date_verified),
        breakdown_items=[make_dynamo_breakdown_item_dict_from_orm(b) for b in breakdown_items],
    )


def extract() -> List[dict]:
    """Query breakdowns items from postgres database."""
    # connect to an instance of the rootski postgres database running locally
    db_service = get_dbservice()
    session = db_service.get_sync_session()

    # query all of the breakdown rows from postgres
    orm_breakdowns: List[orm.Breakdown] = (
        session.query(orm.Breakdown)
        .options(joinedload(orm.Breakdown.breakdown_items), joinedload(orm.Breakdown.submitted_by_user))
        .all()
    )

    return orm_breakdowns

    # convert the SQLAlchemy "orm.Breakdown" models to dicts meant for dynamo

    # m_families: List[MorphemeFamily] = [make_dynamo_morpheme_family_from_orm(b) for b in breakdown_orm]
    # m_family_items: List[dict] = [m.to_item() for m in m_families]

    return breakdowns_orm


if __name__ == "__main__":
    # batch_etl_morphemes_from_postgres_to_dynamo()
    query = get_breakdown_items_from_postgres()
    print(query)
