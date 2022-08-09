from rootski.services.database.dynamo.actions.dynamo import get_item_from_dynamo_response, get_item_status_code
from rootski.services.database.dynamo.db_service import DBService
from rootski.services.database.dynamo.models.breakdown import Breakdown, make_keys


class BreakdownNotFoundError(Exception):
    """Error thrown if a Breakdown isn't found."""


def get_verified_breakdown_by_word_id(word_id: str, db: DBService) -> bool:
    """Query a breakdown from Dynamo matching the ``word_id``.

    :raises BreakdownNotFoundError: raised if no breakdown exists for the given ``word``.
    """
    table = db.rootski_table
    breakdown_dynamo_keys: dict = make_keys(word_id=word_id)

    get_item_response = table.get_item(Key=breakdown_dynamo_keys)
    if get_item_status_code(item_output=get_item_response) == 404:
        raise BreakdownNotFoundError(f"No word with ID {word_id} was found in Dynamo.")

    item = get_item_from_dynamo_response(get_item_response)
    breakdown = Breakdown.from_dict(breakdown_dict=item)
    return breakdown.is_verified
