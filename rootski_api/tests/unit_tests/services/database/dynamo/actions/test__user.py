import pytest
from rootski.services.database.dynamo.actions.user import UserNotFoundError, get_user, upsert_user
from rootski.services.database.dynamo.db_service import DBService as DynamoDBService
from rootski.services.database.dynamo.models.user import User

TEST_USER = {
    "pk": "USER#new_user@gmail.com",
    "sk": "USER#new_user@gmail.com",
    "email": "new_user@gmail.com",
    "is_admin": False,
}

TEST_USER_AS_ADMIN = {
    "pk": "USER#new_user@gmail.com",
    "sk": "USER#new_user@gmail.com",
    "email": "new_user@gmail.com",
    "is_admin": True,
}


def test__upsert_user(dynamo_db_service: DynamoDBService):
    # first, try to read a non-existent user
    with pytest.raises(UserNotFoundError):
        get_user(email=TEST_USER["email"], db=dynamo_db_service)

    # insert a user
    upsert_user(email=TEST_USER["email"], is_admin=True, db=dynamo_db_service)

    # verify we can read the inserted user
    user: User = get_user(email=TEST_USER["email"], db=dynamo_db_service)
    assert user.email == TEST_USER["email"]
    assert user.is_admin

    # mutate the user
    upsert_user(email=TEST_USER["email"], is_admin=False, db=dynamo_db_service)
    user: User = get_user(email=TEST_USER["email"], db=dynamo_db_service)
    assert user.email == TEST_USER["email"]
    assert not user.is_admin
