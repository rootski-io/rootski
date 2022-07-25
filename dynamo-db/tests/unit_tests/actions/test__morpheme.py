from fixtures.rootski_dynamo_table import get_dynamodb_resource

from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import _Table

from dynamodb_play.dynamo import ROOTSKI_DYNAMO_TABLE_NAME


# pylint: disable=redefined-outer-name
def test__table_creation(rootski_dynamo_table: _Table):
    dynamo: DynamoDBServiceResource = get_dynamodb_resource()
    table: _Table = dynamo.Table(name=ROOTSKI_DYNAMO_TABLE_NAME)
    assert table.item_count == rootski_dynamo_table.item_count == 0
    assert table.name == rootski_dynamo_table.name == ROOTSKI_DYNAMO_TABLE_NAME
