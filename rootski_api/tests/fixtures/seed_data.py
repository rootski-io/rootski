"""
Seed data to put into the mock DynamoDB table and test the breakdown endpoint.
"""
from mypy_boto3_dynamodb.service_resource import _Table

EXAMPLE_BREAKDOWN = {
    "pk": "WORD#32",
    "sk": "BREAKDOWN",
    "gsi1pk": "USER#anonymous",
    "gsi1sk": "WORD#32",
    "gsi2pk": "WORD#32",
    "gsi2sk": "USER#anonymous",
    "__type": "BREAKDOWN",
    "word": "мочь",
    "word_id": "32",
    "submitted_by_user_email": "anonymous",
    "is_verified": False,
    "is_inference": True,
    "date_submitted": "2022-02-15 05:45:18.740114",
    "date_verified": "None",
    "breakdown_items": [{"position": "0", "morpheme_id": None, "morpheme": "мочь", "morpheme_family_id": None}],
}


EXAMPLE_VERIFiED_BREAKDOWN = {
    "pk": "WORD#32",
    "sk": "BREAKDOWN",
    "gsi1pk": "USER#anonymous",
    "gsi1sk": "WORD#32",
    "gsi2pk": "WORD#32",
    "gsi2sk": "USER#anonymous",
    "__type": "BREAKDOWN",
    "word": "мочь",
    "word_id": "32",
    "submitted_by_user_email": "anonymous",
    "is_verified": True,
    "is_inference": True,
    "date_submitted": "2022-02-15 05:45:18.740114",
    "date_verified": "None",
    "breakdown_items": [{"position": "0", "morpheme_id": None, "morpheme": "мочь", "morpheme_family_id": None}],
}

EXAMPLE_BREAKDOWN_2 = {
    "pk": "WORD#61900",
    "sk": "BREAKDOWN",
    "gsi1pk": "USER#anonymous",
    "gsi1sk": "WORD#61900",
    "gsi2pk": "WORD#61900",
    "gsi2sk": "USER#anonymous",
    "__type": "BREAKDOWN",
    "word": "занавешивать",
    "word_id": "61900",
    "submitted_by_user_email": "anonymous",
    "is_verified": False,
    "is_inference": True,
    "date_submitted": "2022-02-15 05:45:18.740114",
    "date_verified": "None",
    "breakdown_items": [
        {"position": "0", "morpheme": "занавеш", "morpheme_id": None, "morpheme_family_id": None},
        {"position": "1", "morpheme": "ивать", "morpheme_id": None, "morpheme_family_id": None},
    ],
}


EXAMPLE_BREAKDOWN_ITEM_1 = {
    "submitted_by_user_email": "eric.riddoch@gmail.com",
    "breakdown_id": "77222",
    "morpheme_id": "2213",
    "gsi1sk": "BREAKDOWN#eric.riddoch@gmail.com",
    "__type": "BREAKDOWN_ITEM",
    "word_id": "771",
    "sk": "BREAKDOWN_ITEM#2213#0",
    "morpheme_family_id": "2213",
    "pk": "WORD#771",
    "position": "0",
    "morpheme": "вы",
    "gsi1pk": "MORPHEME_FAMILY#2213",
}


EXAMPLE_NULL_BREAKDOWN_ITEM_1 = {
    "pk": "WORD#9203",
    "sk": "BREAKDOWN_ITEM#f4ef8326-a27e-4cb6-9cac-0089fc1eda45#8",
    "__type": "BREAKDOWN_ITEM_NULL",
    "word_id": "9203",
    "position": "8",
    "morpheme": "ся",
    "morpheme_id": None,
    "morpheme_family_id": None,
    "submitted_by_user_email": None,
}

EXAMPLE_DATA = [
    EXAMPLE_BREAKDOWN,
    EXAMPLE_BREAKDOWN_2,
    EXAMPLE_VERIFiED_BREAKDOWN,
    EXAMPLE_BREAKDOWN_ITEM_1,
    EXAMPLE_NULL_BREAKDOWN_ITEM_1,
]


# Helper Function
def seed_data(rootski_dynamo_table: _Table) -> None:
    for data in EXAMPLE_DATA:
        rootski_dynamo_table.put_item(Item=data)
    item = rootski_dynamo_table.get_item(Key={"pk": "WORD#32", "sk": "BREAKDOWN"})
    print(item)
