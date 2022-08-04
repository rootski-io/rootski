"""
NOTE: remember to cast all IDs to strings
"""

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Union

from dynamodb_play.models.base import DynamoModel
from dynamodb_play.models.breakdown_item import BreakdownItem, NullBreakdownItem


@dataclass(frozen=True)
class Breakdown(DynamoModel):

    word: str
    word_id: int
    submitted_by_user_email: Optional[str]
    is_verified: bool
    is_inference: bool
    date_submitted: str
    date_verified: Optional[str]
    breakdown_items: List[Union[BreakdownItem, NullBreakdownItem]]
    __type: Literal["BREAKDOWN"] = "BREAKDOWN"

    @property
    def pk(self) -> str:
        return make_pk(word_id=self.word_id)

    @property
    def sk(self) -> str:
        return make_sk()

    @property
    def gsi1pk(self) -> str:
        return make_gsi1pk(submitted_by_user_email=self.submitted_by_user_email)

    @property
    def gsi1sk(self) -> str:
        return make_pk(word_id=self.word_id)

    @property
    def gsi2pk(self) -> str:
        return make_pk(word_id=self.word_id)

    @property
    def gsi2sk(self) -> str:
        return make_gsi1pk(submitted_by_user_email=self.submitted_by_user_email)

    def to_item(self) -> dict:
        return {
            **self.keys,
            "__type": self.__type,
            "word": self.word,
            "word_id": str(self.word_id),
            "submitted_by_user_email": self.submitted_by_user_email,
            "is_verified": self.is_verified,
            "is_inference": self.is_inference,
            "date_submitted": self.date_submitted,
            "date_verified": self.date_verified,
            "breakdown_items": [b.to_BreakdownItemItem() for b in self.breakdown_items],
        }


def make_pk(word_id: str) -> str:
    return f"WORD#{word_id}"


def make_sk() -> str:
    return "BREAKDOWN"


def make_gsi1pk(submitted_by_user_email: str) -> str:
    return f"USER#{submitted_by_user_email}"


def make_keys(word_id: str) -> Dict[str, str]:
    return {
        "pk": make_pk(word_id=word_id),
        "sk": make_sk(),
    }


def make_gsi1_keys(submitted_by_user_email: str, word_id: str) -> Dict[str, str]:
    return {
        "gsi1pk": make_gsi1pk(submitted_by_user_email=submitted_by_user_email),
        "gsi1sk": make_pk(word_id=word_id),
    }


def make_gsi2_keys(word_id: str, submitted_by_user_email: str) -> Dict[str, str]:
    return {
        "gsi2pk": make_pk(word_id=word_id),
        "gsi2sk": make_gsi1pk(submitted_by_user_email=submitted_by_user_email),
    }
