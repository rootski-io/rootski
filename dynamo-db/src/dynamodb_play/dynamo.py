import boto3
from mypy_boto3_dynamodb.service_resource import _Table

ROOTSKI_DYNAMO_TABLE_NAME = "rootski-table"


def get_rootski_dynamo_table() -> _Table:
    rootski_table = boto3.resource("dynamodb").Table(name=ROOTSKI_DYNAMO_TABLE_NAME)
    return rootski_table
