"""
NOTE: remember to cast all IDs to strings
"""

from dataclasses import dataclass
from typing import Dict, Literal

from rootski.services.database.dynamo.models.base import DynamoModel


@dataclass
class Morpheme(DynamoModel):

    morpheme: str
    morpheme_id: str
    family_id: str

    __type: Literal["MORPHEME"] = "MORPHEME"

    @property
    def pk(self) -> str:
        return make_pk(family_id=self.family_id)

    @property
    def sk(self) -> str:
        return make_sk(morpheme_id=self.morpheme_id)

    @property
    def gsi1pk(self) -> str:
        return make_gsi1pk(morpheme_id=self.morpheme_id)

    @property
    def gsi1sk(self) -> str:
        return make_gsi1sk(morpheme_id=self.morpheme_id)

    def to_item(self) -> dict:
        return {
            **self.keys,
            "__type": self.__type,
            "family_id": self.family_id,
            "morpheme": self.morpheme,
            "morpheme_id": self.morpheme_id,
        }


def make_pk(family_id: str) -> str:
    return f"MORPHEME_FAMILY#{family_id}"


def make_sk(morpheme_id: str) -> str:
    return f"MORPHEME#{morpheme_id}"


def make_gsi1pk(morpheme_id: str) -> str:
    return make_sk(morpheme_id=morpheme_id)


def make_gsi1sk(morpheme_id: str) -> str:
    return make_sk(morpheme_id=morpheme_id)


def make_keys(family_id: str, morpheme_id: str) -> Dict[str, str]:
    return {"pk": make_pk(family_id=family_id), "sk": make_sk(morpheme_id=morpheme_id)}


def make_gsi1_keys(morpheme_id: str) -> Dict[str, str]:
    return {
        "gsi1pk": make_gsi1pk(morpheme_id=morpheme_id),
        "gsi1sk": make_gsi1sk(morpheme_id=morpheme_id),
    }
