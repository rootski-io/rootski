"""App that creates an S3 bucket and IAM user for the lightsail instance."""

# For consistency with TypeScript code, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
import aws_cdk as cdk

from rootski_backend_cdk.common.constants import StackNames
from rootski_backend_cdk.database.lightsail_dependencies.stacks.db_backups_bucket_stack import (
    DatabaseBackupsBucketStack,
)
from rootski_backend_cdk.database.lightsail_dependencies.stacks.lightsail_iam_user_stack import (
    LightsailIAMUserStack,
)

# only run this in main so the documentation can generate properly
if __name__ == "__main__":

    app = cdk.App()

    environment = cdk.Environment(
        account="091910621680",
        region="us-west-2",
    )

    db_backup_stack = DatabaseBackupsBucketStack(app, StackNames.db_backups_bucket.value, env=environment)
    iam_stack = LightsailIAMUserStack(
        app,
        StackNames.iam_user.value,
        rootski_db_bucket=db_backup_stack.bucket,
        env=environment,
    )

    app.synth()
