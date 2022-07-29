"""
NOTE: remember to cast all IDs to strings
"""


from ast import Break
from turtle import position
from rich.pretty import pprint
from sqlalchemy.orm import joinedload
from functools import reduce


from typing import List, Union
import rootski.services.database.models as orm
from dynamodb_play.etl.db_service import get_dbservice
from dynamodb_play.dynamo import get_rootski_dynamo_table
from dynamodb_play.etl.utils import batchify, bulk_upload_to_dynamo
from dynamodb_play.models.breakdown import Breakdown, BreakdownItemItem
from dynamodb_play.models.breakdown_item import BreakdownItem, NullBreakdownItem


def make_dynamo_breakdown_item_dict_from_orm(orm_breakdown_item :orm.BreakdownItem) -> Union[BreakdownItem, NullBreakdownItem]:
    """Build a ```BreakdownItem``` or ```NullBreakdownItem``` object from a SQLAlchemy ```orm.BreakdownItem``` object.

    The resulting object has data organized in the way it is intended to end up in dynamo.
    """
    if orm.BreakdownItem.morpheme_id is None:
        return NullBreakdownItem(
            word_id=str(orm_breakdown_item),
            position=str(orm_breakdown_item.position),
            morpheme=str(orm_breakdown_item.morpheme),
            submitted_by_user_email=orm_breakdown_item.breakdown.submitted_by_user.email
        )
    else:
        return BreakdownItem(
            word_id=str(orm_breakdown_item.breakdown.word_id),
            position=str(orm_breakdown_item.position),
            morpheme_family_id=orm_breakdown_item.morpheme_.family_id,
            morpheme=str(orm_breakdown_item.morpheme),
            morpheme_id=str(orm_breakdown_item.morpheme_id),
            submitted_by_user_email=orm_breakdown_item.breakdown.submitted_by_user.email,
            breakdown_id=str(orm_breakdown_item.breakdown_id)
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
        breakdown_items=[
            make_dynamo_breakdown_item_dict_from_orm(b)
            for b in breakdown_items
        ],
    )


def extract() -> List[dict]:
    """Query breakdowns items from postgres database.
    """
    # connect to an instance of the rootski postgres database running locally
    db_service = get_dbservice()
    session = db_service.get_sync_session()

    # query all of the breakdown rows from postgres
    orm_breakdowns: List[orm.Breakdown] = (
        session.query(orm.Breakdown)
        .options(
            joinedload(orm.Breakdown.breakdown_items),
            joinedload(orm.Breakdown.submitted_by_user)
        )
        .all()
    )

    return orm_breakdowns
    
    
def transform(orm_breakdowns) -> List[dict]:
    """_summary_

    :return: _description_
    """
    # convert the SQLAlchemy "orm.Breakdown" models to dicts meant for dynamo
    b
    orm_breakdowns:
    
    
    
    # m_families: List[MorphemeFamily] = [make_dynamo_morpheme_family_from_orm(b) for b in breakdown_orm]
    # m_family_items: List[dict] = [m.to_item() for m in m_families]

    return breakdowns_orm


if __name__ == "__main__":
    # batch_etl_morphemes_from_postgres_to_dynamo()
    query = get_breakdown_items_from_postgres()
    print(query)