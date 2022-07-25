"""Stack that creates DynamoDB table for rootski."""

import aws_cdk.aws_dynamodb as dynamodb
from aws_cdk import Stack
from constructs import Construct


class DynamoStack(Stack):
    """Stack that creates DynamoDB table for rootski."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        rootski_table = dynamodb.Table(
            self,
            "rootski-dynamodb-table",
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            table_name="rootski-table",
        )

        rootski_table.add_global_secondary_index(
            index_name="gsi1",
            partition_key=dynamodb.Attribute(name="gsi1pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="gsi1sk", type=dynamodb.AttributeType.STRING),
        )
