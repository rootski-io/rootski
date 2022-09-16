"""
Configuration for rootski tests.

Some tests run against real infrastructure, such as a postres database
or a Cognito user pool. Some tests mock out pieces (or all) of the external
infrastructure.

When tests DO rely on infrastructure, those configuration values should be
provided via environment variables. Those can go in the tests/resources/docker-compose.yml
file or in the makefile.
"""

ROOTSKI_DYNAMO_TABLE_NAME = "TEST_DYNAMO_TABLE"


TEST_USER = {
    "email": "banana-man@rootski.io",
    "password": "Eric Is Banana Man",
}

# config values for items that don't depend on infrastructure
# such as the backend database or Cognito user pool
BASE_SAMPLE_CONFIG_VALUES = {
    "host": "test-host",
    "port": 9999,
    "domain": "www.test-domain.io",
    "s3_static_site_origin": "http://www.static-site.com:25565",
    "cognito_web_client_id": "some-hash-looking-string",
    "extra_allowed_cors_origins": [
        "http://www.extra-origin.com",
        "https://www.extra-origin.com",
    ],
}

# config values used when tests are not meant to authenticate with a real cognito user pool
DUMMY_COGNITO_CONFIG_VALUES = {
    "cognito_aws_region": "us-west-1",
    "cognito_user_pool_id": "123456789",
}

# complete set of config values that can be used to instantiate a Config object
# for tests that do not depend on any external infrastructure
DUMMY_CONFIG_VALUES = dict(**BASE_SAMPLE_CONFIG_VALUES, **DUMMY_COGNITO_CONFIG_VALUES)

# config for real database tests: there are dummy values for all infrastructure
# but the database; the real database config values should come from environment
# variables
CONFIG_VALUES_FOR_REAL_DATABASE = dict(**BASE_SAMPLE_CONFIG_VALUES, **DUMMY_COGNITO_CONFIG_VALUES)
