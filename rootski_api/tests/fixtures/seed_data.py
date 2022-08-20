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
    "breakdown_items": [{"position": 0, "morpheme_id": None, "morpheme": "мочь", "morpheme_family_id": None}],
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
        {"position": 0, "morpheme": "занавеш", "morpheme_id": None, "morpheme_family_id": None},
        {"position": 1, "morpheme": "ивать", "morpheme_id": None, "morpheme_family_id": None},
    ],
}


EXAMPLE_BREAKDOWN_ANOTHER_USER_2 = {
    "pk": "WORD#5",
    "sk": "BREAKDOWN",
    "gsi1pk": "USER#another_user@gmail.com",
    "gsi1sk": "WORD#5",
    "gsi2pk": "WORD#5",
    "gsi2sk": "USER#another_user@gmail.com",
    "__type": "BREAKDOWN",
    "word": "занавешивать",
    "word_id": "5",
    "submitted_by_user_email": "another_user@gmail.com",
    "is_verified": True,
    "is_inference": False,
    "date_submitted": "2022-02-15 05:45:18.740114",
    "date_verified": "None",
    "breakdown_items": [
        {"position": 0, "morpheme": "занавеш", "morpheme_id": None, "morpheme_family_id": None},
        {"position": 1, "morpheme": "ивать", "morpheme_id": None, "morpheme_family_id": None},
    ],
}


EXAMPLE_BREAKDOWN_57 = {
    "gsi2sk": "USER#anonymous",
    "submitted_by_user_email": "anonymous",
    "gsi1sk": "WORD#57",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "57",
    "date_submitted": "2022-02-15 05:45:18.740114",
    "word": "знать",
    "sk": "BREAKDOWN",
    "pk": "WORD#57",
    "breakdown_items": [
        {"morpheme": "зна", "morpheme_family_id": "245", "position": 0, "morpheme_id": "511"},
        {"morpheme": "ть", "morpheme_family_id": "1385", "position": 1, "morpheme_id": "2196"},
    ],
    "gsi1pk": "USER#anonymous",
    "is_verified": False,
    "is_inference": True,
    "gsi2pk": "WORD#57",
}


EXAMPLE_BREAKDOWN_ANOTHER_USER = {
    "pk": "WORD#10",
    "sk": "BREAKDOWN",
    "gsi1pk": "USER#another_user@gmail.com",
    "gsi1sk": "WORD#10",
    "gsi2pk": "WORD#10",
    "gsi2sk": "USER#another_user@gmail.com",
    "__type": "BREAKDOWN",
    "word": "занавешивать",
    "word_id": "10",
    "submitted_by_user_email": "another_user@gmail.com",
    "is_verified": False,
    "is_inference": False,
    "date_submitted": "2022-02-15 05:45:18.740114",
    "date_verified": "None",
    "breakdown_items": [
        {"position": 0, "morpheme": "занавеш", "morpheme_id": None, "morpheme_family_id": None},
        {"position": 1, "morpheme": "ивать", "morpheme_id": None, "morpheme_family_id": None},
    ],
}


EXAMPLE_BREAKDOWN_ERIC_USER = {
    "pk": "WORD#5",
    "sk": "BREAKDOWN",
    "gsi1pk": "USER#eric.riddoch@gmail.com",
    "gsi1sk": "WORD#5",
    "gsi2pk": "WORD#5",
    "gsi2sk": "USER#eric.riddoch@gmail.com",
    "__type": "BREAKDOWN",
    "word": "занавешивать",
    "word_id": "5",
    "submitted_by_user_email": "eric.riddoch@gmail.com",
    "is_verified": True,
    "is_inference": False,
    "date_submitted": "2022-02-15 05:45:18.740114",
    "date_verified": "None",
    "breakdown_items": [
        {"position": 0, "morpheme": "занавеш", "morpheme_id": None, "morpheme_family_id": None},
        {"position": 1, "morpheme": "ивать", "morpheme_id": None, "morpheme_family_id": None},
    ],
}


EXAMPLE_VERIFIED_BREAKDOWN = {
    "pk": "WORD#30",
    "sk": "BREAKDOWN",
    "gsi1pk": "USER#eric.riddoch@gmail.com",
    "gsi1sk": "WORD#30",
    "gsi2pk": "WORD#30",
    "gsi2sk": "USER#eric.riddoch@gmail.com",
    "__type": "BREAKDOWN",
    "word": "мочь",
    "word_id": "30",
    "submitted_by_user_email": "eric.riddoch@gmail.com",
    "is_verified": True,
    "is_inference": False,
    "date_submitted": "2022-02-15 05:45:18.740114",
    "date_verified": "None",
    "breakdown_items": [{"position": 0, "morpheme_id": None, "morpheme": "мочь", "morpheme_family_id": None}],
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
    "position": 0,
    "morpheme": "вы",
    "gsi1pk": "MORPHEME_FAMILY#2213",
}


EXAMPLE_NULL_BREAKDOWN_ITEM_1 = {
    "pk": "WORD#9203",
    "sk": "BREAKDOWN_ITEM#f4ef8326-a27e-4cb6-9cac-0089fc1eda45#8",
    "__type": "BREAKDOWN_ITEM_NULL",
    "word_id": "9203",
    "position": 8,
    "morpheme": "ся",
    "morpheme_id": None,
    "morpheme_family_id": None,
    "submitted_by_user_email": None,
}


EXAMPLE_MORPHEME_FAMILY_245 = {
    "morphemes": [{"morpheme": "знай", "morpheme_id": "510"}, {"morpheme": "зна", "morpheme_id": "511"}],
    "family_meanings": ["know"],
    "level": 1,
    "__type": "MORPHEME_FAMILY",
    "sk": "MORPHEME_FAMILY#245",
    "word_pos": "any",
    "family_id": "245",
    "pk": "MORPHEME_FAMILY#245",
    "type": "root",
}


EXAMPLE_MORPHEME_FAMILY_1385 = {
    "morphemes": [{"morpheme": "ть", "morpheme_id": "2196"}],
    "family_meanings": [None],
    "level": 6,
    "__type": "MORPHEME_FAMILY",
    "sk": "MORPHEME_FAMILY#1385",
    "word_pos": "verb",
    "family_id": "1385",
    "pk": "MORPHEME_FAMILY#1385",
    "type": "suffix",
}


EXAMPLE_DATA = [
    EXAMPLE_BREAKDOWN,
    EXAMPLE_BREAKDOWN_2,
    EXAMPLE_BREAKDOWN_57,
    EXAMPLE_BREAKDOWN_ANOTHER_USER,
    EXAMPLE_BREAKDOWN_ANOTHER_USER_2,
    EXAMPLE_BREAKDOWN_ERIC_USER,
    EXAMPLE_VERIFIED_BREAKDOWN,
    EXAMPLE_BREAKDOWN_ITEM_1,
    EXAMPLE_NULL_BREAKDOWN_ITEM_1,
    EXAMPLE_MORPHEME_FAMILY_245,
    EXAMPLE_MORPHEME_FAMILY_1385,
]


# Helper Function
def seed_data(rootski_dynamo_table: _Table) -> None:
    for data in EXAMPLE_DATA:
        rootski_dynamo_table.put_item(Item=data)
