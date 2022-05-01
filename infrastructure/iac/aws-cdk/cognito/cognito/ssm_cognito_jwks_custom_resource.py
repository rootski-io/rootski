"""Stack containing a custom resource and instance of the custom resource to save JWKs in SSM."""

from pathlib import Path
from typing import TypedDict

import aws_cdk as cdk
from aws_cdk import CustomResource, Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import custom_resources
from constructs import Construct

THIS_DIR = Path(__file__).parent
CUSTOM_RESOURCE_LAMBDA_DIR = (THIS_DIR / "./resources/jwks_ssm_custom_resource_lambda").resolve().absolute()


class CognitoJwksCustomResourceProps(TypedDict):
    """Properties for the CognitoJwksCustomResource."""

    CognitoUserPoolId: str
    CognitoUserPoolRegion: str
    SSMParameterPath: str


class SSMParameterWithCognitoJWKsStack(Stack):
    """Custom resource that stores cognito JSON Web Keys in an SSM Parameter."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        cognito_user_pool_id: str,
        cognito_user_pool_region: str,
        cognito_jwks_ssm_parameter_path: str,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        #: lambda function that processes CloudFormation custom resource lifecycle events
        self.on_event__lambda_handler: lambda_.Function = self.make__on_event__lambda_handler()

        #: wrapper for the on_event__lambda_handler used to create instances of the custom resource
        self.custom_resource_provider = custom_resources.Provider(
            self,
            "SSM-Parameter-With-Cognito-JWKs-Provider",
            on_event_handler=self.on_event__lambda_handler,
        )

        #: instance of custom resource with information about a particular cognito user pool
        self.ssm_parameter_with_cognito_jwks = CustomResource(
            self,
            "SSM-Parameter-With-Cognito-JWKs",
            service_token=self.custom_resource_provider.service_token,
            resource_type="Custom::Rootski-CognitoJWKsInSSM",
            properties=CognitoJwksCustomResourceProps(
                CognitoUserPoolId=cognito_user_pool_id,
                CognitoUserPoolRegion=cognito_user_pool_region,
                SSMParameterPath=cognito_jwks_ssm_parameter_path,
            ),
        )

    def make__on_event__lambda_handler(self):
        """
        Create a lambda function that processes CloudFormation custom resource lifecycle events.

        These events include Create, Read, Update, and Delete operations on the
        SSM parameter that is created by this custom resource.
        """
        on_event__lambda_handler = lambda_.Function(
            self,
            "Rootski-FastAPI-Lambda",
            timeout=cdk.Duration.seconds(30),
            memory_size=256,
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="jwk_cognito_custom_resource.custom_resource_handler.handler",
            code=lambda_.Code.from_asset(
                path=str(CUSTOM_RESOURCE_LAMBDA_DIR),
                bundling=cdk.BundlingOptions(
                    # learn about this here:
                    # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/README.html#bundling-asset-code
                    # Using this lambci image makes it so that dependencies with C-binaries compile correctly for the lambda runtime.
                    # The AWS CDK python images were not doing this.
                    image=cdk.DockerImage.from_registry(image="lambci/lambda:build-python3.8"),
                    command=[
                        "bash",
                        "-c",
                        "mkdir -p /asset-output /asset-input"
                        + "&& pip install /asset-input/ -t /asset-output/"
                        + "&& rm -rf /asset-output/boto3 /asset-output/botocore",
                    ],
                ),
            ),
        )

        # allow lambda to do CRUD operations of the SSM parameter created by this resource
        on_event__lambda_handler.role.attach_inline_policy(
            policy=iam.Policy(
                self,
                id="Allow-Lambda-Access-To-SSM-Params",
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        resources=[
                            "arn:aws:ssm:{region}:{account}:parameter/rootski/cognito*".format(
                                region=cdk.Stack.of(self).region,
                                account=cdk.Stack.of(self).account,
                            )
                        ],
                        actions=[
                            # create the SSM parameter
                            "ssm:Put*",
                            # delete the SSM parameter
                            "ssm:Delete*",
                            # read the SSM parameter to verify that it was deleted
                            "ssm:Get*",
                        ],
                    )
                ],
            )
        )

        on_event__lambda_handler.role.add_managed_policy(
            policy=iam.ManagedPolicy.from_managed_policy_arn(
                self,
                id="Allow-Lambda-To-Connect-To-Lightsail-VPC-via-VPC-Peering",
                managed_policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
            )
        )

        return on_event__lambda_handler
