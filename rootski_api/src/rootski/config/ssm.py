from typing import Dict
import boto3


def get_ssm_parameters_by_prefix(prefix: str) -> Dict[str, str]:
    """
    Get all SSM parameters that start with the given prefix.

    :param prefix: Fetch all parameters with this prefix.
    """
    ssm = boto3.client("ssm")
    response = ssm.get_parameters_by_path(
        Path=prefix,
        Recursive=True,
        WithDecryption=True,
    )

    parameters = {p["Name"].split("/")[-1]: p["Value"] for p in response["Parameters"]}

    return parameters
