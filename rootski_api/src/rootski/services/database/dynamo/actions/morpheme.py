from typing import Dict, List

from mypy_boto3_dynamodb.type_defs import KeysAndAttributesServiceResourceTypeDef
from rootski.errors import RootskiApiError
from rootski.services.database.dynamo.actions.dynamo import (
    batch_get_item_status_code,
    get_items_from_dynamo_batch_get_items_response,
)
from rootski.services.database.dynamo.db_service import DBService as DynamoDBService
from rootski.services.database.dynamo.models.morpheme import Morpheme, make_gsi1_keys
from rootski.services.database.dynamo.models.morpheme_family import MorphemeFamily


class MorphemeNotFoundError(RootskiApiError):
    """Error thrown if a Morpheme isn't found."""


class MorphemeFamilyNotFoundError(RootskiApiError):
    """Error thrown if a MorphemeFamily isn't found."""
