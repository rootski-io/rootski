from mypy_boto3_dynamodb.type_defs import GetItemOutputTableTypeDef


def get_item_status_code(item_output: GetItemOutputTableTypeDef) -> int:
    return item_output["ResponseMetadata"]["HTTPStatusCode"]


def get_item_from_dynamo_response(item_output: GetItemOutputTableTypeDef) -> dict:
    return item_output["Item"]
