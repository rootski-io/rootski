"""
For these tests, we will override the authorization dependency
so that the tests are not dependent on cognito. We'll assume that
the ``test__auth`` service is sufficient.
"""
from typing import List, Tuple, Union

import pytest
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from starlette.testclient import TestClient

from rootski import schemas
from rootski.main.endpoints.breakdown.errors import (
    MORPHEME_IDS_NOT_FOUND_MSG,
    PARTS_DONT_SUM_TO_WHOLE_WORD_MSG,
    WORD_ID_NOT_FOUND,
)
from rootski.schemas.breakdown import make_specific_breakdown_item
from rootski.services.database import DBService
from tests.functional_tests.main.endpoints.fake_data import (
    get_breakdown_orm_objs,
    get_schemas_from_models,
    insert_test_objs,
)

############################
# --- Helper Functions --- #
############################


def make_request_payload(word: schemas.Word, morphemes: List[schemas.Morpheme]) -> schemas.BreakdownUpsert:
    breakdown_items = [make_specific_breakdown_item(morpheme=m, position=i) for i, m in enumerate(morphemes)]
    payload = schemas.BreakdownUpsert(word_id=word.id, breakdown_items=breakdown_items)
    return payload


def make_submit_breakdown_request(
    word: schemas.Word, morphemes: List[schemas.Morpheme], client: TestClient, should_succeed: bool
) -> Union[Tuple[int, schemas.SubmitBreakdownResponse], Response]:
    payload = make_request_payload(word=word, morphemes=morphemes)
    response = client.post("/breakdown", json=payload.dict(exclude_unset=True))
    if should_succeed:
        return response.status_code, schemas.SubmitBreakdownResponse(**response.json())
    else:
        return response


#################
# --- Tests --- #
#################


@pytest.mark.parametrize(
    ["disable_auth", "act_as_admin"],
    [
        (
            True,
            False,
        )
    ],
)
def test__submit_breakdown__success(client: TestClient, db_service: DBService):
    # seed the database
    word_orm, morphemes_orm = get_breakdown_orm_objs()
    word, morphemes = insert_test_objs(db=db_service, word=word_orm, morphemes=morphemes_orm)

    # make the request
    status_code, response = make_submit_breakdown_request(
        word=word, morphemes=morphemes, client=client, should_succeed=True
    )

    # verify that the breakdown was submitted successfully
    assert status_code == HTTP_200_OK
    assert response.breakdown_id == 1  # there were no others, so it should be 1
    assert response.is_verified == False  # the test user is not an admin
    assert response.word_id == word.id


@pytest.mark.parametrize(
    ["disable_auth", "act_as_admin"],
    [
        (
            True,
            False,
        )
    ],
)
def test__submit_breakdown__success_with_null_morpheme(client: TestClient, db_service: DBService):
    # seed the database with "ать" as a null morpheme
    word_orm, morphemes_orm = get_breakdown_orm_objs()

    # only insert the first two morphemes, the third will be null
    _, _ = insert_test_objs(db=db_service, word=word_orm, morphemes=morphemes_orm[:2])
    word, morphemes = get_schemas_from_models(word=word_orm, morphemes=morphemes_orm)
    morphemes[2].morpheme_id = None
    morphemes[2].type = None

    # make the request
    status_code, response = make_submit_breakdown_request(
        word=word, morphemes=morphemes, client=client, should_succeed=True
    )

    assert status_code == HTTP_200_OK
    assert response.breakdown_id == 1  # there were no others, so it should be 1
    assert response.is_verified == False  # the test user is not an admin
    assert response.word_id == word.id


@pytest.mark.parametrize(
    ["disable_auth", "act_as_admin"],
    [
        (
            True,
            False,
        )
    ],
)
def test__submit_breakdown__error_when_morpheme_ids_not_found(client: TestClient, db_service: DBService):
    # seed the database with only the first of three morphemes
    word_orm, morphemes_orm = get_breakdown_orm_objs()
    _, _ = insert_test_objs(db=db_service, word=word_orm, morphemes=morphemes_orm[:1])
    word, morphemes = get_schemas_from_models(word=word_orm, morphemes=morphemes_orm)

    # in the request body, have the second and third breakdown items have morpheme
    # IDs that don't exist in the database
    morphemes[1].morpheme_id = 99
    morphemes[2].morpheme_id = 100

    # make the request
    response = make_submit_breakdown_request(
        word=word, morphemes=morphemes, client=client, should_succeed=False
    )

    # we should get a 404 Not Found error, because the submitted breakdown tried
    # to use the IDs of two morphemes that don't exist
    assert response.status_code == HTTP_404_NOT_FOUND
    assert "detail" in response.json().keys()
    assert MORPHEME_IDS_NOT_FOUND_MSG.format(not_found_ids=str({99, 100})) == response.json()["detail"]


@pytest.mark.parametrize(
    ["disable_auth", "act_as_admin"],
    [
        (
            True,
            False,
        )
    ],
)
def test__submit_breakdown__error_when_word_not_found(client: TestClient, db_service: DBService):
    # seed the database with
    word_orm, morphemes_orm = get_breakdown_orm_objs()
    _, _ = insert_test_objs(db=db_service, word=word_orm, morphemes=morphemes_orm[:1])
    word_orm.id = 99
    word_orm.word = "nerf nerf nerf"
    word, morphemes = get_schemas_from_models(word=word_orm, morphemes=morphemes_orm)

    # make the request
    response = make_submit_breakdown_request(
        word=word, morphemes=morphemes, client=client, should_succeed=False
    )

    # we should get a 404 Not Found error, because there is no word with ID 99
    # in the database
    assert response.status_code == HTTP_404_NOT_FOUND
    assert "detail" in response.json().keys()
    assert WORD_ID_NOT_FOUND.format(word_id=word.id) == response.json()["detail"]


@pytest.mark.parametrize(
    ["disable_auth", "act_as_admin"],
    [
        (
            True,
            False,
        )
    ],
)
def test__submit_breakdown__error_when_breakdown_doesnt_add_up(client: TestClient, db_service: DBService):
    # seed the database with
    word_orm, morphemes_orm = get_breakdown_orm_objs()
    morphemes_orm[0].morpheme = "dobby"
    morphemes_orm[1].morpheme = "is"
    morphemes_orm[2].morpheme = "free!"
    _, _ = insert_test_objs(db=db_service, word=word_orm, morphemes=morphemes_orm[:1])
    word, morphemes = get_schemas_from_models(word=word_orm, morphemes=morphemes_orm)

    # make the request
    response = make_submit_breakdown_request(
        word=word, morphemes=morphemes, client=client, should_succeed=False
    )

    # we should get a 404 Not Found error, because there is no word with ID 99
    # in the database
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "detail" in response.json().keys()
    assert (
        PARTS_DONT_SUM_TO_WHOLE_WORD_MSG.format(submitted_breakdown="dobby-is-free!", word="приказать")
        == response.json()["detail"]
    )
