"""
NOTE: remember to cast all IDs to strings
"""

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Type, Union

from rootski.services.database.dynamo.models.base import DynamoModel
from rootski.services.database.dynamo.models.breakdown_item import (
    BreakdownItem,
    NullBreakdownItem,
    make_dynamo_BreakdownItemItem_from_dict,
)


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

    @classmethod
    def from_dict(cls: Type["Breakdown"], breakdown_dict: dict) -> "Breakdown":

        return cls(
            word=breakdown_dict["word"],
            word_id=breakdown_dict["word_id"],
            submitted_by_user_email=breakdown_dict["submitted_by_user_email"],
            is_verified=breakdown_dict["is_verified"],
            is_inference=breakdown_dict["is_inference"],
            date_submitted=breakdown_dict["date_submitted"],
            date_verified=breakdown_dict["date_verified"],
            breakdown_items=[
                make_dynamo_BreakdownItemItem_from_dict(breakdown_item)
                for breakdown_item in breakdown_dict["breakdown_items"]
            ],
        )


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
