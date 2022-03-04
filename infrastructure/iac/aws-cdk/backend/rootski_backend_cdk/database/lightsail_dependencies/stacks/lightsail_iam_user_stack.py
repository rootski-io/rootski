"""Stack defining an IAM user for the lightsail instance."""

from enum import Enum

from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_ssm as ssm
from aws_cdk import core as cdk

ROOTSKI_PRIVATE_KEY_SSM_PARAMETER_KEY = "/rootski/ssh/private-key"


class StackOutputs(str, Enum):
    """Stack outputs for the :py:class:`LightsailIAMUserStack`."""

    # pylint: disable=invalid-name
    rootski_iam_user_secret_key_id__secret_arn = "RootskiIAMUserSecretKeyIdSecretARN"
    rootski_iam_user_secret_key__secret_arn = "RootskiIAMUserSecretKeySecretARN"


class LightsailIAMUserStack(cdk.Stack):
    """
    An IAM user to be used on the rootski lightsail instance.

    An IAM key pair is generated for the user and stored in secrets manager.
    The key pair can be retrieved and placed in the ``/home/ec2-user/.aws/credentials``
    file on the rootski lightsail instance.
    """

    def __init__(self, scope: cdk.Construct, construct_id: str, rootski_db_bucket: s3.Bucket, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        group = iam.Group(
            self,
            id="rootski-lightsail-group",
            group_name="rootski-lightsail-group",
        )

        user = iam.User(
            self,
            id="rootski-lightsail-user",
            user_name="rootski-lightsail-user",
        )

        user.add_to_group(group)

        rootski_private_key_ssm_param = ssm.StringParameter.from_string_parameter_name(
            scope=self,
            id="rootski-private-key-ssm-param",
            string_parameter_name=ROOTSKI_PRIVATE_KEY_SSM_PARAMETER_KEY,
        )
        rootski_private_key_ssm_param.grant_read(group)

        rootski_db_bucket.grant_read_write(group)

        access_key = iam.AccessKey(self, id="rootski-lightsail-user-access-key", user=user)
        # ssm.StringParameter(
        #     self,
        #     id="rootski-iam-user-secret-key-id",
        #     parameter_name="rootski-iam-user-secret-key-id",
        #     string_value=access_key.access_key_id,
        #     description="IAM secret key ID granting the rootski-iam-user programmatic access.",
        # )
        # ssm.StringParameter(
        #     self,
        #     id="rootski-iam-user-secret-key-id",
        #     parameter_name="rootski-iam-user-secret-key-id",
        #     string_value=access_key.secret_access_key,
        #     description="IAM secret key granting the rootski-iam-user programmatic access.",
        # )

        access_key_id = secretsmanager.SecretStringValueBeta1.from_token(access_key.access_key_id)
        self.access_key_id = secretsmanager.Secret(
            self,
            id="rootski-iam-user-secret-key-id",
            # secret_name="rootski-iam-user-secret-key-id",
            description="IAM secret key ID granting the rootski-iam-user programmatic access.",
            secret_string_beta1=access_key_id,
        )

        access_key = secretsmanager.SecretStringValueBeta1.from_token(access_key.secret_access_key.to_string())
        self.access_key = secretsmanager.Secret(
            self,
            id="rootski-iam-user-secret-key",
            # secret_name=cfn_format_name("rootski-iam-user-secret-key"),
            description="IAM secret key granting the rootski-iam-user programmatic access.",
            secret_string_beta1=access_key,
        )

        cdk.CfnOutput(
            self,
            id=StackOutputs.rootski_iam_user_secret_key_id__secret_arn.value,
            value=self.access_key_id.secret_arn,
            export_name=StackOutputs.rootski_iam_user_secret_key_id__secret_arn.value,
        )
        cdk.CfnOutput(
            self,
            id=StackOutputs.rootski_iam_user_secret_key__secret_arn.value,
            value=self.access_key.secret_arn,
            export_name=StackOutputs.rootski_iam_user_secret_key__secret_arn.value,
        )
