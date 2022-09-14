from dataclasses import dataclass
from typing import Type

from rootski.services.database.dynamo.models.base import DynamoModel


@dataclass(frozen=True)
class User(DynamoModel):
    email: str
    is_admin: bool

    @property
    def pk(self) -> str:
        return make_pk(email=self.email)

    @property
    def sk(self) -> str:
        return make_sk(email=self.email)

    def to_item(self) -> dict:
        return {
            **self.keys,
            "email": self.email,
            "is_admin": self.is_admin,
        }

    @classmethod
    def from_dict(cls: Type["User"], user_dict: dict) -> "User":
        return cls(email=user_dict["email"], is_admin=user_dict["is_admin"])


def make_pk(email: str) -> str:
    return "USER#" + email


def make_sk(email: str) -> str:
    return make_pk(email=email)


def make_keys(email: str) -> dict:
    return {
        "pk": make_pk(email),
        "sk": make_sk(email),
    }
