import pandas as pd
from fastapi import APIRouter, Request
from loguru import logger

from rootski.schemas.core import Services
from rootski.services.database import DBService


router = APIRouter()


@router.get("/search/{search_term}")
async def get_matching_search_terms(search_term: str, request: Request):
    app_services: Services = request.app.state.services
    db_service: DBService = app_services.db
    engine = db_service.sync_engine

    words = pd.read_sql(
        f"""
        SELECT
            word,
            id AS word_id,
            pos,
            COALESCE(frequency, -1) AS frequency
        FROM words WHERE word LIKE '{search_term}%%' LIMIT 100
    """,
        con=engine,
    )
    words.frequency = words.frequency.astype(int)

    to_return = {"words": words.to_dict(orient="records")}
    logger.debug(str(to_return))
    return to_return
