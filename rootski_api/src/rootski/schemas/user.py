from typing import List

from pydantic import BaseModel, EmailStr

from rootski.schemas.breakdown import Breakdown


class User(BaseModel):
    email: EmailStr
    is_admin: bool = False

    class Config:
        # this is just to make it easier to convert an orm.User to a schemas.User;
        # there isn't actually a SQLAlchemy table definition with this schema.
        # UserInDB should be used for that.
        orm_mode = True


class UserInDB(User):
    submitted_breakdowns: List[Breakdown]
    verified_breakdowns: List[Breakdown]

    class Config:
        orm_mode = True
