from typing import Any, Dict, Optional
import boto3
from rootski_backend_cdk.common.outputs import get_stack_outputs


def get_secret_response_by_secret_id(secret_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    :param secret_id: the secret ID or ARN of the secret to retrieve

    :returns: object of the form

        .. code-block:: json

            {
                "ARN": "arn:aws:secretsmanager:us-west-2:xxx:secret:my-test-secret-str-k4sx86",
                "Name": "my-test-secret-str",
                "VersionId": "490a3ce1-c3d1-496a-b65e-cde9b8a7631c",
                "SecretString": "test-secret-str",
                "VersionStages": ["AWSCURRENT"],
                "CreatedDate": "datetime.datetime(2021, 2, 26, 21, 35, 32, 273000, tzinfo=tzlocal())",
                "ResponseMetadata":
                    {
                        "RequestId": "64163213-1f39-430a-9ad2-816983695e51",
                        "HTTPStatusCode": 200,
                        "HTTPHeaders": {"date": "Sat, 27 Feb 2021 05:56:38 GMT",
                        "content-type": "application/x-amz-json-1.1",
                        "content-length": "262",
                        "connection": "keep-alive",
                        "x-amzn-requestid": "64163213-1f39-430a-9ad2-816983695e51"},
                        "RetryAttempts": 0
                    }
            }
    """
    secrets_client = boto3.client("secretsmanager", region_name=region)
    kwargs = {"SecretId": secret_id}
    response = secrets_client.get_secret_value(**kwargs)
    return response


def get_secret_by_id(secret_id: str, region: Optional[str] = None) -> str:
    response = get_secret_response_by_secret_id(secret_id=secret_id, region=region)
    secret = response["SecretString"]
    return secret


def get_secret_by_arn_in_stack_output(
    stack_name: str, secret_arn_output_key: str, region: Optional[str] = None
) -> str:
    """
    :param stack_name: name of a CFN stack with an output containing a secret ID
    :param secret_id_output_key: an output key (export name) for the stack whose value is a secret ID

    :returns: the secret pointed to by the stack output
    """
    stack_outputs: Dict[str, str] = get_stack_outputs(stack_name=stack_name, region=region)
    secret_arn: str = stack_outputs[secret_arn_output_key]
    secret: str = get_secret_by_id(secret_arn=secret_arn, region=region)
    return secret
