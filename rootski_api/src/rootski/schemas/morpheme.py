from typing import List, Literal, Optional

from pydantic import BaseModel, constr

# morpheme types
MORPHEME_TYPE_PREFIX = "prefix"
MORPHEME_TYPE_ROOT = "root"
MORPHEME_TYPE_SUFFIX = "suffix"
MORPHEME_TYPE_LINK = "link"
MORPHEME_TYPE_NULL = None

# typing.Literal's play more nicely with pydantic and strawberry than
# the builtin enum.Enum type
MORPHEME_TYPE_ENUM = Literal[
    MORPHEME_TYPE_PREFIX, MORPHEME_TYPE_ROOT, MORPHEME_TYPE_SUFFIX, MORPHEME_TYPE_LINK, MORPHEME_TYPE_NULL
]

# parts of speech of the words that a morpheme typically shows up in
MORPHEME_WORD_POS_ANY = "any"
MORPHEME_WORD_POS_ADJECTIVE = "adjective"
MORPHEME_WORD_POS_NOUN = "noun"
MORPHEME_WORD_POS_VERB = "verb"

MORPHEME_WORD_POS_ENUM = Literal[
    MORPHEME_WORD_POS_ANY,
    MORPHEME_WORD_POS_ADJECTIVE,
    MORPHEME_WORD_POS_NOUN,
    MORPHEME_WORD_POS_VERB,
]
MORPHEME_WORD_POS_VALUES = [
    MORPHEME_WORD_POS_ANY,
    MORPHEME_WORD_POS_ADJECTIVE,
    MORPHEME_WORD_POS_NOUN,
    MORPHEME_WORD_POS_VERB,
]


class Morpheme(BaseModel):
    morpheme_id: int
    morpheme: constr(max_length=256)
    type: MORPHEME_TYPE_ENUM
    word_pos: MORPHEME_WORD_POS_ENUM
    family_id: Optional[int]  # required in DB, but not in schema


class MorphemeFamily(BaseModel):
    id: int
    family: constr(max_length=256)
    level: int


class MorphemeFamilyInDb(MorphemeFamily):
    class Config:
        orm_mode = True


class MorphemeInDb(Morpheme):
    family: MorphemeFamilyInDb
    family_id: int

    class Config:
        orm_mode = True


class MorphemeFamilyMeaning(BaseModel):
    id: int
    family_id: int
    meaning: constr(max_length=256)

    class Config:
        orm_mode = True


class MorphemeFamilyInDb(MorphemeFamily):
    morphemes: List[Morpheme]
    meanings: List[MorphemeFamilyMeaning]

    class Config:
        orm_mode = True


class CompleteMorpheme(Morpheme):
    # id of morpheme in backend database; null if not an actual morpheme
    morpheme_id: int
    # morpheme text
    morpheme: str
    # type of morpheme; null if not an actual morpheme
    type: MORPHEME_TYPE_ENUM
    # part of speech of morpheme
    word_pos: MORPHEME_WORD_POS_ENUM
    # descriptions of what the root means
    meanings: List[str]
    # family which the morpheme is a member of
    family_id: int
    # level 1-6 of how common/difficult the root is; 6 is uncommon and/or difficult
    level: int
    # comma separated string of other morpheme variants in the family
    family: str
