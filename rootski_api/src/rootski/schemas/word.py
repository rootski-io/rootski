from typing import List, Literal

from pydantic import BaseModel

from rootski.schemas import BreakdownInDB

WORD_POS_ENUM = Literal[
    "noun",
    "verb",
    "particle",
    "adjective",
    "preposition",
    "participle",
    "pronoun",
    "conjunction",
    "adverb",
    "interjection",
]

# class WordPOS(Enum):
#     NOUN = "noun"
#     VERB = "verb"
#     PARTICLE = "particle"
#     ADJECTIVE = "adjective"
#     PREPOSITION = "preposition"
#     PARTICIPLE = "participle"
#     PRONOUN = "pronoun"
#     CONJUNCTION = "conjunction"
#     ADVERB = "adverb"
#     INTERJECTION = "interjection"


class Word(BaseModel):
    id: int
    word: str
    accent: str
    pos: WORD_POS_ENUM
    frequency: int

    class Config:
        orm_mode = True


class WordInDb(Word):
    breakdowns: List[BreakdownInDB]

    class Config:
        use_enum_values = True
        orm_mode = True
