"""Tests to validate the functionality of the custom resource lambda handler."""

import json
import os
from typing import Callable, Literal, Union

import boto3
import pytest
from aws_lambda_typing.context import Context
from aws_lambda_typing.events import (
    CloudFormationCustomResourceCreate,
    CloudFormationCustomResourceDelete,
    CloudFormationCustomResourceEvent,
)
from jwk_cognito_custom_resource.custom_resource_handler import (
    CognitoJwksCustomResourceProps,
    create,
    delete,
    parse_region_from_stack_arn,
)
from moto import mock_cognitoidp, mock_ssm

# from .jwk_cognito_custom_resource.custom_resource import handler, create, poll_create, update, delete, CognitoJwksCustomResourceProps
from mypy_boto3_ssm import SSMClient
from mypy_boto3_ssm.type_defs import GetParameterResultTypeDef, GetParametersByPathResultTypeDef

TLambdaHandler = Callable[[CloudFormationCustomResourceEvent, Context], None]

# prevent mistakes with moto/boto3 by pointing away from real accounts
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


#####################
# --- Constants --- #
#####################

STACK_ID = "arn:aws:cloudformation:us-west-2:091910621680:stack/Cognito-JWKs-In-SSM-Parameter-Custom-Resource-CF/36444d20-c8e3-11ec-81f0-06fa347afb33"
RESOURCE_PROPERTIES = CognitoJwksCustomResourceProps(
    CognitoUserPoolId="test-pool-id",
    CognitoUserPoolRegion="us-west-2",
    SSMParameterPath="/rootski/cognito/jwks.json",
)


def create_event(
    event_type: Literal["Create", "Delete"]
) -> Union[CloudFormationCustomResourceCreate, CloudFormationCustomResourceDelete]:
    """Create a CloudFormation lifecycle event to be used in test cases."""
    return {
        "RequestType": event_type,
        "ServiceToken": "arn:aws:lambda:us-west-2:091910621680:function:Cognito-JWKs-In-SSM-Param-SSMParameterWithCognitoJ-GGOkyUUvA1f4",
        "ResponseURL": "https://cloudformation-custom-resource-response-uswest2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A091910621680%3Astack/Cognito-JWKs-In-SSM-Parameter-Custom-Resource-CF/36444d20-c8e3-11ec-81f0-06fa347afb33%7CSSMParameterWithCognitoJWKs%7C471031d4-5160-496c-9f00-6126aa96ee3d?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20220501T001223Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA54RCMT6SJTABWA2S%2F20220501%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=7b01a55a52ea74a68a3bd1075cfc25804bead538503a4f05c844005546325451",
        "StackId": STACK_ID,
        "RequestId": "471031d4-5160-496c-9f00-6126aa96ee3d",
        "LogicalResourceId": "SSMParameterWithCognitoJWKs",
        "ResourceType": "Custom::Rootski-CognitoJWKsInSSM",
        "ResourceProperties": RESOURCE_PROPERTIES,
    }


CREATE_EVENT: CloudFormationCustomResourceCreate = create_event(event_type="Create")
DELETE_EVENT: CloudFormationCustomResourceDelete = create_event(event_type="Delete")


#################
# --- Tests --- #
#################


@mock_cognitoidp
@mock_ssm
def test__create():
    """Verify that parameter creation works correctly."""
    create_parameter_with_assertions(event=CREATE_EVENT)


@mock_cognitoidp
@mock_ssm
def test__delete():
    """Verify that parameter creation works correctly."""
    create_parameter_with_assertions(event=CREATE_EVENT)
    delete_parameter_with_assertions(event=DELETE_EVENT)


############################
# --- Helper Functions --- #
############################


def fetch_ssm_parameter(name: str, region: str) -> GetParameterResultTypeDef:
    """Fetch an SSM parameter."""
    ssm_client: SSMClient = boto3.client("ssm", region_name=region)
    return ssm_client.get_parameter(Name=name)


def create_parameter_with_assertions(
    event: CloudFormationCustomResourceCreate,
) -> GetParametersByPathResultTypeDef:
    """Call the creation handler and assert that the parameter was created correctly."""
    create(event=event, context=None)

    jwks_parameter_path: str = event["ResourceProperties"]["SSMParameterPath"]
    result = fetch_ssm_parameter(name=jwks_parameter_path, region=parse_region_from_stack_arn(event["StackId"]))

    assert result["Parameter"]["Name"] == event["ResourceProperties"]["SSMParameterPath"]
    assert result["Parameter"]["Type"] == "String"

    parameter: dict = json.loads(result["Parameter"]["Value"])
    assert "keys" in parameter.keys()
    assert len(parameter["keys"]) >= 1

    return result


def delete_parameter_with_assertions(
    event: CloudFormationCustomResourceDelete,
) -> GetParametersByPathResultTypeDef:
    """Call the deletion handler on a deletion event and assert that the parameter is deleted."""
    delete(event=event, context=None)

    # you can't import errors from botocore directly >:(
    ssm_client = boto3.client("ssm")
    with pytest.raises(ssm_client.exceptions.ParameterNotFound):
        fetch_ssm_parameter(
            name=event["ResourceProperties"]["SSMParameterPath"],
            region=parse_region_from_stack_arn(event["StackId"]),
        )
