#!/usr/bin/env python3
import os

import aws_cdk as cdk
from ml_pipeline.ecs_cluster.ml_batch_compute_environment import MlBatchComputeEnvironment

environment = cdk.Environment(
    account="091910621680",
    region="us-west-2",
)

app = cdk.App()

MlBatchComputeEnvironment(
    app, 
    "Rootski-ML-Batch-Compute-Environment-cdk",
    env=environment,
)

app.synth()
