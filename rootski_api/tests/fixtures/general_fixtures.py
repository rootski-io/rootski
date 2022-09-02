"""
Non specific fixtures for use across all tests.

This fixture is accessible to all tests due to its inclusion in conftest.py.

see: https://docs.pytest.org/en/6.2.x/fixture.html
"""

from typing import Optional

import pytest
from fastapi import FastAPI
from rootski.config.config import DEPLOYMENT_ENVIRONMENT_ENV_VAR, FETCH_VALUES_FROM_SSM_ENV_VAR, Config
from rootski.main import deps
from rootski.main.deps import register_user
from rootski.main.main import create_app
from rootski.schemas.core import Services
from rootski.services.database import DBService
from rootski.services.database import models as orm
from rootski.services.database.dynamo.db_service import DBService as DynamoDBService
from sqlalchemy.orm import Session
from starlette.testclient import TestClient
from tests.constants import CONFIG_VALUES_FOR_REAL_DATABASE, ROOTSKI_DYNAMO_TABLE_NAME, TEST_USER
from tests.mocks import MockService
from tests.utils import scoped_env_vars

####################
# --- Fixtures --- #
####################


@pytest.fixture
def db_service() -> DBService:
    """Get a SQL Connection to a fresh database with all Rootski tables ready."""
    env_vars = {
        # fetch actual "dev" parameters from parameter store for tests
        DEPLOYMENT_ENVIRONMENT_ENV_VAR: "dev",
        FETCH_VALUES_FROM_SSM_ENV_VAR: "true",
    }
    with scoped_env_vars(env_vars=env_vars):
        # connect to the test database and ping it
        config = Config(**CONFIG_VALUES_FOR_REAL_DATABASE)
        db_service = DBService.from_config(config=config)
        db_service.init()

        # clean the database
        orm.Base.metadata.drop_all(bind=db_service.sync_engine)
        orm.Base.metadata.create_all(bind=db_service.sync_engine)

        yield db_service

        # clean the database
        orm.Base.metadata.drop_all(bind=db_service.sync_engine)


@pytest.fixture
def client(disable_auth: bool, act_as_admin: bool, db_service: DBService) -> TestClient:
    """
    Return a TestClient with the startup event run, and where
    the shutdown event runs during teardown.

    This link explains how the "on_startup" event is triggered by this code:
    https://fastapi.tiangolo.com/advanced/testing-events/

    :param disable_auth: if True, mocks out most of auth so that there are
        no dependencies on AWS Cognito
    :param act_as_admin: if True, the test user will be made an admin for the
        lifetime of the app created by this function
    """
    app: FastAPI = make_app(disable_auth=disable_auth)

    # trigger "on_startup" event by instantiating TestClient with a context manager
    with TestClient(app) as client:

        # register the test user as an admin if desired
        if act_as_admin:
            db_service: DBService = app.state.services.db
            # tests were hanging forever when I didn't wrap the session in a context manager... why?
            session: Session
            with db_service.get_sync_session() as session:
                register_user(session=session, email=TEST_USER["email"], is_admin=True)

        yield client


@pytest.fixture
def dynamo_client(dynamo_db_service: DynamoDBService, disable_auth: bool, act_as_admin: bool) -> TestClient:
    CONFIG_VALUES = {
        "postgres_user": "dummy-user",
        "postgres_password": "dummy-pass",
        "postgres_host": "dummy-host",
        "postgres_port": 12345,
        "postgres_db": "dummy_db",
        "cognito_aws_region": "us-west-2",
        "cognito_user_pool_id": "123456789",
        "host": "test-host",
        "port": 9999,
        "domain": "www.test-domain.io",
        "s3_static_site_origin": "http://www.static-site.com:25565",
        "cognito_web_client_id": "some-hash-looking-string",
        "dynamo_table_name": ROOTSKI_DYNAMO_TABLE_NAME,
        "extra_allowed_cors_origins": [
            "http://www.extra-origin.com",
            "https://www.extra-origin.com",
        ],
    }

    config = Config(**CONFIG_VALUES)
    app: FastAPI = make_app(disable_auth=disable_auth, config_override=config)
    # app.dependency_overrides[deps.get_current_user] = lambda: schemas.User(
    #     email=TEST_USER["email"], is_admin=act_as_admin
    # )
    with TestClient(app) as client:
        yield client


############################
# --- Helper functions --- #
############################


def make_app(disable_auth=True, config_override: Optional[Config] = None) -> FastAPI:
    """Create an default instance of an app.

    :param enable_auth: if ``False``, disable auth so that all requests
        are made by the global test user.
    """
    config = config_override or Config(**CONFIG_VALUES_FOR_REAL_DATABASE)
    app = create_app(config=config)
    if disable_auth:
        _disable_auth(app=app)
    return app


def _disable_auth(app: FastAPI):
    """Cause all requests to be pre-authenticated for the test user by mocking the auth service."""
    # make all requests on behalf of a pre-authorized test user
    def fake_get_authorized_user_email():
        return TEST_USER["email"]

    # we could override deps.get_current_user which depends on deps.get_authorized_user_email_or_anon,
    # but mocking only this part causes requests to actually look into the database to read
    # user information; it's good that our tests are involving that logic.
    app.dependency_overrides[deps.get_authorized_user_email_or_anon] = fake_get_authorized_user_email

    # replace the AuthService with a mock
    app_services: Services = app.state.services
    app_config: Config = app.state.config
    app_services.auth = MockService.from_config(config=app_config)

    return app
