#################
# --- Tests --- #
#################
from typing import Any, Dict

import pytest
from loguru import logger as LOGGER
from rootski.services.database.dynamo.db_service import DBService as DynamoDBService
from starlette.testclient import TestClient
from tests.fixtures.seed_data import (
    EXAMPLE_BREAKDOWN_W_MORPHEME_FAMILIES_IN_DB,
    EXAMPLE_OFFICIAL_BREAKDOWN_BY_USER_W_NULL_AND_NON_NULL_BREAKDOWN_ITEMS_IN_DB,
    seed_data,
)


# this decorator causes the test to be run twice with the following parameters passed to the fixtures:
#     (disable_auth=True, act_as_admin=False) and (disable_auth=True, act_as_admin=True)
@pytest.mark.parametrize(["disable_auth", "act_as_admin"], [(True, False), (True, True)])
def test__get_breakdown(dynamo_client: TestClient, dynamo_db_service: DynamoDBService):
    # Put data into mocked dynamo table
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    EXAMPLE_BREAKDOWN = EXAMPLE_BREAKDOWN_W_MORPHEME_FAMILIES_IN_DB

    # Get response from client
    word_id = int(EXAMPLE_BREAKDOWN["word_id"])
    response = dynamo_client.get(f"/breakdown/{word_id}")
    response: Dict[str, Any] = response.json()
    LOGGER.info(response)

    # assert the correct values
    assert "breakdown_items" in response.keys()
    assert response["word_id"] == int(EXAMPLE_BREAKDOWN["word_id"])
    assert response["word"] == EXAMPLE_BREAKDOWN["word"]
    assert response["is_verified"] == EXAMPLE_BREAKDOWN["is_verified"]
    assert response["is_inference"] == EXAMPLE_BREAKDOWN["is_inference"]


# TODO: This test passes based on the order of insertion into the seed database.
# Data modeling and the dynamo action need to be re-written.
@pytest.mark.parametrize(["disable_auth", "act_as_admin"], [(True, False)])
def test__get_breakdown_submitted_by_another_user(
    dynamo_client: TestClient, dynamo_db_service: DynamoDBService
):
    # Put data into mocked dynamo table
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    EXAMPLE_BREAKDOWN = EXAMPLE_OFFICIAL_BREAKDOWN_BY_USER_W_NULL_AND_NON_NULL_BREAKDOWN_ITEMS_IN_DB

    # Get response from client
    word_id = int(EXAMPLE_BREAKDOWN["word_id"])
    response = dynamo_client.get(f"/breakdown/{word_id}")
    response: Dict[str, Any] = response.json()
    # LOGGER.info(response)

    # assert the correct values
    assert "breakdown_items" in response.keys()
    assert response["word_id"] == int(EXAMPLE_BREAKDOWN["word_id"])
    assert response["word"] == EXAMPLE_BREAKDOWN["word"]
    assert response["is_verified"] == EXAMPLE_BREAKDOWN["is_verified"]
    assert response["is_inference"] == EXAMPLE_BREAKDOWN["is_inference"]
    assert response["submitted_by_current_user"] == False
