"""
NOTE: remember to cast all IDs to strings
"""

from dataclasses import dataclass
from typing import Dict, List, Literal, Type, TypedDict

from rootski.schemas.morpheme import MORPHEME_TYPE_ENUM, MORPHEME_WORD_POS_ENUM
from rootski.services.database.dynamo.models.base import DynamoModel, replace_decimals
from rootski.services.database.dynamo.models.morpheme import Morpheme


class MorphemeItem(TypedDict):
    morpheme_id: str
    morpheme: str


@dataclass(frozen=True)
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

    @classmethod
    def from_dict(cls: Type["MorphemeFamily"], morpheme_family_dict: dict) -> "MorphemeFamily":
        cleaned_morpheme_family_dict = replace_decimals(morpheme_family_dict)

        return cls(
            type=cleaned_morpheme_family_dict["type"],
            word_pos=cleaned_morpheme_family_dict["word_pos"],
            family_id=cleaned_morpheme_family_dict["family_id"],
            level=cleaned_morpheme_family_dict["level"],
            family_meanings=cleaned_morpheme_family_dict["family_meanings"],
            morphemes=[
                make_dynamo_MorphemeItem_from_dict(morpheme_dict)
                for morpheme_dict in cleaned_morpheme_family_dict["morphemes"]
            ],
        )


def make_dynamo_MorphemeItem_from_dict(morpheme_item_dict: dict) -> MorphemeItem:
    return MorphemeItem(morpheme=morpheme_item_dict["morpheme"], morpheme_id=morpheme_item_dict["morpheme_id"])


def make_pk(morpheme_family_id: str) -> str:
    return f"MORPHEME_FAMILY#{morpheme_family_id}"


def make_keys(morpheme_family_id: str) -> Dict[str, str]:
    return {
        "pk": make_pk(morpheme_family_id=morpheme_family_id),
        "sk": make_pk(morpheme_family_id=morpheme_family_id),
    }
