#!/usr/bin/env python3

# For consistency with TypeScript code, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core
from aws_cdk import core as cdk

# from stacks.backend_api.backend_api import BackendAPIStack

from lightsail_dependencies.stacks.lightsail_iam_user_stack import LightsailIAMUserStack
from lightsail_dependencies.stacks.db_backups_bucket_stack import DatabaseBackupsBucketStack
from common.constants import StackNames

app = core.App()

environment = cdk.Environment(
    account="091910621680",
    region="us-west-2",
)

db_backup_stack = DatabaseBackupsBucketStack(app, StackNames.db_backups_bucket.value, env=environment)
iam_stack = LightsailIAMUserStack(
    app, StackNames.iam_user.value, rootski_db_bucket=db_backup_stack.bucket, env=environment
)

app.synth()
