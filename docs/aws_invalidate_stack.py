"""
CLI script that invalidates the CloudFront cache in an S3 Static Site script.

See rootski/infrastructure/iac/aws-cdk/backend/s3_static_site/
to understand how the stack is built.
"""

import argparse
from pathlib import Path
from textwrap import dedent
from time import time
from typing import Any, Dict, NamedTuple, Optional, TypeVar

import boto3

CLOUDFRONT_ID__OUTPUT_KEY_IN_STATIC_SITE_STACK = "CloudfrontID"
AWS_CREDENTIALS_PATH = Path.home() / ".aws/credentials"

TCloudFormationClient = TypeVar("TCloudFormationClient")
TCloudFrontClient = TypeVar("TCloudFrontClient")


class TArguments(NamedTuple):
    """Type for arguments parsed with argparse."""

    s3_static_site_stack_name: str
    region: Optional[str] = None
    profile: Optional[str] = None


class NoStackOutputFound(Exception):
    """Raised when an output value requested for a stack cannot be found."""


def main():
    """Parse the CLI arguments and invalidate the CloudFront cache."""
    args: TArguments = parse_args()
    invalidate_cache_from_stack(
        stack_name=args.s3_static_site_stack_name,
        region=args.region,
        profile=args.profile,
    )


def parse_args() -> TArguments:
    """
    Parse arguments used for invalidating the cache.

    .. note::

        In :py:mod:`argparse`, simply prefixing an argument name with ``--``
        makes it optional. Unless the ``default`` argument is set, it defaults
        to ``None``.
    """
    parser = argparse.ArgumentParser(
        description="Invalidate the CDN cache for an S3 static site."
    )
    parser.add_argument(
        "--s3-static-site-stack-name",
        type=str,
        help="AWS CloudFormation stack name of static site",
    )
    parser.add_argument(
        "--region",
        type=str,
        help="AWS region override, if not provided, the profile or default will be used.",
    )
    parser.add_argument(
        "--profile",
        type=str,
        help=dedent(
            """\
            AWS profile override. If not provided, the default
            profile will be used. If there is no ~/.aws/credentials file,
            environment variables or IAM role will be used.\
            """
        ),
    )
    args: TArguments = parser.parse_args()
    return args


def invalidate_cache_from_stack(
    stack_name: str, region: Optional[str] = None, profile: Optional[str] = None
):
    """Invalidate the CloudFront distribution for an S3StaticSiteStack.

    :param stack_name: Name of the S3StaticSiteStack instance
    :param region: region the stack is deployed in
    :param profile: AWS profile to get credentials from if credentials file exists
    """
    cloudformation_client: TCloudFormationClient = get_cloudformation_client(
        region=region, profile=profile
    )
    cloudfront_client: TCloudFrontClient = get_cloudfront_client(
        region=region, profile=profile
    )
    cloudfront_distribution_id: str = get_cloudformation_stack_output(
        cf_client=cloudformation_client,
        stack_name=stack_name,
        output_key=CLOUDFRONT_ID__OUTPUT_KEY_IN_STATIC_SITE_STACK,
    )
    print(
        f'Invalidating CloudFront distrubition cache with id "{cloudfront_distribution_id}"'
    )
    invalidation_status: str = invalidate_cloudfront_distribution_cache(
        cloudfront_client=cloudfront_client, distribution_id=cloudfront_distribution_id
    )
    print(f"Request successful. Invalidation status: {invalidation_status}")


def invalidate_cloudfront_distribution_cache(
    cloudfront_client: TCloudFrontClient, distribution_id: str, path: str = "/*"
) -> str:
    """
    Create a cloudfront invalidation.

    :param distribution_id: ID of the cloudfront distrubution whose cache will be invalidated.
    :param path: path to invalidate, can use wildcard eg. ``/*`` means all path

    :return: invalidation id
    """
    response: Dict[str, Any] = cloudfront_client.create_invalidation(
        DistributionId=distribution_id,
        InvalidationBatch={
            "Paths": {"Quantity": 1, "Items": [path]},
            "CallerReference": str(time()).replace(".", ""),
        },
    )
    invalidation_status = response["Invalidation"]["Status"]
    return invalidation_status


def get_boto_session(
    region: Optional[str] = None, profile: Optional[str] = None
) -> boto3.session.Session:
    """Prepare a boto Session object to create clients with the desired credentials.

    If AWS credentials file does not exist, the profile will be ignored.

    :param region: default region for boto operations
    :param profile: profile to pull credentials from
    :return: Session with credentials
    """
    session: Optional[boto3.session.Session] = None
    session_kwargs = {
        "region_name": region,
    }
    if AWS_CREDENTIALS_PATH.exists():
        session_kwargs.update({"profile_name": profile})
    session = boto3.session.Session(**session_kwargs)
    return session


def get_cloudformation_client(
    region: Optional[str] = None, profile: Optional[str] = None
) -> TCloudFormationClient:
    """Prepare a client to perform CloudFormation operations.

    :param region: default region for boto operations
    :param profile: profile to pull credentials from
    :return: cloudformation client
    """
    session: boto3.session.Session = get_boto_session(region=region, profile=profile)
    return session.client("cloudformation")


def get_cloudfront_client(
    region: Optional[str] = None, profile: Optional[str] = None
) -> TCloudFrontClient:
    """Prepare a client to perform CloudFront operations.

    :param region: default region for boto operations
    :param profile: profile to pull credentials from
    :return: CloudFront client
    """
    session: boto3.session.Session = get_boto_session(region=region, profile=profile)
    return session.client("cloudfront")


def get_cloudformation_stack_output(
    cf_client: TCloudFormationClient, stack_name: str, output_key: str
) -> str:
    """Fetch a single stack output from a CloudFormation stack.

    :param cf_client: Client for CloudFormation operations
    :param stack_name: name of the stack to fetch a value from
    :param output_key: name of the output stack key to fetch the valoe of
    :raises NoStackOutputFound: if the stack does not have an output named ``output_key``
    :return: string value of the output key
    """
    response: Dict[str, Any] = cf_client.describe_stacks(StackName=stack_name)
    outputs = response["Stacks"][0]["Outputs"]
    for output in outputs:
        key_name: str = output["OutputKey"]
        if key_name == output_key:
            return output["OutputValue"]

    raise NoStackOutputFound(f'Output with key "{output_key}" not found.')


if __name__ == "__main__":
    main()


# cf_client = boto3.client("cloudformation")
