"""
NOTE: remember to cast all IDs to strings
"""

from dataclasses import dataclass
from typing import Dict, Literal, Optional, TypedDict
from uuid import uuid4

from dynamodb_play.models.base import DynamoModel


class BreakdownItemItem(TypedDict):

    position: str
    morpheme_id: Optional[str]
    morpheme: str
    morpheme_family_id: Optional[str]


@dataclass(frozen=True)
class NullBreakdownItem(DynamoModel):

    word_id: str
    position: int
    morpheme: str
    submitted_by_user_email: Optional[str]
    __type: Literal["BREAKDOWN_ITEM_NULL"] = "BREAKDOWN_ITEM_NULL"

    @property
    def pk(self) -> str:
        return make_pk(word_id=self.word_id)

    @property
    def sk(self) -> str:
        fake_morpheme_family_id = str(uuid4())
        return make_sk(morpheme_family_id=fake_morpheme_family_id, position=self.position)

    def to_item(self) -> dict:
        return {
            **self.keys,
            "__type": self.__type,
            "word_id": str(self.word_id),
            "position": self.position,
            "morpheme": self.morpheme,
            "morpheme_id": None,
            "family_id": None,
            "submitted_by_user_email": self.submitted_by_user_email,
        }

    def to_BreakdownItemItem(self) -> BreakdownItemItem:
        return BreakdownItemItem(
            position=self.position, morpheme_id=None, morpheme=self.morpheme, morpheme_family_id=None
        )


@dataclass(frozen=True)
class BreakdownItem(DynamoModel):

    word_id: str
    position: int
    morpheme_family_id: Optional[str]
    morpheme: str
    morpheme_id: str
    submitted_by_user_email: Optional[str]
    breakdown_id: int
    __type: Literal["BREAKDOWN_ITEM"] = "BREAKDOWN_ITEM"

    @property
    def pk(self) -> str:
        return make_pk(word_id=self.word_id)

    @property
    def sk(self) -> str:
        return make_sk(morpheme_family_id=self.morpheme_family_id, position=self.position)

    @property
    def gsi1pk(self) -> str:
        return make_gsi1pk(morpheme_family_id=self.morpheme_family_id)

    @property
    def gsi1sk(self) -> str:
        return make_gsi1sk(submitted_by_user_email=self.submitted_by_user_email)

    def to_item(self) -> dict:
        return {
            **self.keys,
            "__type": self.__type,
            "word_id": str(self.word_id),
            "morpheme_family_id": str(self.morpheme_family_id),
            "morpheme": self.morpheme,
            "morpheme_id": str(self.morpheme_id),
            "submitted_by_user_email": self.submitted_by_user_email,
            "breakdown_id": self.breakdown_id,
        }

    def to_BreakdownItemItem(self) -> BreakdownItemItem:
        return BreakdownItemItem(
            position=self.position,
            morpheme_id=self.morpheme_id,
            morpheme=self.morpheme,
            morpheme_family_id=self.morpheme_family_id,
        )


def make_pk(word_id: str) -> str:
    return f"WORD#{word_id}"


def make_sk(morpheme_family_id: str, position: int) -> str:
    return f"BREAKDOWN_ITEM#{morpheme_family_id}#{position}"


def make_gsi1pk(morpheme_family_id: str) -> str:
    return f"MORPHEME_FAMILY#{morpheme_family_id}"


def make_gsi1sk(submitted_by_user_email: str) -> str:
    return f"BREAKDOWN#{submitted_by_user_email}"


def make_keys(word_id: str, morpheme_family_id: str, position: int) -> Dict[str, str]:
    return {
        "pk": make_pk(word_id=word_id),
        "sk": make_sk(morpheme_family_id=morpheme_family_id, position=position),
    }


def make_gsi1_keys(morpheme_family_id: str, submitted_by_user_email: str) -> Dict[str, str]:
    return {
        "gsi1pk": make_gsi1pk(morpheme_family_id=morpheme_family_id),
        "gsi1sk": make_gsi1sk(submitted_by_user_email=submitted_by_user_email),
    }
