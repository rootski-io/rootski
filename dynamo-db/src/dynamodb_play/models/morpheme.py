"""
NOTE: remember to cast all IDs to strings
"""

from dataclasses import dataclass
from typing import List, Literal
from dynamodb_play.models.base import DynamoModel

from rootski.schemas.morpheme import MORPHEME_TYPE_ENUM, MORPHEME_WORD_POS_ENUM


@dataclass
class MorphemeFamily(DynamoModel):

    type: MORPHEME_TYPE_ENUM
    word_pos: MORPHEME_WORD_POS_ENUM
    family_id: str  # these should be converted to strings
    family_meanings: List[str]
    level: int
    family: str  # comma separated list of morpheme variants

    __type: Literal["MORPHEME_FAMILY"] = "MORPHEME_FAMILY"

    @property
    def pk(self) -> str:
        return f"MORPHEME_FAMILY#{self.family_id}"

    @property
    def sk(self) -> str:
        return self.pk

    def to_dict(self) -> dict:
        return {
            **self.keys,
            "__type": self.__type,
            "type": self.type,
            "word_pos": self.word_pos,
            "family_id": str(self.family_id),
            "level": self.level,
            "family": self.family,
            "family_meanings": self.family_meanings,
        }


@dataclass
class Morpheme(DynamoModel):

    morpheme: str
    morpheme_id: str
    family_id: str

    __type: Literal["MORPHEME"] = "MORPHEME"

    @property
    def pk(self) -> str:
        return f"MORPHEME_FAMILY#{self.family_id}"

    @property
    def sk(self) -> str:
        return f"MORPHEME#{self.morpheme_id}"

    @property
    def gsi1pk(self) -> str:
        return self.sk

    @property
    def gsi1sk(self) -> str:
        return self.sk

    def to_dict(self) -> dict:
        return {
            **self.keys,
            "__type": self.__type,
            "family_id": self.family_id,
            "morpheme": self.morpheme,
            "morpheme_id": self.morpheme_id,
        }
