from typing import List, Literal, Optional

from pydantic import BaseModel, Field
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
    word_id: str
    word: str
    accent: str
    pos: WORD_POS_ENUM
    frequency: Optional[int]

    class Config:
        orm_mode = True


class WordInDb(Word):
    breakdowns: List[BreakdownInDB]

    class Config:
        use_enum_values = True
        orm_mode = True


#######################
# --- Definitions --- #
#######################


class SubDefinition(BaseModel):
    sub_def_id: int
    sub_def_position: int
    definition: str
    notes: Optional[str]


class Definition(BaseModel):
    def_position: int
    definition_id: int
    sub_defs: List[SubDefinition]


class DefinitionForPOS(BaseModel):
    pos: WORD_POS_ENUM
    definitions: List[Definition]


#############################
# --- Example Sentences --- #
#############################


class ExampleSentence(BaseModel):
    rus: str
    eng: str
    exact_match: bool


#########################
# --- Base Response --- #
#########################


class WordResponse(BaseModel):
    word: Word
    definitions: List[DefinitionForPOS]
    sentences: List[ExampleSentence]


#########################
# --- Noun Response --- #
#########################


class NounDeclensions(BaseModel):
    gender: Optional[Literal["m", "f", "n"]]
    animate: Optional[bool]
    indeclinable: Optional[bool]

    nom: Optional[str]
    acc: Optional[str]
    prep: Optional[str]
    gen: Optional[str]
    dat: Optional[str]
    inst: Optional[str]
    nom_pl: Optional[str]
    acc_pl: Optional[str]
    prep_pl: Optional[str]
    gen_pl: Optional[str]
    dat_pl: Optional[str]
    inst_pl: Optional[str]


class NounResponse(WordResponse):
    declensions: Optional[NounDeclensions]


#############################
# --- AdjectiveResponse --- #
#############################


class AdjectiveShortForms(BaseModel):
    comp: Optional[str]
    fem_short: Optional[str]
    masc_short: Optional[str]
    neut_short: Optional[str]
    plural_short: Optional[str]


class AdjectiveResponse(WordResponse):
    short_forms: Optional[AdjectiveShortForms]


#########################
# --- Verb Response --- #
#########################


class VerbConjugations(BaseModel):
    aspect: Optional[Literal["perf", "impf"]]
    c__1st_per_sing: Optional[str] = Field(alias="1st_per_sing")
    c__2nd_per_sing: Optional[str] = Field(alias="2nd_per_sing")
    c__3rd_per_sing: Optional[str] = Field(alias="3rd_per_sing")
    c__1st_per_pl: Optional[str] = Field(alias="1st_per_pl")
    c__2nd_per_pl: Optional[str] = Field(alias="2nd_per_pl")
    c__3rd_per_pl: Optional[str] = Field(alias="3rd_per_pl")
    past_m: Optional[str]
    past_f: Optional[str]
    past_n: Optional[str]
    past_pl: Optional[str]
    actv_part: Optional[str]
    pass_part: Optional[str]
    actv_past_part: Optional[str]
    pass_past_part: Optional[str]
    gerund: Optional[str]
    impr: Optional[str]
    impr_pl: Optional[str]


class VerbAspectualPair(BaseModel):
    imp_word_id: Optional[str]
    imp_accent: Optional[str]
    pfv_word_id: Optional[str]
    pfv_accent: Optional[str]


class VerbResponse(WordResponse):
    conjugations: VerbConjugations
    aspectual_pairs: List[VerbAspectualPair]
