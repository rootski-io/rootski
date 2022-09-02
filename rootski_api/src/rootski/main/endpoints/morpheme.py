from pathlib import Path
from typing import List

from fastapi.routing import APIRouter
from loguru import logger
from rootski.config.config import Config
from rootski.main.endpoints.breakdown.docs import ExampleResponse, make_apidocs_responses_obj
from rootski.schemas.core import Services
from rootski.schemas.morpheme import CompleteMorpheme
from rootski.services.database.dynamo import models as dynamo
from rootski.services.database.dynamo.actions.morpheme import get_all_morphemes

# from rootski.services.database.database import DBService
from rootski.services.database.dynamo.db_service import DBService as DynamoDBService
from rootski.services.database.dynamo.models2schemas import morpheme as models2schemas
from rootski.services.database.make_morphemes_json import make_morphemes_json

# from sqlalchemy.orm.session import Session
from starlette.requests import Request
from starlette.responses import FileResponse

router = APIRouter()


@router.get(
    "/morpheme/morphemes.json",
    responses={
        200: make_apidocs_responses_obj(
            [
                ExampleResponse(
                    title="Morpheme Index",
                    body={
                        "1": {
                            "morpheme_id": 1,
                            "morpheme": "баб",
                            "type": "root",
                            "word_pos": "any",
                            "family_id": 0,
                            "meanings": [{"meaning": "old woman"}],
                            "level": 4,
                            "family": "баб",
                        },
                        "2": {
                            "morpheme_id": 2,
                            "morpheme": "бав",
                            "type": "root",
                            "word_pos": "any",
                            "family_id": 1,
                            "meanings": [{"meaning": "being,be"}],
                            "level": 2,
                            "family": "бав,бв,быв",
                        },
                    },
                ),
            ]
        )
    },
)
async def get_morphemes_json(request: Request, force: bool = False):
    """
    Get the morphemes.json file. This is used on the frontend as
    an index of morphemes. This endpoint allows the frontend to fetch
    all morphemes along with their data in one round trip.

    One use of this is that it makes the performace of the breakdown
    widget very fast.

    NOTE: if the morphemes.json file does not exist locally, it
    will be created here and cached on disk.

    Query parameters:
        force (boolean): forces regeneration of the morphemes.json file
    """
    app_config: Config = request.app.state.config

    morphemes_json_fpath = app_config.static_morphemes_json_fpath
    if force or not Path.exists(morphemes_json_fpath):
        # Set up services
        logger.info(f"Generating morphemes.json from scratch. force was {force}")
        app_services: Services = request.app.state.services
        dynamo_db_service: DynamoDBService = app_services.dynamo

        # Get all dynamo_morphemes and convert them to CompleteMorpheme schemas
        dynamo_morphemes: List[dynamo.Morpheme] = get_all_morphemes(db=dynamo_db_service)
        complete_morphemes: List[CompleteMorpheme] = [
            models2schemas.dynamo_to_pydantic__complete_morpheme(morpheme=dynamo_morpheme)
            for dynamo_morpheme in dynamo_morphemes
        ]

        # Write the morpheme data to a json object
        make_morphemes_json(complete_morphemes=complete_morphemes, morphemes_json_fpath=morphemes_json_fpath)

    return FileResponse(morphemes_json_fpath, media_type="application/json")
