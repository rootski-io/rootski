import time
from dataclasses import dataclass
from pathlib import Path

import boto3
import pandas as pd
from mypy_boto3_dynamodb import DynamoDBClient, DynamoDBServiceResource
from rich import print
from rich.pretty import pprint

THIS_DIR = Path(__file__).parent

WORDS_CSV_FPATH = THIS_DIR / "../../words.csv"

WORDS_DF = pd.read_csv(WORDS_CSV_FPATH)


def _get_boto_session() -> boto3.Session:
    return boto3.Session(profile_name="rootski", region_name="us-west-2")


def get_dynamodb_resource() -> DynamoDBServiceResource:
    session = _get_boto_session()
    return session.resource("dynamodb")


def get_dynamodb_client() -> DynamoDBClient:
    session = _get_boto_session()
    return session.client("dynamodb")


dynamo = get_dynamodb_resource()
dynamo_client = get_dynamodb_client()

# Table defination
def delete_table_if_exists(dynamo: DynamoDBServiceResource, table_name: str):
    try:
        table = dynamo.Table(name=table_name)
        table.delete()
        time.sleep(4)
    except:
        ...


# delete_table_if_exists(dynamo, "russian-words")

# dynamo.create_table(
#     TableName="russian-words",
#     KeySchema=[
#         {"AttributeName": "word", "KeyType": "HASH"},
#         # {
#         #     'AttributeName': 'datacount',
#         #     'KeyType': 'RANGE'  # Sort key
#         # }
#     ],
#     AttributeDefinitions=[
#         {"AttributeName": "word", "AttributeType": "S"},
#         # {"AttributeName": "word_id", "AttributeType": "S"},
#     ],
#     BillingMode="PAY_PER_REQUEST",
# )

table = dynamo.Table("russian-words")

df = WORDS_DF[:10]

# df.apply(axis=1, func=put_item)


@dataclass
class WordItem:
    word: str
    id: str

    def to_item(self) -> dict:
        return {"word": self.word, "word_id": str(self.id), "extra": {"name": "Eric", "age": 25}}


with table.batch_writer() as writer:

    def put_item(row):
        item = WordItem(**row)
        print("putting item:", item)
        writer.put_item(item.to_item())

    df.apply(axis=1, func=put_item)


result = dynamo_client.execute_statement(
    Statement="""
    SELECT extra
    FROM "russian-words"
    WHERE contains(word, 'н')
"""
)
pprint(
    result["Items"],
)
