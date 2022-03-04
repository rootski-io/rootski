"""Functions for reading secrets from AWS secrets manager."""

from typing import Any, Dict, Optional

import boto3


def get_secret_response_by_secret_id(secret_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Send a GET secret request with boto3 and return the response.

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
    """Fetch an AWS secrets manager secret by its ID.

    :param secret_id: ID of the secret to fetch
    :param region: AWS region to where the secret should exist
    """
    response = get_secret_response_by_secret_id(secret_id=secret_id, region=region)
    secret = response["SecretString"]
    return secret
