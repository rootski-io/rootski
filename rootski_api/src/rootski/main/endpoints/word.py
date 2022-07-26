from typing import Union

from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from rootski.schemas.core import Services
from rootski.services.database import DBService
from rootski.services.database.dynamo import models as dynamo
from rootski.services.database.dynamo.models2schemas.word import dynamo_to_pydantic__word
from rootski.services.database.non_orm.db_service import RootskiDBService as LegacyDBService
from starlette.status import HTTP_400_BAD_REQUEST

from rootski import schemas

router = APIRouter()

TWordResponse = Union[
    schemas.AdjectiveResponse, schemas.NounResponse, schemas.VerbResponse, schemas.WordResponse
]


@router.get("/word/{word_id}/{word_type}", response_model=TWordResponse)
async def get_word_data(word_id: int, word_type: str, request: Request):
    """
    Return all data necessary to populate the word page for the given word
    except for the breakdown (see the note)

    NOTE: the "breakdown" field is not returned by this endpoint any more.
    That data should be fetched using GET /breakdown
    """
    app_services: Services = request.app.state.services
    db_service: DBService = app_services.db
    legacy_db_service = LegacyDBService(engine=db_service.sync_engine)

    logger.info(f"Getting word data for word {word_id} of type {word_type}")

    # validate params
    if word_type not in [
        "noun",
        "adjective",
        "verb",
        "particle",
        "adverb",
        "preposition",
        "pronoun",
        "conjunction",
    ]:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid word type.")

    payload = legacy_db_service.fetch_word_data(word_id, word_type)

    dynamo_word = dynamo.Word(data=payload)
    from rich.pretty import pprint

    pprint(dynamo_word.data)
    response: TWordResponse = dynamo_to_pydantic__word(word=dynamo_word)

    print(type(response))
    pprint(response.dict(by_alias=True))

    return response
