#################
# --- Tests --- #
#################
from typing import Any, Dict

import pytest
from loguru import logger as LOGGER
from rootski.services.database.dynamo.db_service import DBService as DynamoDBService
from starlette.testclient import TestClient
from tests.fixtures.seed_data import EXAMPLE_BREAKDOWN_W_MORPHEME_FAMILIES_IN_DB, seed_data


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


# this decorator causes the test to be run twice with the following parameters passed to the fixtures:
#     (disable_auth=True, act_as_admin=False) and (disable_auth=True, act_as_admin=True)
# @pytest.mark.parametrize(["disable_auth", "act_as_admin"], [(True, False), (True, True)])
# def test__get_breakdown(client: TestClient, db_service: DBService, act_as_admin: bool):
#     # post a breakdown
#     word_orm, morphemes_orm = get_breakdown_orm_objs()
#     word, morphemes = insert_test_objs(db=db_service, word=word_orm, morphemes=morphemes_orm)
#     status_code, response = make_submit_breakdown_request(
#         word=word, morphemes=morphemes, client=client, should_succeed=True
#     )

#     word_id: int = response.word_id
#     response = client.get(f"/breakdown/{word_id}")
#     response: Dict[str, Any] = response.json()

#     print(f"got response for GET /breakdown/{word_id}")
#     pprint(response)

#     assert status_code == HTTP_200_OK

#     # validate the general breakdown metadata
#     assert "breakdown_items" in response.keys()
#     assert response["is_inference"] == False
#     assert response["word_id"] == 1

#     # the response should be verified if submitted by an admin, otherwise it shouldn't
#     assert response["is_verified"] == act_as_admin

#     # validate the content of the breakdown items; NOTE no "null morphemes" are expected in this
#     # output. If there were, we would also have to check for "word_pos" and "morpheme_id" set to None.
#     assert len(response["breakdown_items"]) == 3
#     for b_item in response["breakdown_items"]:
#         assert b_item["position"] > -1  # checking that these are integers
#         assert b_item["morpheme"] != ""
#         assert b_item["word_pos"] in {e for e in MORPHEME_WORD_POS_VALUES}

#     # is the breakdown itself valid? (do the broken down parts sum to the actual word?)
#     assert word.word == "".join([b_item["morpheme"] for b_item in response["breakdown_items"]])
