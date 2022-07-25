"""Stack defining an S3 bucket for rootski database backups."""

from enum import Enum

import aws_cdk as cdk
from aws_cdk import aws_s3 as s3
from constructs import Construct


class StackOutputs(str, Enum):
    """Stack output keys for a database backups stack."""

    # pylint: disable=invalid-name
    rootski_db_backups_s3_bucket_arn = "RootskiDbBackupsS3BucketARN"
    rootski_db_backups_s3_bucket_name = "RootskiDbBackupsS3BucketName"


class DatabaseBackupsBucketStack(cdk.Stack):
    """Stack with an S3 bucket for database backups."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = s3.Bucket(
            self,
            id="rootski-database-backups",
            bucket_name="rootski-database-backups",
            access_control=s3.BucketAccessControl.PRIVATE,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[
                # delete objects after 14 days
                s3.LifecycleRule(
                    enabled=True,
                    expiration=cdk.Duration.days(14),
                )
            ],
        )

        cdk.CfnOutput(
            scope=self,
            value=self.bucket.bucket_name,
            description="Name of bucket for database backups.",
            id=StackOutputs.rootski_db_backups_s3_bucket_name.value,
            export_name=StackOutputs.rootski_db_backups_s3_bucket_name.value,
        )
        cdk.CfnOutput(
            scope=self,
            value=self.bucket.bucket_arn,
            description="ARN of bucket for database backups.",
            id=StackOutputs.rootski_db_backups_s3_bucket_arn.value,
            export_name=StackOutputs.rootski_db_backups_s3_bucket_arn.value,
        )
