from rootski.errors import RootskiApiError
from rootski.services.database.dynamo.actions.dynamo import (
    batch_get_item_status_code,
    get_items_from_dynamo_batch_get_items_response,
)


class MorphemeNotFoundError(RootskiApiError):
    """Error thrown if a Morpheme isn't found."""


class MorphemeFamilyNotFoundError(RootskiApiError):
    """Error thrown if a MorphemeFamily isn't found."""
