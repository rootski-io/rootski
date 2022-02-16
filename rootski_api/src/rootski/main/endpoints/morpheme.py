from pathlib import Path

from fastapi.routing import APIRouter
from loguru import logger
from sqlalchemy.orm.session import Session
from starlette.requests import Request
from starlette.responses import FileResponse

from rootski.config.config import Config
from rootski.main.endpoints.breakdown.docs import (
    ExampleResponse,
    make_apidocs_responses_obj,
)
from rootski.schemas.core import Services
from rootski.services.database.database import DBService
from rootski.services.database.make_morphemes_json import make_morphemes_json

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
        logger.info(f"Generating morphemes.json from scratch. force was {force}")
        app_services: Services = request.app.state.services
        db_service: DBService = app_services.db
        session: Session = db_service.get_sync_session()
        make_morphemes_json(session=session, morphemes_json_fpath=morphemes_json_fpath)

    return FileResponse(morphemes_json_fpath, media_type="application/json")
