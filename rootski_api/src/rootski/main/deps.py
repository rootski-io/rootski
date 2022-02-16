"""
Dependencies for the endpoints.

The goal is to create all dependencies using a Config class
so that the app can be configured differently for testing and production.
"""
from typing import Generator, Optional

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from rootski import schemas
from rootski.config.config import ANON_USER
from rootski.errors import UserAlreadyRegisteredError
from rootski.gql.context import RootskiGraphQLContext
from rootski.schemas import Services
from rootski.services.database import DBService
from rootski.services.database import models as orm

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
    db: Session = Depends(get_session), email: str = Depends(get_authorized_user_email_or_anon)
) -> schemas.User:
    """Retrieve the data of the current user from the database."""
    if email == ANON_USER:
        return schemas.User(email=ANON_USER, is_admin=False)

    # try to fetch the user's information in case they are already registered
    user_in_db: Optional[orm.User] = db.query(orm.User).filter_by(email=email).first()

    print("USER IN DB", user_in_db)

    # If the current user isn't registered, register them. They've only made
    # it this far it they authenticated with cognito and have a signed JWT
    # token with their email in it.
    current_user: Optional[schemas.User] = None
    if user_in_db:
        current_user = schemas.User.from_orm(user_in_db)
    else:
        current_user: schemas.User = register_user(session=db, email=email, is_admin=False)

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


############################
# --- Helper functions --- #
############################


def register_user(session: Session, email: str, is_admin: bool = False) -> schemas.User:
    """Add the user information to the database.

    :param session: used to check if the user already exists and add the user to the db
    :param email: email of the user
    :param is_admin: sets the "is_admin" field of the user to this value in the db

    :raises UserAlreadyRegisteredError: if the user is already registered, the caller
        of this function should have checked this in advance

    :returns: model of the registered user
    """
    # query database for the current user
    user_in_db: Optional[orm.User] = session.query(orm.User).filter_by(email=email).first()

    if user_in_db is not None:
        raise UserAlreadyRegisteredError(f'User with email "{email}" is already registered.')

    # add the user to the database
    user_in_db = orm.User(email=email, is_admin=is_admin)
    session.add(user_in_db)
    session.commit()

    return schemas.User.from_orm(user_in_db)
