from dataclasses import dataclass
from typing import Dict, Literal, Union

from rootski.services.database.dynamo.models.base import DynamoModel
from rootski.services.database.dynamo.models.word import WORD_POS_ENUM


@dataclass
class WordForSearch(DynamoModel):

    word: str
    word_id: str
    pos: Union[WORD_POS_ENUM, Literal["deprecated"]]
    frequency: int = -1

    __type: Literal["WORD"] = "WORD_FOR_SEARCH"

    @property
    def pk(self) -> str:
        return make_pk()

    @property
    def sk(self) -> str:
        return make_sk(word=self.word)

    @property
    def keys(self) -> Dict[str, str]:
        return make_keys(word=self.word)

    def to_item(self) -> dict:
        return {
            **self.keys,
            "word": self.word,
            "word_id": self.word_id,
            "frequency": int(self.frequency) if self.frequency not in [None, -1] else -1,
            "pos": self.pos,
            "__type": self.__type,
        }


def make_pk() -> str:
    return "WORD"


def make_sk(word: str) -> str:
    return word


def make_keys(word: str) -> Dict[str, str]:
    return {
        "pk": make_pk(),
        "sk": make_sk(word=word),
    }
