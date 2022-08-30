from datetime import datetime
from typing import Dict, List, Optional

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
)
from rootski.main.endpoints.breakdown.utils import query_morphemes, raise_exception_for_invalid_breakdown
from rootski.schemas.core import Services
from rootski.services.database import models as orm
from rootski.services.database.dynamo import models as dynamo
from rootski.services.database.dynamo.actions import breakdown_actions
from rootski.services.database.dynamo.models2schemas import breakdown as models_to_schemas
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from rootski import schemas

router = APIRouter()


def get_first_breakdown(breakdowns: List[orm.Breakdown], user_email: str) -> Optional[schemas.Breakdown]:
    if len(breakdowns) > 0:
        breakdown = breakdowns[0]
        if not breakdown.word:
            breakdown.word = breakdown.word_.word
        to_return = schemas.Breakdown.from_orm_breakdown(breakdown)
        to_return.submitted_by_current_user = breakdown.submitted_by_user_email == user_email
        return to_return
    else:
        return None


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
    word_id: int,
    user: schemas.User = Depends(deps.get_current_user),
):
    """
    Return the first one of these to be found (prioritized in this order):

    1. A verified breakdown
    2. The breakdown last submitted by the requesting user
    3. The breakdown last submitted by another user
    4. The inferenced breakdown
    5. The default, unverified breakdown

    If this request does not have a "Bearer ..." Authorization header,
    the user is assumed to be anonymous.
    """

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
    except breakdown_actions.BreakdownNotFoundError as err:
        LOGGER.info(err)
        raise NOT_FOUND_ERROR
    LOGGER.info(breakdown)

    # (1) return a verified breakdown if there is one;
    # there can be up to one verified breakdown per word
    LOGGER.info("Starting step 1")
    if breakdown_actions.is_breakdown_verified(breakdown=breakdown):
        morpheme_family_dict = breakdown_actions.get_morpheme_families(breakdown=breakdown, db=dynamo_db)
        return models_to_schemas.dynamo_to_pydantic__breakdown(
            breakdown=breakdown, morpheme_family_dict=morpheme_family_dict, user_email=user.email
        )
    LOGGER.info(f"No verified breakdown for word with ID {word_id} was found in Dynamo.")

    LOGGER.info("Starting step 2")
    if breakdown.submitted_by_user_email == user.email:
        morpheme_family_dict = breakdown_actions.get_morpheme_families(breakdown=breakdown, db=dynamo_db)
        return models_to_schemas.dynamo_to_pydantic__breakdown(
            breakdown=breakdown, morpheme_family_dict=morpheme_family_dict, user_email=user.email
        )

    try:
        user_submitted_breakdown = breakdown_actions.get_breakdown_submitted_by_user_email_and_word_id(
            word_id=word_id, user_email=user.email, db=dynamo_db
        )
        morpheme_family_dict = breakdown_actions.get_morpheme_families(
            breakdown=user_submitted_breakdown, db=dynamo_db
        )
        return models_to_schemas.dynamo_to_pydantic__breakdown(
            breakdown=user_submitted_breakdown, morpheme_family_dict=morpheme_family_dict, user_email=user.email
        )
    except breakdown_actions.BreakdownNotFoundError as err:
        LOGGER.info(err)

    # (3) return a breakdown submitted by another user
    LOGGER.info("Starting step 3")
    if breakdown.submitted_by_user_email != "anonymous":
        morpheme_family_dict = breakdown_actions.get_morpheme_families(breakdown=breakdown, db=dynamo_db)
        return models_to_schemas.dynamo_to_pydantic__breakdown(
            breakdown=breakdown, morpheme_family_dict=morpheme_family_dict, user_email=user.email
        )
    try:
        another_user_breakdown = breakdown_actions.get_official_breakdown_submitted_by_another_user(
            word_id=word_id, db=dynamo_db
        )
        if another_user_breakdown.submitted_by_user_email != "anonymous":
            morpheme_family_dict = breakdown_actions.get_morpheme_families(
                breakdown=another_user_breakdown, db=dynamo_db
            )
            return models_to_schemas.dynamo_to_pydantic__breakdown(
                breakdown=another_user_breakdown,
                morpheme_family_dict=morpheme_family_dict,
                user_email=user.email,
            )
    except breakdown_actions.BreakdownNotFoundError as err:
        LOGGER.info(err)

    # (4) return a breakdown inferenced by the AI
    LOGGER.info("Starting step 4")
    LOGGER.info(breakdown)
    if breakdown.is_inference is True:
        morpheme_family_dict = breakdown_actions.get_morpheme_families(breakdown=breakdown, db=dynamo_db)
        return models_to_schemas.dynamo_to_pydantic__breakdown(
            breakdown=breakdown, morpheme_family_dict=morpheme_family_dict, user_email=user.email
        )

    # (5) raise not found error
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
                )
            ]
        ),
    },
)
def submit_breakdown(
    payload: schemas.BreakdownUpsert = Body(...),
    user: schemas.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_session),
):
    """
    Submit a breakdown on behalf of a user.

    Case: If the breakdown is not valid, an error is returned.
    Case: If the user has already submitted a breakdown for this same word before, the previously submitted breakdown is replaced for that user.
    Case: If the user is an admin user, the breakdown is marked as "verified". Otherwise it is unverified.

    """

    # does the word exist?
    word: Optional[orm.Word] = db.query(orm.Word).filter(orm.Word.id == payload.word_id).first()
    if not word:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=WORD_ID_NOT_FOUND.format(word_id=payload.word_id),
        )

    # is the breakdown valid?
    id_to_morpheme: Dict[int, str] = {}
    try:
        id_to_morpheme = query_morphemes(db=db, breakdown_items=payload.breakdown_items)
        raise_exception_for_invalid_breakdown(
            db=db,
            word=word.word,
            breakdown_items=payload.breakdown_items,
            id_to_morpheme=id_to_morpheme,
        )
    except MorphemeNotFoundError as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=str(e))
    except BadBreakdownError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))

    # look for a breakdown for this word already submitted by this user so we can update it
    breakdown: Optional[orm.Breakdown] = (
        db.query(orm.Breakdown)
        .filter(
            orm.Breakdown.submitted_by_user_email == user.email and orm.Breakdown.word_id == payload.word_id
        )
        .first()
    )

    # if not found, we'll create a new one
    if not breakdown:
        breakdown = orm.Breakdown(word_id=payload.word_id, submitted_by_user_email=user.email)
    breakdown.submitted_by_user_email = user.email
    breakdown.word_id = word.id

    # is it verified?
    breakdown.is_verified = user.is_admin
    if user.is_admin:
        breakdown.verified_by_user_email = user.email
        breakdown.date_verified = datetime.now()

    # prepare to save the breakdown in the database; NOTE ideally, we would
    #
    breakdown_items = []
    for b_item in payload.breakdown_items:
        b_item_kwargs = b_item.dict()
        to_add = schemas.BreakdownItemInDb(**b_item_kwargs).to_orm()
        if isinstance(b_item, schemas.NullMorphemeBreakdownItem):
            to_add.morpheme = b_item.morpheme
        elif isinstance(b_item, schemas.MorphemeBreakdownItemInRequest):
            to_add.morpheme = id_to_morpheme[to_add.morpheme_id]
        else:
            raise HTTP_400_BAD_REQUEST("Bad request body.")
        breakdown_items.append(to_add)
    breakdown.breakdown_items = breakdown_items

    # save the breakdown in the database
    db.add(breakdown)
    db.commit()

    return schemas.SubmitBreakdownResponse(
        breakdown_id=breakdown.breakdown_id,
        word_id=breakdown.word_id,
        is_verified=breakdown.is_verified,
    )
