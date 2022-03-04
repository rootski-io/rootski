"""
Do realistic testing of user authentication.

These tests require:

1. AWS Cognito

  - A User Pool is spun up
  - An app/web client is registered for that user pool

2. Config

  - The ``rootski-config.yml`` file must be configured with the AWS Cognito values

3. The ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY`` env vars need to be set for an IAM user with admin access to the configured user pool
"""
from pathlib import Path
from pprint import pprint
from typing import Tuple

import boto3
import pytest

from rootski.config.config import YAML_CONFIG_PATH_ENV_VAR, Config
from rootski.services.auth import AuthService
from tests.constants import TEST_USER
from tests.utils import scoped_env_vars

THIS_DIR = Path(__file__).parent
ROOTSKI_CONFIG_YAML_FPATH: Path = (
    (THIS_DIR / ".." / ".." / ".." / "config" / "rootski-config.yml").resolve().absolute()
)

# the scope of this fixture must be session to match the jwt_id_token scope
@pytest.fixture(scope="session")
def config() -> Config:
    with scoped_env_vars({YAML_CONFIG_PATH_ENV_VAR: str(ROOTSKI_CONFIG_YAML_FPATH)}):
        config = Config()
        yield config


@pytest.fixture(scope="session")
def jwt_id_token(config: Config) -> str:
    # create a real confirmed user in the Cognito User Pool
    try:
        delete_cognito_user(user_pool_id=config.cognito_user_pool_id, email=TEST_USER["email"])
    except boto3.client("cognito-idp").exceptions.UserNotFoundException as e:
        print("No user to delete")
    register_cognito_user(
        email=TEST_USER["email"],
        password=TEST_USER["password"],
        app_client_id=config.cognito_web_client_id,
    )
    confirm_user_email(user_pool_id=config.cognito_user_pool_id, username=TEST_USER["email"])
    jwt_access_token, jwt_id_token, jwt_refresh_token = sign_in_user(
        email=TEST_USER["email"],
        password=TEST_USER["password"],
        user_pool_id=config.cognito_user_pool_id,
        app_client_id=config.cognito_web_client_id,
    )
    yield jwt_id_token
    # clean up the user
    delete_cognito_user(user_pool_id=config.cognito_user_pool_id, email=TEST_USER["email"])


#########################################
# --- Helper functions for fixtures --- #
#########################################


def register_cognito_user(email: str, password: str, app_client_id: str):
    """
    Raises:
        ClientError: if the user can't be signed up; for example, the user
            may already exist or the app_client_id could be wrong
    """
    cognito_idp = boto3.client("cognito-idp")
    # Add user to pool
    sign_up_response = cognito_idp.sign_up(
        ClientId=app_client_id,
        Username=email,
        Password=password,
        UserAttributes=[{"Name": "email", "Value": email}],
    )
    pprint(sign_up_response)


def confirm_user_email(user_pool_id: str, username: str):
    """Confirm a user's email address. For rootski, the ``username`` is their email."""
    cognito_idp = boto3.client("cognito-idp")
    print("    Confirming user...")
    # Use Admin powers to confirm user. Normally the user would
    # have to provide a code or click a link received by email
    confirm_sign_up_response = cognito_idp.admin_confirm_sign_up(UserPoolId=user_pool_id, Username=username)
    pprint(confirm_sign_up_response)


def sign_in_user(email: str, password: str, user_pool_id: str, app_client_id: str) -> Tuple[str, str, str]:
    cognito_idp = boto3.client("cognito-idp")

    # This is less secure, but simpler
    response = cognito_idp.admin_initiate_auth(
        AuthFlow="ADMIN_NO_SRP_AUTH",
        AuthParameters={"USERNAME": email, "PASSWORD": password},
        UserPoolId=user_pool_id,
        ClientId=app_client_id,
    )
    print("----- Log in response -----")
    pprint(response)
    print("---------------------------")
    # AWS official docs on using tokens with user pools:
    # https://amzn.to/2HbmJG6
    # If authentication was successful we got three tokens
    jwt_access_token = response["AuthenticationResult"]["AccessToken"]
    jwt_id_token = response["AuthenticationResult"]["IdToken"]
    jwt_refresh_token = response["AuthenticationResult"]["RefreshToken"]

    return jwt_access_token, jwt_id_token, jwt_refresh_token


def delete_cognito_user(user_pool_id: str, email: str):
    cognito_idp = boto3.client("cognito-idp")
    cognito_idp.admin_delete_user(UserPoolId=user_pool_id, Username=email)


######################
# --- Test cases --- #
######################


def test__auth_service(config: Config, jwt_id_token: str):
    auth_service = AuthService.from_config(config=config)
    auth_service.init()
    assert auth_service.token_is_valid(jwt_id_token)
    assert auth_service.get_token_email(jwt_id_token) == TEST_USER["email"]
