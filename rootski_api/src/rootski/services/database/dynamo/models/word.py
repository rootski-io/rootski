from dataclasses import dataclass
from typing import Dict, Literal, TypedDict

from rootski.services.database.dynamo.models.base import DynamoModel

WORD_POS_ENUM = Literal[
    "noun", "adjective", "verb", "adverb", "particle", "preposition", "pronoun", "conjunction"
]


class Word_(TypedDict):
    word_id: str
    word: str
    accent: str
    pos: WORD_POS_ENUM
    frequency: int


@dataclass
class Word(DynamoModel):

    data: dict
    __type: Literal["WORD"] = "WORD"

    @property
    def word_id(self) -> str:
        return str(self.data["word"]["word_id"])

    @property
    def pk(self) -> str:
        return make_pk(word_id=self.word_id)

    @property
    def sk(self) -> str:
        return make_sk(word_id=self.word_id)

    @property
    def keys(self) -> Dict[str, str]:
        return make_keys(word_id=self.word_id)

    @property
    def word_pos(self) -> str:
        return self.data["word"]["pos"]

    def to_item(self) -> dict:
        data = {**self.data}
        data["word"]["word_id"] = self.word_id
        return {**self.keys, **data, "__type": self.__type}


def make_pk(word_id: str) -> str:
    return f"WORD#{word_id}"


def make_sk(word_id: str) -> str:
    return make_pk(word_id=word_id)


def make_keys(word_id: str) -> Dict[str, str]:
    return {
        "pk": make_pk(word_id=word_id),
        "sk": make_sk(word_id=word_id),
    }
