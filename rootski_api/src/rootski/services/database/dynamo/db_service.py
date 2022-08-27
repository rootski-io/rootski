from __future__ import annotations

from typing import Type

import boto3
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, _Table
from rootski.config.config import Config
from rootski.services.service import Service


class DBService(Service):
    def __init__(self, dynamo_table_name: str):
        self.dynamo_table_name: str = dynamo_table_name

    def init(self):
        self.dynamo: DynamoDBServiceResource = boto3.resource("dynamodb")
        self.rootski_table: _Table = self.dynamo.Table(name=self.dynamo_table_name)

    @classmethod
    def from_config(cls: Type[DBService], config: Config):
        return cls(dynamo_table_name=config.dynamo_table_name)
