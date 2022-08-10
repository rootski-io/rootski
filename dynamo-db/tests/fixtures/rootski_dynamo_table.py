import boto3
import pytest
from dynamodb_play.dynamo import ROOTSKI_DYNAMO_TABLE_NAME
from moto import mock_dynamodb
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import _Table
from mypy_boto3_dynamodb.type_defs import GlobalSecondaryIndexTypeDef


def _get_boto_session() -> boto3.Session:
    return boto3.Session(region_name="us-west-2")


def get_dynamodb_resource() -> DynamoDBServiceResource:
    session = _get_boto_session()
    return session.resource("dynamodb")


def create_rootski_table() -> _Table:
    dynamo = get_dynamodb_resource()
    dynamo.create_table(
        TableName=ROOTSKI_DYNAMO_TABLE_NAME,
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
            {"AttributeName": "GSI2PK", "AttributeType": "S"},
            {"AttributeName": "GSI2SK", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            GlobalSecondaryIndexTypeDef(
                IndexName="GSI1",
                KeySchema=[
                    {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                ],
                Projection={"ProjectionType": "ALL"},
            ),
        ],
        GlobalSecondaryIndexes=[
            GlobalSecondaryIndexTypeDef(
                IndexName="GSI2",
                KeySchema=[
                    {"AttributeName": "GSI2PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI2SK", "KeyType": "RANGE"},
                ],
                Projection={
                    "ProjectionType": "ALL"
                }
            ),
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    return dynamo.Table(name=ROOTSKI_DYNAMO_TABLE_NAME)


@pytest.fixture
def rootski_dynamo_table() -> _Table:
    with mock_dynamodb():
        table = create_rootski_table()
        yield table
