#################
# --- Tests --- #
#################
from pprint import pprint
from typing import Any, Dict

import pytest
from starlette.status import HTTP_200_OK
from starlette.testclient import TestClient

from rootski.schemas import MORPHEME_WORD_POS_VALUES
from rootski.services.database import DBService
from tests.functional_tests.main.endpoints.fake_data import (
    get_breakdown_orm_objs,
    insert_test_objs,
)
from tests.functional_tests.main.endpoints.test__submit_breakdown import (
    make_submit_breakdown_request,
)


# this decorator causes the test to be run twice with the following parameters passed to the fixtures:
#     (disable_auth=True, act_as_admin=False) and (disable_auth=True, act_as_admin=True)
@pytest.mark.parametrize(["disable_auth", "act_as_admin"], [(True, False), (True, True)])
def test__get_breakdown(client: TestClient, db_service: DBService, act_as_admin: bool):
    # post a breakdown
    word_orm, morphemes_orm = get_breakdown_orm_objs()
    word, morphemes = insert_test_objs(db=db_service, word=word_orm, morphemes=morphemes_orm)
    status_code, response = make_submit_breakdown_request(
        word=word, morphemes=morphemes, client=client, should_succeed=True
    )

    word_id: int = response.word_id
    response = client.get(f"/breakdown/{word_id}")
    response: Dict[str, Any] = response.json()

    print(f"got response for GET /breakdown/{word_id}")
    pprint(response)

    assert status_code == HTTP_200_OK

    # validate the general breakdown metadata
    assert "breakdown_items" in response.keys()
    assert response["is_inference"] == False
    assert response["word_id"] == 1

    # the response should be verified if submitted by an admin, otherwise it shouldn't
    assert response["is_verified"] == act_as_admin

    # validate the content of the breakdown items; NOTE no "null morphemes" are expected in this
    # output. If there were, we would also have to check for "word_pos" and "morpheme_id" set to None.
    assert len(response["breakdown_items"]) == 3
    for b_item in response["breakdown_items"]:
        assert b_item["position"] > -1  # checking that these are integers
        assert b_item["morpheme"] != ""
        assert b_item["word_pos"] in {e for e in MORPHEME_WORD_POS_VALUES}

    # is the breakdown itself valid? (do the broken down parts sum to the actual word?)
    assert word.word == "".join([b_item["morpheme"] for b_item in response["breakdown_items"]])
