from dataclasses import dataclass
from typing import Dict

from dynamodb_play.models.base import DynamoModel


@dataclass
class Word(DynamoModel):

    word_id: str

    @property
    def pk(self) -> str:
        return make_pk(word_id=self.word_id)

    @property
    def sk(self) -> str:
        return make_sk(word_id=self.word_id)

    @property
    def keys(self) -> Dict[str, str]:
        return make_keys(word_id=self.word_id)


def make_pk(word_id: str) -> str:
    return f"WORD#{word_id}"


def make_sk(word_id: str) -> str:
    return make_pk(word_id=word_id)


def make_keys(word_id: str) -> Dict[str, str]:
    return {
        "pk": make_pk(word_id=word_id),
        "sk": make_sk(word_id=word_id),
    }
