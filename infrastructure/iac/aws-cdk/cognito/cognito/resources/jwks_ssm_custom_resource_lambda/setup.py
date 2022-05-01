"""Define a package for the SSM-Cognito-JWK custom resource."""

from setuptools import find_packages, setup

setup(
    name="jwk_cognito_custom_resource",
    package_dir={"": "."},
    packages=find_packages(),
    install_requires=[
        "requests",
        # framework for writing Lambda-backed AWS custom resources
        "crhelper==2.0.10",
        # community-maintained types for AWS Lambda function arguments
        "aws-lambda-typing==2.10.1",
        # community-maintained types for AWS SSM
        "boto3-stubs[ssm]",
    ],
)
