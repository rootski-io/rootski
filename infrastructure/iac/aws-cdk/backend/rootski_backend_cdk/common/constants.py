from aws_cdk import CfnTag
from enum import Enum

TAGS = [
    CfnTag(key="app", value="rootski"),
]


class StackNames(str, Enum):
    # lightsail dependencies
    db_backups_bucket = "Rootski-Database-Backups-Bucket-cdk"
    iam_user = "Rootski-Lightsail-IAM-User-cdk"

    # lightsail
    lightsail_instance = "Rootski-Database-Stack-cdk"
