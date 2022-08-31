"""
Seed data to put into the mock DynamoDB table and test the breakdown endpoint.
"""
from decimal import Decimal

from mypy_boto3_dynamodb.service_resource import _Table

#############################
# Modified/made-up Examples #
#############################

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


######################
# Real Data Examples #
######################

EXAMPLE_BREAKDOWN_56 = {
    "gsi2sk": "USER#anonymous",
    "submitted_by_user_email": "anonymous",
    "gsi1sk": "WORD#56",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "56",
    "date_submitted": "2022-02-15 05:45:18.740114",
    "word": "самый",
    "sk": "BREAKDOWN",
    "pk": "WORD#56",
    "breakdown_items": [
        {"morpheme": "сам", "morpheme_family_id": None, "position": "0", "morpheme_id": None},
        {"morpheme": "ый", "morpheme_family_id": None, "position": "1", "morpheme_id": None},
    ],
    "gsi1pk": "USER#anonymous",
    "is_verified": False,
    "is_inference": True,
    "gsi2pk": "WORD#56",
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
        {"morpheme": "зна", "morpheme_family_id": "245", "position": 0, "morpheme_id": "511"},
        {"morpheme": "ть", "morpheme_family_id": "1385", "position": 1, "morpheme_id": "2196"},
    ],
    "gsi1pk": "USER#anonymous",
    "is_verified": False,
    "is_inference": True,
    "gsi2pk": "WORD#57",
}


EXAMPLE_BREAKDOWN_438 = {
    "gsi2sk": "USER#anonymous",
    "submitted_by_user_email": "anonymous",
    "gsi1sk": "WORD#438",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "438",
    "date_submitted": "2022-02-15 05:45:18.740114",
    "word": "выходить",
    "sk": "BREAKDOWN",
    "pk": "WORD#438",
    "breakdown_items": [
        {"morpheme": "вы", "morpheme_family_id": "102", "position": "0", "morpheme_id": "218"},
        {"morpheme": "ход", "morpheme_family_id": "812", "position": "1", "morpheme_id": "1577"},
        {"morpheme": "ить", "morpheme_family_id": "1333", "position": "2", "morpheme_id": "2139"},
    ],
    "gsi1pk": "USER#anonymous",
    "is_verified": False,
    "is_inference": True,
    "gsi2pk": "WORD#438",
}


EXAMPLE_BREAKDOWN_771 = {
    "gsi2sk": "USER#eric.riddoch@gmail.com",
    "submitted_by_user_email": "eric.riddoch@gmail.com",
    "gsi1sk": "WORD#771",
    "date_verified": "2022-07-23 05:42:11.985578",
    "__type": "BREAKDOWN",
    "word_id": "771",
    "date_submitted": "2022-02-15 09:00:24.068323",
    "word": "выглядеть",
    "sk": "BREAKDOWN",
    "pk": "WORD#771",
    "breakdown_items": [
        {"morpheme": "вы", "morpheme_family_id": "1401", "position": "0", "morpheme_id": "2213"},
        {"morpheme": "гляд", "morpheme_family_id": "127", "position": "1", "morpheme_id": "276"},
        {"morpheme": "еть", "morpheme_family_id": "1324", "position": "2", "morpheme_id": "2130"},
    ],
    "gsi1pk": "USER#eric.riddoch@gmail.com",
    "is_verified": True,
    "is_inference": False,
    "gsi2pk": "WORD#771",
}


EXAMPLE_BREAKDOWN_59470 = {
    "gsi2sk": "USER#dmitriy.abaimov@bengroupinc.com",
    "submitted_by_user_email": "dmitriy.abaimov@bengroupinc.com",
    "gsi1sk": "WORD#59470",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "59470",
    "date_submitted": "2022-02-23 15:38:30.049221",
    "word": "None",
    "sk": "BREAKDOWN",
    "pk": "WORD#59470",
    "breakdown_items": [
        {"morpheme": "само", "morpheme_family_id": "1107", "position": "0", "morpheme_id": "1892"},
        {"morpheme": "у", "morpheme_family_id": "1399", "position": "1", "morpheme_id": "2211"},
        {"morpheme": "со", "morpheme_family_id": "1403", "position": "2", "morpheme_id": "2219"},
        {"morpheme": "верш", "morpheme_family_id": "64", "position": "3", "morpheme_id": "124"},
        {"morpheme": "ен", "morpheme_family_id": None, "position": "4", "morpheme_id": None},
        {"morpheme": "ство", "morpheme_family_id": "1268", "position": "5", "morpheme_id": "2066"},
        {"morpheme": "ва", "morpheme_family_id": None, "position": "6", "morpheme_id": None},
        {"morpheme": "ни", "morpheme_family_id": None, "position": "7", "morpheme_id": None},
        {"morpheme": "е", "morpheme_family_id": "1189", "position": "8", "morpheme_id": "1985"},
    ],
    "gsi1pk": "USER#dmitriy.abaimov@bengroupinc.com",
    "is_verified": False,
    "is_inference": False,
    "gsi2pk": "WORD#59470",
}


EXAMPLE_BREAKDOWN_ITEM = {
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


EXAMPLE_NULL_BREAKDOWN_ITEM = {
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
    "level": Decimal("1"),
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
    "level": Decimal("6"),
    "__type": "MORPHEME_FAMILY",
    "sk": "MORPHEME_FAMILY#1385",
    "word_pos": "verb",
    "family_id": "1385",
    "pk": "MORPHEME_FAMILY#1385",
    "type": "suffix",
}

#########
# Users #
#########

TEST_USER = {
    "email": "banana-man@rootski.io",
    "password": "Eric Is Banana Man",
}


EXAMPLE_DATA = [
    # Hand-crafted/Modified examples for testing
    EXAMPLE_BREAKDOWN,
    EXAMPLE_BREAKDOWN_2,
    EXAMPLE_BREAKDOWN_ANOTHER_USER,
    EXAMPLE_BREAKDOWN_ANOTHER_USER_2,
    EXAMPLE_BREAKDOWN_ERIC_USER,
    EXAMPLE_VERIFIED_BREAKDOWN,
    # Examples based on real data
    EXAMPLE_BREAKDOWN_56,  # inferenced example with all null breakdown items
    EXAMPLE_BREAKDOWN_57,  # inferenced example with duplicate breakdown_items
    EXAMPLE_BREAKDOWN_438,  # inferenced example with no null breakdown items
    EXAMPLE_BREAKDOWN_771,  # Verified example by user eric.riddoch@gmail.com
    EXAMPLE_BREAKDOWN_59470,  # Non-verified example by user dmitriy.abaimov@bengroupinc.com
    EXAMPLE_BREAKDOWN_ITEM,
    EXAMPLE_NULL_BREAKDOWN_ITEM,
    EXAMPLE_MORPHEME_FAMILY_245,
    EXAMPLE_MORPHEME_FAMILY_1385,
]


# Helper Function
def seed_data(rootski_dynamo_table: _Table) -> None:
    for data in EXAMPLE_DATA:
        rootski_dynamo_table.put_item(Item=data)
