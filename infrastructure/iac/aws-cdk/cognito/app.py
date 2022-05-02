#!/usr/bin/env python3

import aws_cdk as cdk
from cognito.cognito_stack import CognitoStack
from cognito.ssm_cognito_jwks_custom_resource import SSMParameterWithCognitoJWKsStack

app = cdk.App()

cognito_stack = CognitoStack(
    app,
    "RootksiCognitoStack",
)

SSMParameterWithCognitoJWKsStack(
    app,
    "Cognito-JWKs-In-SSM-Parameter-Custom-Resource-CF",
    cognito_user_pool_id=cognito_stack.cognito_user_pool.ref,
    cognito_user_pool_region=cognito_stack.region,
    cognito_jwks_ssm_parameter_path="/rootski/cognito/jwks.json",
)

app.synth()
