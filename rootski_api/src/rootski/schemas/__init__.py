"""
Schemas are schemas used in requests/responses.

These are distinct from database models which represent
data as it is stored in the database.
"""
from .breakdown import (
    Breakdown,
    BreakdownInDB,
    BreakdownItem,
    BreakdownItemInDb,
    BreakdownUpsert,
    GetBreakdownResponse,
    MorphemeBreakdownItemInRequest,
    MorphemeBreakdownItemInResponse,
    NullMorphemeBreakdownItem,
    SubmitBreakdownResponse,
)
from .core import Services
from .morpheme import (
    MORPHEME_TYPE_ENUM,
    MORPHEME_TYPE_LINK,
    MORPHEME_TYPE_PREFIX,
    MORPHEME_TYPE_ROOT,
    MORPHEME_TYPE_SUFFIX,
    MORPHEME_WORD_POS_ADJECTIVE,
    MORPHEME_WORD_POS_ANY,
    MORPHEME_WORD_POS_ENUM,
    MORPHEME_WORD_POS_NOUN,
    MORPHEME_WORD_POS_VALUES,
    MORPHEME_WORD_POS_VERB,
    CompleteMorpheme,
    Morpheme,
    MorphemeFamily,
    MorphemeFamilyInDb,
    MorphemeFamilyMeaning,
    MorphemeInDb,
)
from .user import User, UserInDB
from .word import (
    WORD_POS_ENUM,
    AdjectiveResponse,
    AdjectiveShortForms,
    Definition,
    DefinitionForPOS,
    ExampleSentence,
    NounDeclensions,
    NounResponse,
    SubDefinition,
    VerbAspectualPair,
    VerbConjugations,
    VerbResponse,
    Word,
    WordInDb,
    WordResponse,
)

__all__ = [
    # breakdown
    "BreakdownInDB",
    "Breakdown",
    "BreakdownItem",
    "BreakdownItemInDb",
    "BreakdownUpsert",
    "GetBreakdownResponse",
    "MorphemeBreakdownItemInRequest",
    "MorphemeBreakdownItemInResponse",
    "NullMorphemeBreakdownItem",
    "SubmitBreakdownResponse",
    # morpheme
    "CompleteMorpheme",
    "Morpheme",
    "MorphemeFamily",
    "MorphemeFamilyInDb",
    "MorphemeFamilyMeaning",
    "MorphemeInDb",
    # user
    "User",
    "UserInDB",
    # word
    "WORD_POS_ENUM",
    "Word",
    "WordInDb",
    "SubDefinition",
    "Definition",
    "DefinitionForPOS",
    "ExampleSentence",
    "WordResponse",
    "NounDeclensions",
    "NounResponse",
    "AdjectiveShortForms",
    "AdjectiveResponse",
    "VerbConjugations",
    "VerbAspectualPair",
    "VerbResponse",
    # core
    "Services",
    # morpheme types
    "MORPHEME_TYPE_PREFIX",
    "MORPHEME_TYPE_ROOT",
    "MORPHEME_TYPE_SUFFIX",
    "MORPHEME_TYPE_LINK",
    "MORPHEME_TYPE_ENUM",
    # word pos for morphemes
    "MORPHEME_WORD_POS_ANY",
    "MORPHEME_WORD_POS_ADJECTIVE",
    "MORPHEME_WORD_POS_NOUN",
    "MORPHEME_WORD_POS_VERB",
    "MORPHEME_WORD_POS_ENUM",
    "MORPHEME_WORD_POS_VALUES",
]
