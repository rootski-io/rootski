"""
Dependencies for the endpoints.

The goal is to create all dependencies using a Config class
so that the app can be configured differently for testing and production.
"""
from typing import Generator, Optional

import rootski.services.database.dynamo.models as dynamo_models
from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from rootski.config.config import ANON_USER
from rootski.gql.context import RootskiGraphQLContext
from rootski.schemas import Services
from rootski.services.database import DBService
from rootski.services.database.dynamo.actions.user import UserNotFoundError, get_user, register_user
from rootski.services.database.dynamo.db_service import DBService as DynamoDBService
from rootski.services.database.dynamo.models2schemas.user import dynamo_to_pydantic__user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from rootski import schemas

################################
# --- FastAPI Dependencies --- #
################################


async def filter_valid_token(
    request: Request, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """Return the token if it is valid, otherwise return None. None is taken to be the anon user."""
    if credentials:
        token: str = credentials.credentials
        app_services: Services = request.app.state.services
        if not app_services.auth.token_is_valid(token):
            logger.error(f'Got malformed token "{str(token)}".')
            raise HTTPException(status_code=401, detail="Authorization token is invalid. See logs for details.")
        return token
    return None


async def get_authorized_user_email_or_anon(request: Request, token: str = Depends(filter_valid_token)) -> str:
    """
    :raises AuthServiceError: if the token is not wellformed
    """
    app_services: Services = request.app.state.services
    if not token or token.strip() == "":
        return ANON_USER
    return app_services.auth.get_token_email(token)


def get_session(request: Request) -> Generator[Session, None, None]:
    """Initiate a DB session that will be closed when a request finishes."""
    db_service: DBService = request.app.state.services.db
    with db_service.get_sync_session() as session:
        yield session


async def get_async_session(request: Request) -> Generator[AsyncSession, None, None]:
    """Initiate a DB session that will be closed when a request finishes."""
    db_service: DBService = request.app.state.services.db
    async with db_service.get_async_session() as session:
        yield session


async def get_current_user(
    request: Request, email: str = Depends(get_authorized_user_email_or_anon)
) -> schemas.User:
    """Retrieve the data of the current user from the database."""

    services: Services = request.app.state.services
    dynamo: DynamoDBService = services.dynamo

    if email == ANON_USER:
        return schemas.User(email=ANON_USER, is_admin=False)

    # try to fetch the user's information in case they are already registered
    current_user_in_db: Optional[dynamo_models.User] = None
    try:
        current_user_in_db: dynamo_models.User = get_user(email=email, db=dynamo)
    except UserNotFoundError:
        ...

    # If the current user isn't registered, register them. They've only made
    # it this far it they authenticated with cognito and have a signed JWT
    # token with their email in it.
    current_user: Optional[schemas.User] = None
    if current_user_in_db:
        current_user_dynamo_model: dynamo_models.User = get_user(email=email, db=dynamo)
        current_user: schemas.User = dynamo_to_pydantic__user(dynamo_user=current_user_dynamo_model)
    else:
        register_user(email=email, is_admin=False, db=dynamo)
        current_user = schemas.User(email=email, is_admin=False)

    return current_user


def get_graphql_context(
    request: Request,
    db: Session = Depends(get_async_session),
    user: schemas.User = Depends(get_current_user),
) -> RootskiGraphQLContext:
    """Prepare the context object used by GraphQL resolvers."""
    return RootskiGraphQLContext(
        request=request,
        session=db,
        user=user,
    )
