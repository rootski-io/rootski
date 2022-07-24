from dataclasses import dataclass
from dynamodb_play.models.base import DynamoModel


@dataclass
class Word(DynamoModel):

    word_id: str

    @property
    def pk(self) -> str:
        return f"WORD#{self.word_id}"

    @property
    def sk(self) -> str:
        return self.pk
