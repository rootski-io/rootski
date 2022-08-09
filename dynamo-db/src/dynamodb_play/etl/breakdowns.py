"""
NOTE: remember to cast all IDs to strings
"""

from itertools import chain
from typing import List, Union

import rootski.services.database.models as orm
from dynamodb_play.etl.db_service import get_dbservice
from dynamodb_play.etl.utils import batch_load_into_dynamo
from dynamodb_play.models.breakdown import Breakdown
from dynamodb_play.models.breakdown_item import BreakdownItem, NullBreakdownItem
from sqlalchemy.orm import joinedload


def extract() -> List[orm.Breakdown]:
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


def make_dynamo_breakdown_item_dict_from_orm(
    orm_breakdown_item: orm.BreakdownItem,
) -> Union[BreakdownItem, NullBreakdownItem]:
    """Build a ```BreakdownItem``` or ```NullBreakdownItem``` object from a SQLAlchemy ```orm.BreakdownItem``` object.

    The resulting object has data organized in the way it is intended to end up in dynamo.
    """
    if orm_breakdown_item.morpheme_id is None:
        return NullBreakdownItem(
            word_id=str(orm_breakdown_item.breakdown.word_id),
            position=str(orm_breakdown_item.position),
            submitted_by_user_email=orm_breakdown_item.breakdown.submitted_by_user_email,
            morpheme=str(orm_breakdown_item.morpheme),
        )
    else:
        # user_or_none: Optional[orm.User] = orm_breakdown_item.breakdown.submitted_by_user
        # family_id_or_none: Optional[orm.BreakdownItem] = orm_breakdown_item.morpheme_

        return BreakdownItem(
            word_id=str(orm_breakdown_item.breakdown.word_id),
            position=str(orm_breakdown_item.position),
            submitted_by_user_email=orm_breakdown_item.breakdown.submitted_by_user_email,  # None if not user_or_none else user_or_none.email,
            morpheme=str(orm_breakdown_item.morpheme),
            morpheme_family_id=orm_breakdown_item.morpheme_id,  # None if not family_id_or_none else family_id_or_none.family_id,
            morpheme_id=str(orm_breakdown_item.morpheme_id),
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
        submitted_by_user_email="anonymous"
        if orm_breakdown.submitted_by_user_email is None
        else str(orm_breakdown.submitted_by_user_email),
        is_verified=orm_breakdown.is_verified,
        is_inference=True if orm_breakdown.submitted_by_user_email is None else orm_breakdown.is_inference,
        date_submitted=str(orm_breakdown.date_submitted),
        date_verified=str(orm_breakdown.date_verified),
        breakdown_items=[make_dynamo_breakdown_item_dict_from_orm(b) for b in breakdown_items],
    )


def transform(orm_breakdowns) -> List[dict]:
    """Create a list of dictionaries representing either a dynamo Breakdown or Breakdown_Item object"""
    # convert the SQLAlchemy "orm.Breakdown" models to dicts meant for dynamo
    dynamo_breakdown_models: List[Breakdown] = [make_dynamo_breakdown_dict_from_orm(b) for b in orm_breakdowns]
    breakdown_dict_list: List[dict] = [b.to_item() for b in dynamo_breakdown_models]

    # Build a list of (dynamo) "BreakdownItem" objects from each (dynamo) "Breakdown" object
    dynamo_breakdown_items_lists: List[List[Union[BreakdownItem, NullBreakdownItem]]] = [
        b.breakdown_items for b in dynamo_breakdown_models
    ]
    dynamo_breakdown_items = list(chain(*dynamo_breakdown_items_lists))
    breakdown_item_dict_list: List[dict] = [bi.to_item() for bi in dynamo_breakdown_items]

    # Return all the dictionaries in a single list
    return breakdown_dict_list + breakdown_item_dict_list


if __name__ == "__main__":
    # batch_etl_morphemes_from_postgres_to_dynamo()
    orm_breakdowns_ = extract()
    dynamo_dictionaries_list = transform(orm_breakdowns_)
    batch_load_into_dynamo(dynamo_dictionaries_list, batch_size=1000)
