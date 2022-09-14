import boto3
import pytest
from moto import mock_dynamodb
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import _Table
from mypy_boto3_dynamodb.type_defs import GlobalSecondaryIndexTypeDef
from rootski.services.database.dynamo.db_service import DBService
from tests.constants import ROOTSKI_DYNAMO_TABLE_NAME

# from rootski.services.database import DBService


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
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
            {"AttributeName": "gsi1pk", "AttributeType": "S"},
            {"AttributeName": "gsi1sk", "AttributeType": "S"},
            {"AttributeName": "gsi2pk", "AttributeType": "S"},
            {"AttributeName": "gsi2sk", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            GlobalSecondaryIndexTypeDef(
                IndexName="gsi1",
                KeySchema=[
                    {"AttributeName": "gsi1pk", "KeyType": "HASH"},
                    {"AttributeName": "gsi1sk", "KeyType": "RANGE"},
                ],
                Projection={"ProjectionType": "ALL"},
            ),
            GlobalSecondaryIndexTypeDef(
                IndexName="gsi2",
                KeySchema=[
                    {"AttributeName": "gsi2pk", "KeyType": "HASH"},
                    {"AttributeName": "gsi2sk", "KeyType": "RANGE"},
                ],
                Projection={"ProjectionType": "ALL"},
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


@pytest.fixture
def dynamo_db_service(rootski_dynamo_table: _Table) -> DBService:
    """Create a dynamodb service."""
    db_service = DBService(ROOTSKI_DYNAMO_TABLE_NAME)
    db_service.init()
    yield db_service
