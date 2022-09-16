from loguru import logger as LOGGER
from mypy_boto3_dynamodb.type_defs import PutItemOutputTableTypeDef
from rootski.services.database.dynamo.actions.dynamo import get_item_from_dynamo_response, get_item_status_code
from rootski.services.database.dynamo.db_service import DBService as DynamoDBService
from rootski.services.database.dynamo.errors import (
    USER_ALREADY_REGISTERED_MSG,
    USER_NOT_FOUND_MSG,
    UserAlreadyRegisteredError,
    UserNotFoundError,
)
from rootski.services.database.dynamo.models.user import User, make_keys


def upsert_user(email: str, is_admin: bool, db: DynamoDBService) -> None:
    user_to_upsert = User(email=email, is_admin=is_admin)
    response: PutItemOutputTableTypeDef = db.rootski_table.put_item(Item=user_to_upsert.to_item())
    return User(email=email, is_admin=is_admin)


def get_user(email: str, db: DynamoDBService) -> User:
    dynamo_table_name = db.rootski_table.name
    dynamo_db = db.rootski_table

    keys = make_keys(email=email)
    get_user_response = dynamo_db.get_item(Key=keys)
    if get_item_status_code(item_output=get_user_response) == 404 or "Item" not in get_user_response.keys():
        raise UserNotFoundError(USER_NOT_FOUND_MSG.format(email=email, dynamo_table_name=dynamo_table_name))

    user_dict = get_item_from_dynamo_response(get_user_response)
    user = User.from_dict(user_dict=user_dict)
    return user


def register_user(email: str, is_admin: bool, db: DynamoDBService) -> User:
    """Add the user information to the database.

    :param session: used to check if the user already exists and add the user to the db
    :param email: email of the user
    :param is_admin: sets the "is_admin" field of the user to this value in the db

    :raises UserAlreadyRegisteredError: if the user is already registered, the caller
        of this function should have checked this in advance

    :returns: model of the registered user
    """
    # query database for the current user
    # user_in_db: Optional[orm.User] = session.query(orm.User).filter_by(email=email).first()
    try:
        user_in_db = get_user(email=email, db=db)
    except UserNotFoundError:
        LOGGER.info(f"User not found for {email}, will register.")
    else:
        raise UserAlreadyRegisteredError(USER_ALREADY_REGISTERED_MSG.format(email=email))

    # add the user to the database
    LOGGER.info(f"Registering user {email} in dynamo database.")
    user_in_db: User = upsert_user(email=email, is_admin=is_admin, db=db)

    return user_in_db
