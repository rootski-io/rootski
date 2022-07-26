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
    frequency: int

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
    gender: Literal["m", "f", "n"]
    animate: bool
    indeclinable: bool

    nom: str
    acc: str
    prep: str
    gen: str
    dat: str
    inst: str
    nom_pl: str
    acc_pl: str
    prep_pl: str
    gen_pl: str
    dat_pl: str
    inst_pl: str


class NounResponse(WordResponse):
    declensions: NounDeclensions


#############################
# --- AdjectiveResponse --- #
#############################


class AdjectiveShortForms(BaseModel):
    comp: str
    fem_short: str
    masc_short: str
    neut_short: str
    plural_short: str


class AdjectiveResponse(WordResponse):
    short_forms: AdjectiveShortForms


#########################
# --- Verb Response --- #
#########################


class VerbConjugations(BaseModel):
    aspect: Literal["perf", "impv"]
    c__1st_per_sing: str = Field(alias="1st_per_sing")
    c__2nd_per_sing: str = Field(alias="2nd_per_sing")
    c__3rd_per_sing: str = Field(alias="3rd_per_sing")
    c__1st_per_pl: str = Field(alias="1st_per_pl")
    c__2nd_per_pl: str = Field(alias="2nd_per_pl")
    c__3rd_per_pl: str = Field(alias="3rd_per_pl")
    past_m: str
    past_f: str
    past_n: str
    past_pl: str
    actv_part: Optional[str]
    pass_part: Optional[str]
    actv_past_part: str
    pass_past_part: str
    gerund: str
    impr: str
    impr_pl: str


class VerbAspectualPair(BaseModel):
    imp_word_id: str
    imp_accent: str
    pfv_word_id: str
    pfv_accent: str


class VerbResponse(WordResponse):
    conjugations: VerbConjugations
    aspectual_pairs: List[VerbAspectualPair]
