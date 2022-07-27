"""
NOTE: remember to cast all IDs to strings
"""

from dataclasses import dataclass
from typing import List, Literal, TypedDict

from rootski.schemas.morpheme import MORPHEME_TYPE_ENUM, MORPHEME_WORD_POS_ENUM
from rootski.services.database.dynamo.models.base import DynamoModel
from rootski.services.database.dynamo.models.morpheme import Morpheme


class MorphemeItem(TypedDict):
    morpheme_id: str
    morpheme: str


@dataclass
class MorphemeFamily(DynamoModel):

    type: MORPHEME_TYPE_ENUM
    word_pos: MORPHEME_WORD_POS_ENUM
    family_id: str  # these should be converted to strings
    family_meanings: List[str]
    level: int
    morphemes: List[MorphemeItem]

    __type: Literal["MORPHEME_FAMILY"] = "MORPHEME_FAMILY"

    @property
    def pk(self) -> str:
        return f"MORPHEME_FAMILY#{self.family_id}"

    @property
    def sk(self) -> str:
        return self.pk

    def to_item(self) -> dict:
        return {
            **self.keys,
            "__type": self.__type,
            "type": self.type,
            "word_pos": self.word_pos,
            "family_id": str(self.family_id),
            "level": self.level,
            "morphemes": self.morphemes,
            "family_meanings": self.family_meanings,
        }

    def create_morphemes(self) -> List[Morpheme]:
        return [
            Morpheme(
                family_id=self.family_id,
                morpheme=m["morpheme"],
                morpheme_id=str(m["morpheme_id"]),
            )
            for m in self.morphemes
        ]
