from typing import List

from fastapi import APIRouter, Request
from rootski.schemas.core import Services
from rootski.services.database.dynamo.actions.search_words import search_words
from rootski.services.database.dynamo.db_service import DBService as DynamoDBService
from rootski.services.database.dynamo.models import word_for_search as dynamo_models
from rootski.services.database.dynamo.models2schemas.search_words import dynamo_to_pydantic__word_for_search

from rootski import schemas

router = APIRouter()

@router.get("/search/{search_term}")
async def get_matching_search_terms(search_term: str, request: Request):
    app_services: Services = request.app.state.services
    dynamo: DynamoDBService = app_services.dynamo
    search_results: List[dynamo_models.WordForSearch] = search_words(query=search_term, limit=100, db=dynamo)
    search_result_schemas: List[schemas.SearchWord] = [
        dynamo_to_pydantic__word_for_search(model=word_for_search) for word_for_search in search_results
    ]
    return schemas.SearchResponse(words=search_result_schemas)
