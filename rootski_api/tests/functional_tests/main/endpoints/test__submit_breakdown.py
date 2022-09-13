"""
For these tests, we will override the authorization dependency
so that the tests are not dependent on cognito. We'll assume that
the ``test__auth`` service is sufficient.
"""
from typing import Tuple, Union

import pytest
from rootski.main.endpoints.breakdown.errors import (
    MORPHEME_IDS_NOT_FOUND_MSG,
    PARTS_DONT_SUM_TO_WHOLE_WORD_MSG,
    WORD_ID_NOT_FOUND,
    BreakdownNotFoundError,
)
from rootski.services.database.dynamo.actions.breakdown_actions import (
    get_official_breakdown_by_word_id,
    get_user_submitted_breakdown_by_user_email_and_word_id,
)
from rootski.services.database.dynamo.db_service import DBService as DynamoDBService
from rootski.services.database.dynamo.models.breakdown import Breakdown
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from starlette.testclient import TestClient
from tests.constants import TEST_USER
from tests.fixtures.seed_data import (
    EXAMPLE_BREAKDOWN_DOESNT_ADD_UP,
    EXAMPLE_SUCCESSFUL_BREAKDOWN_SUBMISSION,
    EXAMPLE_SUCCESSFUL_BREAKDOWN_W_ALL_NULL_BREAKDOWN_ITEMS,
    EXAMPLE_USER_SUBMISSION_MISSING_MORPHEME_IDS,
    EXAMPLE_USER_SUBMISSION_MISSING_WORD,
    EXAMPLE_USER_SUBMISSION_REPLACING_CURRENT_BREAKDOWN,
    seed_data,
)

from rootski import schemas

############################
# --- Helper Functions --- #
############################


def make_request_payload(user_submission: dict) -> schemas.BreakdownUpsert:
    payload = schemas.BreakdownUpsert(
        word_id=user_submission["word_id"], breakdown_items=user_submission["breakdown_items"]
    )
    return payload


def make_submit_breakdown_request(
    user_submission: dict, dynamo_client: TestClient, should_succeed: bool
) -> Union[Tuple[int, schemas.SubmitBreakdownResponse], Response]:
    payload = make_request_payload(user_submission=user_submission)
    response = dynamo_client.post("/breakdown", json=payload.dict(exclude_unset=True))
    if should_succeed:
        return response.status_code, schemas.SubmitBreakdownResponse(**response.json())
    else:
        return response


#################
# --- Tests --- #
#################


# TODO: (1) run get_breakdown on an breakdown that doesn't exist: assert it does not exist
# (2) submit the breakdown we just tried to get: assert correct output, response
# (3) then get the breakdown we just submitted based on is_admin: verified it was gotten-ied
@pytest.mark.parametrize(
    ["disable_auth", "act_as_admin"],
    [
        (
            True,
            False,
        ),
        (
            True,
            True,
        ),
    ],
)
def test__submit_breakdown__success(
    dynamo_client: TestClient, dynamo_db_service: DynamoDBService, act_as_admin: bool
):
    # Seed the database and make the request
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)

    # Verify the breakdown is not in the database
    word_id: str = "50"
    user_email: str = TEST_USER["email"]
    try:
        get_official_breakdown_by_word_id(word_id=word_id, db=dynamo_db_service)
        raise Exception(f"Breakdown with word id {word_id} was found in Dynamo when it should not yet exist.")
    except BreakdownNotFoundError:
        pass

    # Upload the breakdown to Dynamo
    USER_SUBMISSION: dict = EXAMPLE_SUCCESSFUL_BREAKDOWN_SUBMISSION
    status_code, response = make_submit_breakdown_request(
        user_submission=USER_SUBMISSION, dynamo_client=dynamo_client, should_succeed=True
    )

    # Verify that the breakdown was submitted successfully
    assert status_code == HTTP_200_OK
    assert response.breakdown_id == -1  # this field is deprecated and should be -1
    assert response.word_id == int(word_id)
    assert response.is_verified == act_as_admin
    # Read the data from the updated database
    if act_as_admin is True:

        official_breakdown: Breakdown = get_official_breakdown_by_word_id(word_id=word_id, db=dynamo_db_service)
        assert official_breakdown.word_id == word_id
        assert official_breakdown.word == "сказать"
        assert official_breakdown.is_verified == True
        assert official_breakdown.is_inference == False
        assert official_breakdown.pk == f"WORD#{word_id}"
        assert official_breakdown.sk == f"BREAKDOWN"
    else:
        user_breakdown = get_user_submitted_breakdown_by_user_email_and_word_id(
            db=dynamo_db_service,
            word_id=word_id,
            user_email=user_email,
        )
        assert user_breakdown.word_id == word_id
        assert user_breakdown.word == "сказать"
        assert user_breakdown.is_verified == False
        assert user_breakdown.is_inference == False
        assert user_breakdown.pk_for_unofficial_breakdown == f"USER#{user_email}"
        assert user_breakdown.sk_for_unofficial_breakdown == f"BREAKDOWN#{word_id}"


@pytest.mark.parametrize(
    ["disable_auth", "act_as_admin"],
    [
        (
            True,
            True,
        )
    ],
)
def test__submit_breakdown__success_overwrite_official_breakdown(
    dynamo_client: TestClient, dynamo_db_service: DynamoDBService, act_as_admin: bool
):
    # Seed the database and make the request
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)

    # Verify the breakdown is not in the database
    word_id: str = "7"
    user_email: str = TEST_USER["email"]

    # Upload the breakdown to Dynamo
    USER_SUBMISSION: dict = EXAMPLE_USER_SUBMISSION_REPLACING_CURRENT_BREAKDOWN
    status_code, response = make_submit_breakdown_request(
        user_submission=USER_SUBMISSION, dynamo_client=dynamo_client, should_succeed=True
    )

    # Verify that the breakdown was submitted successfully
    assert status_code == HTTP_200_OK
    assert response.breakdown_id == -1  # this field is deprecated and should be -1
    assert response.word_id == int(word_id)
    assert response.is_verified == act_as_admin

    official_breakdown: Breakdown = get_official_breakdown_by_word_id(word_id=word_id, db=dynamo_db_service)
    assert official_breakdown.word_id == word_id
    assert official_breakdown.word == "быть"
    assert official_breakdown.is_verified == True
    assert official_breakdown.is_inference == False
    assert official_breakdown.pk == f"WORD#{word_id}"
    assert official_breakdown.sk == f"BREAKDOWN"


@pytest.mark.parametrize(
    ["disable_auth", "act_as_admin"],
    [
        (
            True,
            False,
        )
    ],
)
def test__submit_breakdown__success_with_null_morpheme(
    dynamo_client: TestClient, dynamo_db_service: DynamoDBService
):
    # Seed the database and make the request
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    USER_SUBMISSION: dict = EXAMPLE_SUCCESSFUL_BREAKDOWN_W_ALL_NULL_BREAKDOWN_ITEMS
    status_code, response = make_submit_breakdown_request(
        user_submission=USER_SUBMISSION, dynamo_client=dynamo_client, should_succeed=True
    )

    assert status_code == HTTP_200_OK
    assert response.breakdown_id == -1  # this field is now deprecated
    assert response.is_verified == False  # the test user is not an admin
    assert response.word_id == USER_SUBMISSION["word_id"]


@pytest.mark.parametrize(
    ["disable_auth", "act_as_admin"],
    [
        (
            True,
            False,
        )
    ],
)
def test__submit_breakdown__error_when_morpheme_ids_not_found(
    dynamo_client: TestClient, dynamo_db_service: DynamoDBService
):
    # seed the database and make the request
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    USER_SUBMISSION = EXAMPLE_USER_SUBMISSION_MISSING_MORPHEME_IDS
    response = make_submit_breakdown_request(
        user_submission=USER_SUBMISSION, dynamo_client=dynamo_client, should_succeed=False
    )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert "detail" in response.json().keys()
    assert (
        MORPHEME_IDS_NOT_FOUND_MSG.format(not_found_ids=str({"218", "1577", "2139"}))
        == response.json()["detail"]
    )


@pytest.mark.parametrize(
    ["disable_auth", "act_as_admin"],
    [
        (
            True,
            False,
        )
    ],
)
def test__submit_breakdown__error_when_word_not_found(
    dynamo_client: TestClient, dynamo_db_service: DynamoDBService
):
    # Seed the database and get the response
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    USER_SUBMISSION: dict = EXAMPLE_USER_SUBMISSION_MISSING_WORD
    response = make_submit_breakdown_request(
        user_submission=USER_SUBMISSION, dynamo_client=dynamo_client, should_succeed=False
    )

    # There is no word with ID 150 in mock dynamo db database
    assert response.status_code == HTTP_404_NOT_FOUND
    assert "detail" in response.json().keys()
    assert WORD_ID_NOT_FOUND.format(word_id=USER_SUBMISSION["word_id"]) == response.json()["detail"]


@pytest.mark.parametrize(
    ["disable_auth", "act_as_admin"],
    [
        (
            True,
            False,
        )
    ],
)
def test__submit_breakdown__error_when_breakdown_doesnt_add_up(
    dynamo_client: TestClient, dynamo_db_service: DynamoDBService
):
    # Seed the database and make the request
    seed_data(rootski_dynamo_table=dynamo_db_service.rootski_table)
    USER_SUBMISSION: dict = EXAMPLE_BREAKDOWN_DOESNT_ADD_UP
    response = make_submit_breakdown_request(
        user_submission=USER_SUBMISSION, dynamo_client=dynamo_client, should_succeed=False
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "detail" in response.json().keys()
    assert (
        PARTS_DONT_SUM_TO_WHOLE_WORD_MSG.format(submitted_breakdown="сказe-ать", word="сказать")
        == response.json()["detail"]
    )
