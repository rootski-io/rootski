"""
Entrypoing for the Rootski API.

To run this API with ``gunicorn``, use the following command:

.. code-block:: bash

    gunicorn rootski.main.main:create_app() --bind 0.0.0.0:3333
"""

from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from rootski.config.config import Config
from rootski.main.endpoints.breakdown.routes import router as breakdown_router
from rootski.main.endpoints.graphql import router as graphql_router
from rootski.main.endpoints.morpheme import router as morpheme_router
from rootski.main.endpoints.search import router as search_router
from rootski.main.endpoints.word import router as word_router
from rootski.schemas.core import Services
from rootski.services.auth import AuthService
from rootski.services.database import DBService
from rootski.services.database.dynamo.db_service import DBService as DynamoDBService
from rootski.services.logger import LoggingService
from starlette.middleware.cors import CORSMiddleware


def create_app(
    config: Optional[Config] = None,
) -> FastAPI:

    if not config:
        config = Config()

    app = FastAPI(title="Rootski API")
    app.state.config: Config = config
    app.state.services = Services(
        auth=AuthService.from_config(config=config),
        db=DBService.from_config(config=config),
        logger=LoggingService.from_config(config=config),
        dynamo=DynamoDBService.from_config(config=config),
    )

    # configure startup behavior: initialize services on startup
    @app.on_event("startup")
    async def on_startup():
        services: Services = app.state.services

        logging_service: LoggingService = services.logger
        auth_service: AuthService = services.auth
        db_service: DBService = services.db
        dynamo_service: DynamoDBService = services.dynamo

        # logging should be initialized first since it alters a global logger variable
        logging_service.init()
        auth_service.init()
        db_service.init()
        dynamo_service.init()

        # # ensure that the static assets dir exists (for morphemes.json)
        Path(config.static_assets_dir).mkdir(exist_ok=True, parents=True)

    # add routes
    app.include_router(breakdown_router, tags=["Breakdowns"])
    app.include_router(search_router, tags=["Words"])
    app.include_router(word_router, tags=["Words"])
    app.include_router(morpheme_router, tags=["Morphemes"])
    app.include_router(graphql_router, tags=["GraphQL"])

    # add authorized CORS origins (add these origins to response headers to
    # enable frontends at these origins to receive requests from this API)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


def create_default_app():
    config = Config()
    return create_app(config=config)


if __name__ == "__main__":
    config = Config()
    app = create_app(config=config)
    uvicorn.run(app, host=config.host, port=config.port)
