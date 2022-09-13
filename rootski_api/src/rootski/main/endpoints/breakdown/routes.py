from typing import Dict, List, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from loguru import logger as LOGGER
from rootski.main import deps
from rootski.main.endpoints.breakdown.docs import ExampleResponse, make_apidocs_responses_obj
from rootski.main.endpoints.breakdown.errors import (
    BREAKDOWN_NOT_FOUND,
    MORPHEME_IDS_NOT_FOUND_MSG,
    PARTS_DONT_SUM_TO_WHOLE_WORD_MSG,
    WORD_ID_NOT_FOUND,
    BadBreakdownError,
    MorphemeNotFoundError,
    UserBreakdownNotFoundError,
    WordNotFoundError,
    BreakdownNotFoundError
)
from rootski.schemas.core import Services
from rootski.services.database.dynamo import models as dynamo
from rootski.services.database.dynamo.actions import breakdown_actions
from rootski.services.database.dynamo.actions import word as word_actions
from rootski.services.database.dynamo.db_service import DBService
from rootski.services.database.dynamo.models2schemas import breakdown as models_to_schemas
from rootski.services.database.dynamo.models2schemas import breakdown_schema_to_model as schemas_to_models
from rootski.services.database.dynamo.models.breakdown_item import BreakdownItemItem
from rootski.services.database.dynamo.models.morpheme import Morpheme
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from rootski import schemas

# from rootski.main.endpoints.breakdown.utils import query_morphemes, raise_exception_for_invalid_breakdown
# from rootski.services.database import models as orm
# from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/breakdown/{word_id}",
    response_model=schemas.GetBreakdownResponse,
    # response_model_exclude_unset=True,
    response_model_exclude_none=False,
    responses={
        404: make_apidocs_responses_obj(
            [
                ExampleResponse(
                    title="Breakdown not found",
                    body={"detail": BREAKDOWN_NOT_FOUND.format(word_id=8)},
                )
            ]
        )
    },
)
def get_breakdown(
    request: Request,
    word_id: Union[str, int],
    user: schemas.User = Depends(deps.get_current_user),
):
    """
    Return the first one of these to be found (prioritized in this order):

    1. A verified breakdown
    2. The breakdown last submitted by the requesting user
    3. The breakdown last submitted by another user
    4. The inferenced breakdown
    5. The breakdown was not found

    If this request does not have a "Bearer ..." Authorization header,
    the user is assumed to be anonymous.
    """
    word_id = str(word_id)

    app_services: Services = request.app.state.services
    dynamo_db = app_services.dynamo
    NOT_FOUND_ERROR = HTTPException(
        status_code=HTTP_404_NOT_FOUND,
        detail=BREAKDOWN_NOT_FOUND.format(word_id=word_id),
    )

    try:
        breakdown: dynamo.Breakdown = breakdown_actions.get_official_breakdown_by_word_id(
            word_id=word_id, db=dynamo_db
        )
    except BreakdownNotFoundError as err:
        LOGGER.debug(err)
        raise NOT_FOUND_ERROR
    LOGGER.debug(breakdown)

    # (1) return a verified breakdown if there is one;
    # there can be up to one verified breakdown per word
    LOGGER.debug("Starting step 1")
    if breakdown_actions.is_breakdown_verified(breakdown=breakdown):
        is_to_morpheme_families = breakdown_actions.get_morpheme_families_for_breakdown(
            breakdown=breakdown, db=dynamo_db
        )
        return models_to_schemas.dynamo_to_pydantic__breakdown(
            breakdown=breakdown, ids_to_morpheme_families=is_to_morpheme_families, user_email=user.email
        )
    LOGGER.debug(f"No verified breakdown for word with ID {word_id} was found in Dynamo.")

    # (2) return a breakdown submitted by current user
    LOGGER.debug("Starting step 2")
    if breakdown.submitted_by_user_email == user.email:
        is_to_morpheme_families = breakdown_actions.get_morpheme_families_for_breakdown(
            breakdown=breakdown, db=dynamo_db
        )
        return models_to_schemas.dynamo_to_pydantic__breakdown(
            breakdown=breakdown, ids_to_morpheme_families=is_to_morpheme_families, user_email=user.email
        )

    try:
        user_submitted_breakdown = breakdown_actions.get_user_submitted_breakdown_by_user_email_and_word_id(
            word_id=word_id, user_email=user.email, db=dynamo_db
        )
        is_to_morpheme_families = breakdown_actions.get_morpheme_families_for_breakdown(
            breakdown=user_submitted_breakdown, db=dynamo_db
        )
        return models_to_schemas.dynamo_to_pydantic__breakdown(
            breakdown=user_submitted_breakdown,
            ids_to_morpheme_families=is_to_morpheme_families,
            user_email=user.email,
        )
    except UserBreakdownNotFoundError as err:
        LOGGER.debug(err)

    # (3) return a breakdown submitted by another user
    LOGGER.debug("Starting step 3")
    if breakdown.submitted_by_user_email != "anonymous":
        is_to_morpheme_families = breakdown_actions.get_morpheme_families_for_breakdown(
            breakdown=breakdown, db=dynamo_db
        )
        return models_to_schemas.dynamo_to_pydantic__breakdown(
            breakdown=breakdown, ids_to_morpheme_families=is_to_morpheme_families, user_email=user.email
        )
    try:
        another_user_breakdown = breakdown_actions.get_official_breakdown_submitted_by_another_user(
            word_id=word_id, db=dynamo_db
        )
        if another_user_breakdown.submitted_by_user_email != "anonymous":
            is_to_morpheme_families = breakdown_actions.get_morpheme_families_for_breakdown(
                breakdown=another_user_breakdown, db=dynamo_db
            )
            return models_to_schemas.dynamo_to_pydantic__breakdown(
                breakdown=another_user_breakdown,
                ids_to_morpheme_families=is_to_morpheme_families,
                user_email=user.email,
            )
    except BreakdownNotFoundError as err:
        LOGGER.debug(err)

    # (4) return a breakdown inferenced by the AI
    LOGGER.debug("Starting step 4")
    if breakdown.is_inference is True:
        is_to_morpheme_families = breakdown_actions.get_morpheme_families_for_breakdown(
            breakdown=breakdown, db=dynamo_db
        )
        return models_to_schemas.dynamo_to_pydantic__breakdown(
            breakdown=breakdown, ids_to_morpheme_families=is_to_morpheme_families, user_email=user.email
        )

    # (5) The breakdown was not found.
    raise NOT_FOUND_ERROR


@router.post(
    "/breakdown",
    response_model=schemas.SubmitBreakdownResponse,
    responses={
        404: make_apidocs_responses_obj(
            [
                ExampleResponse(
                    title="Word not found",
                    body={"detail": WORD_ID_NOT_FOUND.format(word_id=54321)},
                ),
                ExampleResponse(
                    title="Morpheme not found",
                    body={"detail": MORPHEME_IDS_NOT_FOUND_MSG.format(not_found_ids="{1, 2, 3}")},
                ),
            ]
        ),
        400: make_apidocs_responses_obj(
            [
                ExampleResponse(
                    title="Invalid breakdown",
                    body={
                        "detail": PARTS_DONT_SUM_TO_WHOLE_WORD_MSG.format(
                            submitted_breakdown="при-каз-ывать", word="приказать"
                        )
                    },
                ),
            ]
        ),
    },
)
def submit_breakdown(
    request: Request,
    payload: schemas.BreakdownUpsert = Body(...),
    user: schemas.User = Depends(deps.get_current_user),
):
    """
    Submit a breakdown on behalf of a user.

    Case: If the breakdown is not valid, an error is returned.
    Case: If the user is an admin user, the breakdown is marked as "verified". Otherwise it is unverified.
    Case: If the user has already submitted a breakdown for this same word before, the previously submitted breakdown is replaced for that user.

    NOTE: We assume the word a breakdown is being submitted for always exists.
    """
    app_services: Services = request.app.state.services
    dynamo_db = app_services.dynamo
    DEPRECATED_BREAKDOWN_ID = -1

    # (1) Check that the breakdown is valid
    LOGGER.debug("Starting step 1")
    try:
        LOGGER.debug("Getting morphemes")
        breakdown_morpheme_data: Dict[str, dynamo.Morpheme] = get_morphemes_for_breakdown(
            user_submitted_breakdown=payload,
            db=dynamo_db,
        )
    except MorphemeNotFoundError as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))

    try:
        LOGGER.debug("Getting word")
        word_obj: dynamo.Word = word_actions.get_word_by_id(word_id=payload.word_id, db=dynamo_db)
        breakdown_word: str = word_obj.data["word"]["word"]
    except WordNotFoundError as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))

    try:
        LOGGER.debug("Checking if the breakdown is a valid dynamo breakdown")
        user_breakdown: dynamo.Breakdown = schemas_to_models.pydantic_to_dynamo__breakdown(
            user_breakdown=payload,
            morpheme_data=breakdown_morpheme_data,
            user_email=user.email,
            word=breakdown_word,
            is_admin=user.is_admin,
        )
    except BadBreakdownError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))

    LOGGER.debug("Recreating the word from the breakdown items")
    recreated_word = recreate_word_from_breakdown_items(breakdown_items=user_breakdown.breakdown_items)
    if not recreated_word == breakdown_word:
        incorrect_word = recreate_incorrect_word_from_breakdown_items(
            breakdown_items=user_breakdown.breakdown_items
        )
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=PARTS_DONT_SUM_TO_WHOLE_WORD_MSG.format(
                submitted_breakdown=incorrect_word, word=breakdown_word
            ),
        )
    LOGGER.debug(user_breakdown)

    # TODO: Delete step 2 or fix this
    # LOGGER.debug("Starting step 2")
    # if not user.is_admin:
    #     user_breakdown.pk = user.email
    #     user_breakdown = user_breakdown.not_official_breakdown_sk(word_id=user_breakdown.word_id)

    # (3) upsert the user's breakdown to dynamo
    LOGGER.debug("Starting step 3")
    breakdown_actions.upsert_breakdown(breakdown=user_breakdown, is_official=user.is_admin, db=dynamo_db)

    return schemas.SubmitBreakdownResponse(
        breakdown_id=DEPRECATED_BREAKDOWN_ID,
        word_id=user_breakdown.word_id,
        is_verified=user_breakdown.is_verified,
    )


##########
# Helper #
##########


def get_morphemes_for_breakdown(
    user_submitted_breakdown: schemas.BreakdownUpsert, db: DBService
) -> Dict[str, Morpheme]:
    unique_morpheme_ids: List[str] = breakdown_actions.get_unique_morpheme_ids_of_non_null_breakdown_items(
        breakdown_items=user_submitted_breakdown.breakdown_items
    )
    morpheme_data: Dict[str, Morpheme] = breakdown_actions.get_morphemes(
        morpheme_ids=unique_morpheme_ids, db=db
    )
    return morpheme_data


def recreate_word_from_breakdown_items(breakdown_items: List[BreakdownItemItem]):
    sorted_breakdown_items_by_position: List[BreakdownItemItem] = sorted(
        breakdown_items, key=lambda breakdown_item: breakdown_item.position
    )
    recreated_word: str = "".join([bi.morpheme for bi in sorted_breakdown_items_by_position])

    return recreated_word


def recreate_incorrect_word_from_breakdown_items(breakdown_items: List[BreakdownItemItem]):
    sorted_breakdown_items_by_position: List[BreakdownItemItem] = sorted(
        breakdown_items, key=lambda breakdown_item: breakdown_item.position
    )
    recreated_incorrect_word: str = "-".join([bi.morpheme for bi in sorted_breakdown_items_by_position])

    return recreated_incorrect_word
