from mypy_boto3_dynamodb.type_defs import (
    BatchGetItemOutputServiceResourceTypeDef,
    GetItemOutputTableTypeDef,
    QueryOutputTableTypeDef,
)


def get_item_status_code(item_output: GetItemOutputTableTypeDef) -> int:
    return item_output["ResponseMetadata"]["HTTPStatusCode"]


def get_item_from_dynamo_response(item_output: GetItemOutputTableTypeDef) -> dict:
    return item_output["Item"]


def get_items_from_dynamo_query_response(item_output: QueryOutputTableTypeDef) -> dict:
    return item_output["Items"]


def batch_get_item_status_code(item_output: BatchGetItemOutputServiceResourceTypeDef) -> int:
    return item_output["ResponseMetadata"]["HTTPStatusCode"]


def get_items_from_dynamo_batch_get_items_response(
    item_output: BatchGetItemOutputServiceResourceTypeDef, table_name: str
) -> dict:
    return item_output["Responses"][table_name]
