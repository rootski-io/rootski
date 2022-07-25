#!/usr/bin/env python3

"""CDK Application for creating a DynamoDB table for rootski."""

import aws_cdk as cdk
from rootski_backend_cdk.dynamo.dynamo_stack import DynamoStack

app = cdk.App()
DynamoStack(app, "DynamoStack")

app.synth()
