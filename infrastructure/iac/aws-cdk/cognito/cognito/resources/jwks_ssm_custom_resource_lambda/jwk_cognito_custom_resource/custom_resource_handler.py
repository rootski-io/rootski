"""
Lambda function that handles CloudFormaiton custom resource lifecycle events.

Context: the backend rootski API runs in an isolated VPC network without internet
access. Due to this, the backend is not able to hit the public AWS endpoint
to fetch the JSON Web Keys used to validate JWT tokens issued by the rootski
Cognito User Pool.

However, the rootski API *is* able to access AWS SSM, including AWS SSM Parameter Store.
This lambda function defines a custom resource that performs an HTTP request to
the cognito URL to fetch the JWKs and then stores those in an SSM parameter.

Thanks to this, the rootski API code can fetch the JWKs from SSM.

.. note::

    The CDK docs to a good job of explaining how to write
    a custom resource lambda handler:
    https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.custom_resources-readme.html#provider-framework

    This file uses an official, AWS-maintained framework called ``crhelper``
    to help structure the lifecycle handler functions with best practices:
    https://github.com/aws-cloudformation/custom-resource-helper
"""

import json
import re
from typing import Match, TypedDict
from uuid import uuid4

import boto3
import requests
from aws_lambda_typing.context import Context
from aws_lambda_typing.events import (
    CloudFormationCustomResourceCreate,
    CloudFormationCustomResourceDelete,
    CloudFormationCustomResourceEvent,
    CloudFormationCustomResourceUpdate,
)
from crhelper import CfnResource
from mypy_boto3_ssm import SSMClient
from mypy_boto3_ssm.type_defs import DeleteParametersResultTypeDef, PutParameterResultTypeDef

# Initialise the helper, all inputs are optional, this example shows the defaults
helper = CfnResource(
    json_logging=False, log_level="DEBUG", boto_level="CRITICAL", sleep_on_delete=120, ssl_verify=False
)


class CognitoJwksCustomResourceProps(TypedDict):
    """Properties for the CognitoJwksCustomResource."""

    CognitoUserPoolId: str
    CognitoUserPoolRegion: str
    SSMParameterPath: str


try:
    # Init code goes here
    pass
# pylint: disable=broad-except
except Exception as e:
    helper.init_failure(e)


###################################
# --- Custom Resource Handler --- #
###################################


def handler(event: CloudFormationCustomResourceEvent, context: Context):
    """Use the ``crhelper`` framework to call ``create()``, ``update()`` or ``delete()`` based on the ``event`` type."""
    helper(event, context)


##################################
# --- Event Handlers by Type --- #
##################################

# pylint: disable=unused-argument
@helper.create
def create(event: CloudFormationCustomResourceCreate, context: Context) -> str:
    """Fetch the Cognito JSON Web Keys and create an SSM parameter containg them."""
    print("Got Create")
    props: CognitoJwksCustomResourceProps = event["ResourceProperties"]

    cognito_user_pool_jwks: dict = request_jwks(
        cognito_aws_region=props["CognitoUserPoolRegion"],
        cognito_user_pool_id=props["CognitoUserPoolId"],
    )

    stack_region: str = parse_region_from_stack_arn(event["StackId"])
    create_ssm_parameter(
        name=props["SSMParameterPath"],
        value=json.dumps(cognito_user_pool_jwks, indent=2),
        region=stack_region,
    )

    helper.Data.update(
        {
            "ParameterPath": props["SSMParameterPath"],
        }
    )

    return str(uuid4())


# pylint: disable=unused-argument
@helper.update
def update(event: CloudFormationCustomResourceUpdate, context: Context) -> str:
    """
    Update the Cognito user pool JWKS.

    If the update resulted in a new resource being created,
    return an id for the new resource. CloudFormation will send a
    delete event with the old id when stack update completes.
    """
    print("Got Update")
    props: CognitoJwksCustomResourceProps = event["ResourceProperties"]

    helper.Data.update(
        {
            "ParameterPath": props["SSMParameterPath"],
        }
    )

    return event["PhysicalResourceId"]


# pylint: disable=unused-argument
@helper.delete
def delete(event: CloudFormationCustomResourceDelete, context: Context):
    """
    Delete the SSM Parameter containing Cognito user pool JWKS.

    Delete never returns anything. Should not fail if the underlying
    resources are already deleted. Desired state.
    """
    print("Got Delete")

    stack_region: str = parse_region_from_stack_arn(event["StackId"])
    props: CognitoJwksCustomResourceProps = event["ResourceProperties"]

    delete_ssm_parameter(
        name=props["SSMParameterPath"],
        region=stack_region,
    )


# pylint: disable=unused-argument
@helper.poll_create
def poll_create(event, context):
    """
    Return a resource id or True to indicate that creation is complete.

    If True is returned an id will be generated.
    """
    print("Got create poll")
    return True


############################
# --- Helper Functions --- #
############################


def parse_region_from_stack_arn(arn: str) -> str:
    """Parse the region from the stack ``arn``."""
    pattern = r"arn:aws:cloudformation:(?P<region>.*):(?P<account_id>.*):stack/(?P<stack_name>.*)/(?P<guid>.*)"
    match: Match = re.match(pattern=pattern, string=arn)
    region = match.group("region")
    return region


def make_jwks_url(cognito_aws_region: str, cognito_user_pool_id: str) -> str:
    """Make a URL to the Cognito user pool JWKS."""
    return (
        f"https://cognito-idp.{cognito_aws_region}.amazonaws.com/{cognito_user_pool_id}/.well-known/jwks.json"
    )


def request_jwks(cognito_aws_region: str, cognito_user_pool_id: str) -> dict:
    """Request the JWKS from the Cognito user pool."""
    cognito_user_pool_jwks_url: str = make_jwks_url(
        cognito_aws_region=cognito_aws_region, cognito_user_pool_id=cognito_user_pool_id
    )
    response = requests.get(cognito_user_pool_jwks_url)
    return response.json()


def create_ssm_parameter(name: str, value: str, region: str) -> PutParameterResultTypeDef:
    """Create an SSM parameter with the given name and value."""
    ssm_client: SSMClient = boto3.client("ssm", region_name=region)
    parameter: PutParameterResultTypeDef = ssm_client.put_parameter(
        Name=name,
        Value=value,
        Type="String",
        Overwrite=False,
    )

    return parameter


def delete_ssm_parameter(name: str, region: str) -> DeleteParametersResultTypeDef:
    """Delete an SSM parameter with the given name and value."""
    ssm_client: SSMClient = boto3.client("ssm", region_name=region)
    response: DeleteParametersResultTypeDef = ssm_client.delete_parameter(
        Name=name,
    )

    return response
