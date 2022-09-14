import rootski.services.database.dynamo.models as dynamo
from rootski.schemas import user as schemas


def dynamo_to_pydantic__user(dynamo_user: dynamo.User) -> schemas.User:
    return schemas.User(
        email=dynamo_user.email,
        is_admin=dynamo_user.is_admin,
    )
