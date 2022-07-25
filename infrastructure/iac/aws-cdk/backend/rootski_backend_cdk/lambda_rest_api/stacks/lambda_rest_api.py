"""Stack defining an API Gateway mapping to a Lambda function with the FastAPI app."""

from enum import Enum
from pathlib import Path

from aws_cdk import aws_apigateway as api_gateway
from aws_cdk import aws_certificatemanager as certificatemanager
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_s3 as s3
import aws_cdk as cdk

API_SUBDOMAIN = "api.rootski.io"

THIS_DIR = Path(__file__).parent
# ROOTSKI_LAMBDA_CODE_DIR = THIS_DIR / "resources"
ROOTSKI_LAMBDA_CODE_DIR = THIS_DIR / "../../../../../../../rootski_api"

# Must be the same version as in the fast api root path
ROOTSKI_API_VERSION = "v1"


class StackOutputs(str, Enum):
    """Stack output keys for the :py:class:`RootskiLambdaRestApiStack`."""

    # pylint: disable=invalid-name
    api_gateway_url = "ApiGatewayUrl"
    subdomain = "ApiSubdomain"


class RootskiLambdaRestApiStack(cdk.Stack):
    """An API Gateway mapping to a Lambda function with the backend code inside."""

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        fast_api_function: lambda_.Function = self.make_fast_api_function()

        lambda_rest_api = api_gateway.LambdaRestApi(
            self,
            "Rootski-Lambda-REST-API",
            handler=fast_api_function,
            description="Proxy to the Rootski FastAPI backend 'lambda-lith'.",
            domain_name=api_gateway.DomainNameOptions(
                certificate=certificatemanager.DnsValidatedCertificate(
                    self,
                    id="Rootski-Lambda-DNS-Validated-ACM-Cert",
                    domain_name=API_SUBDOMAIN,
                    hosted_zone=route53.HostedZone.from_lookup(
                        self, id="Rootski-IO-Hosted-Zone", domain_name="rootski.io"
                    ),
                ),
                domain_name=API_SUBDOMAIN,
            ),
        )

        route53.ARecord(
            self,
            id="Rootski-IO-API-Gateway-A-Record",
            zone=route53.HostedZone.from_lookup(
                self,
                id="Rootski-IO-API-Gateway-HostedZone",
                domain_name="rootski.io",
            ),
            target=route53.RecordTarget.from_alias(route53_targets.ApiGateway(lambda_rest_api)),
            record_name=API_SUBDOMAIN,
        )

        cdk.CfnOutput(
            self,
            id=StackOutputs.subdomain.value,
            value=API_SUBDOMAIN,
            description=f"Map {lambda_rest_api} to the URL of the API Gateway",
            export_name=StackOutputs.subdomain.value,
        )

        cdk.CfnOutput(
            scope=self,
            value=lambda_rest_api.url,
            description="ARN of bucket for database backups.",
            id=StackOutputs.api_gateway_url.value,
            export_name=StackOutputs.api_gateway_url.value,
        )

    def make_fast_api_function(self) -> lambda_.Function:
        """
        Create a lambda function with the FastAPI app.

        To prepare the python depencies for the lambda function, this stack
        will essentially run the following command:

        .. code:: bash

            docker run \
                --rm \
                -v "path/to/rootski_api:/assets_input" \
                -v "path/to/cdk.out/asset.<some hash>:/assets_output" \
                lambci/lambda:build-python3.8 \
                /bin/bash -c "... several commands to install the requirements to /assets_output ..."

        The reason for using docker to install the requirements is because the "lambci/lambda:build-pythonX.X" image
        uses the same underlying operating system as is used in the real AWS Lambda runtime. This means that
        python packages that rely on compiled C/C++ binaries will be compiled correctly for the AWS Lambda runtime.
        If we did not do it this way, packages such as pandas, numpy, psycopg2-binary, asyncpg, sqlalchemy, and others
        relying on C/C++ bindings would not work when uploaded to lambda.

        We use the ``lambci/*`` images instead of the images maintained by AWS CDK because the AWS CDK images
        were failing to correctly install C/C++ based python packages. An extra benefit of using ``lambci/*`` over
        the AWS CDK images is that the ``lambci/*`` images are in docker hub so they can be pulled without doing any
        sort of ``docker login`` command before executing this script. The AWS CDK images are stored in public.ecr.aws
        which requires a ``docker login`` command to be run first.
        """
        # create a bucket to cache the morphemes.json object
        morphemes_json_bucket = s3.Bucket(
            self,
            id="Rootski-Backend-Cache-Bucket",
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        fast_api_function = lambda_.Function(
            self,
            "Rootski-FastAPI-Lambda",
            timeout=cdk.Duration.seconds(30),
            memory_size=512,
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="index.handler",
            code=lambda_.Code.from_asset(
                path=str(ROOTSKI_LAMBDA_CODE_DIR),
                bundling=cdk.BundlingOptions(
                    # learn about this here:
                    # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/README.html#bundling-asset-code
                    # Using this lambci image makes it so that dependencies with C-binaries compile correctly for the lambda runtime.
                    # The AWS CDK python images were not doing this. Relevant dependencies are: pandas, asyncpg, and psycogp2-binary.
                    image=cdk.DockerImage.from_registry(image="lambci/lambda:build-python3.8"),
                    command=[
                        "bash",
                        "-c",
                        "mkdir -p /asset-output"
                        + "&& pip install -r ./aws-lambda/requirements.txt -t /asset-output"
                        + "&& pip install . -t /asset-output"
                        + "&& cp aws-lambda/index.py /asset-output"
                        + "&& rm -rf /asset-output/boto3 /asset-output/botocore",
                    ],
                ),
            ),
            environment={
                "ROOTSKI__FETCH_VALUES_FROM_AWS_SSM": "true",
                "ROOTSKI__ENVIRONMENT": "prod",
                # /tmp is the only writable location in the lambda file system
                "ROOTSKI__STATIC_ASSETS_DIR": "/tmp",
                "ROOTSKI__OBJECT_CACHE_BUCKET_NAME": morphemes_json_bucket.bucket_name,
            },
        )

        morphemes_json_bucket.grant_read_write(fast_api_function)

        # allow lambda to perform GetParametersByPath operation on the /rootski* parameters
        fast_api_function.role.attach_inline_policy(
            policy=iam.Policy(
                self,
                id="Allow-Lambda-Access-To-SSM-Params",
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        resources=[
                            "arn:aws:ssm:{region}:{account}:parameter/rootski*".format(
                                region=cdk.Stack.of(self).region,
                                account=cdk.Stack.of(self).account,
                            )
                        ],
                        actions=["ssm:Get*"],
                    )
                ],
            )
        )
        fast_api_function.role.add_managed_policy(
            policy=iam.ManagedPolicy.from_managed_policy_arn(
                self,
                id="Allow-Lambda-To-Connect-To-Lightsail-VPC-via-VPC-Peering",
                managed_policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
            )
        )

        return fast_api_function
