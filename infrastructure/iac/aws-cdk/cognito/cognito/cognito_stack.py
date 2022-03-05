"""
Cognito Stack for Rootski that enables Google log in.

I basically translated this JavaScript example to Python:
https://github.com/talkncloud/aws/blob/main/cognito-federation/lib/cognito-federation-stack.ts
"""

from pathlib import Path
from typing import Dict

import aws_cdk.aws_ssm as ssm
import yaml

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core as cdk
from aws_cdk.aws_cognito import (
    CfnUserPool,
    CfnUserPoolClient,
    CfnUserPoolDomain,
    CfnUserPoolIdentityProvider,
    PasswordPolicy,
)
from aws_cdk.core import CfnOutput, Stack

THIS_DIR = Path(__file__).parent
ROOTSKI_OAUTH_PROVIDERS_FPATH = THIS_DIR / "rootski-oauth-providers.yml"


def load_oauth_config(oauth_config_path: Path):
    with open(oauth_config_path) as f:
        oauth_config = yaml.safe_load(f)
        return oauth_config


OAUTH_CONFIG: Dict[str, str] = load_oauth_config(ROOTSKI_OAUTH_PROVIDERS_FPATH)


class CognitoStack(Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        cognito_user_pool = CfnUserPool(
            self,
            id="RootskiUserPool",
            auto_verified_attributes=["email"],
            # toggle for admin only sign up
            admin_create_user_config={"allowAdminCreateUserOnly": False},
            # verified email users can reset password
            # account_recovery_setting={
            #     "accountRecoveryMechanisms": {"name": "verified_email", "priority": 1}
            # },
            account_recovery_setting=CfnUserPool.AccountRecoverySettingProperty(
                recovery_mechanisms=[CfnUserPool.RecoveryOptionProperty(name="verified_email", priority=1)]
            ),
            username_attributes=["email"],
            # policies=CfnUserPool.PoliciesProperty([])
            # policies=CfnUserPool.PoliciesProperty(
            #     password_policy=PasswordPolicy(
            #         min_length=6,
            #         require_lowercase=False,
            #         require_uppercase=False,
            #         require_symbols=False,
            #         require_digits=False,
            #     )
            # )
            policies={
                "passwordPolicy": {
                    "minimumLength": 6,
                    "requireLowercase": True,
                    "requireUppercase": False,
                    "requireSymbols": False,
                    "requireDigits": False,
                }
            }
            # you could use a schema to cause the user to have to fill out a form,
            # that way you can require them to give an address, phone number, slack id, etc.
            # schema=[
            #     {
            #         "attributeDataType": "String",
            #         "required": False,
            #         "name": "somethingcustom",  # example of a custom attribute
            #         "mutable": True,
            #     }
            # ],
        )

        # see console.cloud.google.com -> "rootski" app -> "rootski-oauth-client"
        google_identity_provider = CfnUserPoolIdentityProvider(
            self,
            id="RootskiGoogleIdentityProvider",
            provider_name="Google",
            provider_type="Google",
            user_pool_id=cognito_user_pool.ref,
            attribute_mapping={"email": "email"},
            provider_details={
                "client_id": OAUTH_CONFIG["google"]["client_id"],
                "client_secret": OAUTH_CONFIG["google"]["client_secret"],
                "authorize_scopes": "profile email openid",
            },
        )
        # prevent race condition where it says that the rootski user pool
        # doesn't have a Google provider type
        google_identity_provider.add_depends_on(cognito_user_pool)

        # redirect users here when they log in from the Cognito hosted ui
        callback_ur_ls = ["https://www.rootski.io", "http://localhost:3000"]
        # redirect users here after they log out
        logout_ur_ls = ["https://www.rootski.io", "http://localhost:3000"]
        allowed_o_auth_scopes = [
            "email",
            "aws.cognito.signin.user.admin",
            "openid",
            "profile",
        ]
        cognito_user_pool_client = CfnUserPoolClient(
            self,
            id="RootskiCognitoUserPoolClient",
            client_name="rootski-io-cognito-client",
            user_pool_id=cognito_user_pool.ref,
            generate_secret=False,
            supported_identity_providers=[
                "COGNITO",
                google_identity_provider.provider_name,
            ],
            explicit_auth_flows=[
                "ALLOW_ADMIN_USER_PASSWORD_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
            ],
            allowed_o_auth_flows=["code"],
            allowed_o_auth_scopes=allowed_o_auth_scopes,
            allowed_o_auth_flows_user_pool_client=True,
            callback_ur_ls=callback_ur_ls,
            logout_ur_ls=logout_ur_ls,
        )

        # enable the "Hosted UI" (the UI that users get redirected to for login)
        # at rootski.auth.[region].amazoncognito.com.
        user_pool_domain = CfnUserPoolDomain(
            self,
            id="RootskiUserPoolDomain",
            domain="rootski",
            user_pool_id=cognito_user_pool.ref,
        )

        # create SSM parameters that the backend API and other sources can read
        for env in ["dev", "prod"]:

            # app client to access the user pool
            ssm.StringParameter(
                self,
                id=f"RootskiCognitoUserPoolClientId{env}",
                parameter_name=f"/rootski/{env}/cognito/cognito_web_client_id",
                string_value=cognito_user_pool_client.ref,
                type=ssm.ParameterType.STRING,
            )

            # user pool id
            ssm.StringParameter(
                self,
                id=f"RootskiCognitoUserPoolId{env}",
                parameter_name=f"/rootski/{env}/cognito/cognito_user_pool_id",
                string_value=cognito_user_pool.ref,
                type=ssm.ParameterType.STRING,
            )

            # aws region of the user pool
            ssm.StringParameter(
                self,
                id=f"RootskiCognitoUserPoolAWSRegion{env}",
                parameter_name=f"/rootski/{env}/cognito/cognito_aws_region",
                string_value=cdk.Stack.of(self).region,
                type=ssm.ParameterType.STRING,
            )

        # Outputs - these go in the aws amplify config
        CfnOutput(
            scope=self,
            id="user-pool-id",
            value=cognito_user_pool.ref,
            description="ID of the cognito user pool",
            export_name="user-pool-id",
        )
        CfnOutput(
            scope=self,
            id="user-pool-web-client-id",
            value=cognito_user_pool_client.ref,
            description="ID of the user pool web client.",
            export_name="user-pool-web-client-id",
        )
        CfnOutput(
            scope=self,
            id="hosted-ui-fqdn",
            value=".".join([user_pool_domain.domain, "auth", self.region, "amazoncognito.com"]),
            description="ID of the user pool web client.",
            export_name="hosted-ui-fqdn",
        )
        CfnOutput(
            scope=self,
            id="redirectSignIn",
            value=",".join(callback_ur_ls),
            description="ID of the user pool web client.",
            export_name="redirectSignIn",
        )
        CfnOutput(
            scope=self,
            id="redirectSignOut",
            value=",".join(logout_ur_ls),
            description="ID of the user pool web client.",
            export_name="redirectSignOut",
        )
        CfnOutput(
            scope=self,
            id="cognito-web-client-allowed-oauth-scopes",
            value=",".join(allowed_o_auth_scopes),
            description="ID of the user pool web client.",
            export_name="cognito-web-client-allowed-oauth-scopes",
        )
