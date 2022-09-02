from dataclasses import dataclass
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
        return make_pk(email=self.email)

    def to_item(self) -> dict:
        return {
            **self.keys,
            "email": self.email,
            "is_admin": self.is_admin,
        }


def make_pk(email: str) -> str:
    return "USER#" + email
