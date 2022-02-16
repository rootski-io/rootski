from __future__ import annotations

import enum
from textwrap import dedent
from typing import Dict, List

import strawberry
from strawberry import field

from rootski import schemas
from rootski.gql.errors import RootskiGraphQLError


# Unfortunately, strawberry is unable to derive an enum from
# :obj:`WORD_POS_ENUM`. Therefore, we have to keep this class
# up to date with that enum type as it evolves.
@strawberry.enum(name="WordPOS")
class WordPOSEnum(enum.Enum):
    """Word Part of Speech"""

    noun = enum.auto()
    verb = enum.auto()
    particle = enum.auto()
    adjective = enum.auto()
    preposition = enum.auto()
    participle = enum.auto()
    adverb = enum.auto()
    conjunction = enum.auto()
    interjection = enum.auto()
    pronoun = enum.auto()

    @staticmethod
    def from_string(pos: schemas.WORD_POS_ENUM) -> WordPOSEnum:
        """
        Derive the appropriate pos enum from a string.

        :raise RootskiGraphQLError: if the lowercased given ``pos`` does
            not match any of the enum value names
        """
        pos = pos.lower()
        str_to_enum: Dict[str, WordPOSEnum] = {e.name.lower(): e for e in WordPOSEnum}

        valid_pos_strings: List[str] = list(str_to_enum.keys())
        if pos not in valid_pos_strings:
            raise RootskiGraphQLError(
                f'"{pos}" is not a valid part of speech.'
                + f" Only the following values are valid: {valid_pos_strings}"
            )

        return str_to_enum[pos]


@strawberry.type
class Word:
    id: str
    word: str = field(
        description=dedent(
            """
        A russian word in the Cyrillic alphabet with no accent marks.
        These include both capitalized and uncapitalized letters.

        Example: приказать
    """
        )
    )
    accent: str = field(
        description=dedent(
            """
        Same as 'word' except that a single quote (') is placed directly

        Example: приказа'ть

        Note that the cyrillic letter "е" will sometimes be accented as
        "ё" (pronounced "yo"), but can also be accented as "е'"
        (pronounced "ye"). The "ё" spelling may occur in the 'word' field
        as well. This field specifically deals with adding "'" marks
        in the correct places.
    """
        )
    )
    pos: WordPOSEnum = field(
        description=dedent(
            """
        The "part of speech" of the word, i.e. 'noun', 'verb', 'preposition',
        'particle', 'participle', 'adverb', 'conjunction', 'interjection',
        'pronoun', or 'adjective'
    """
        )
    )
    frequency: int = field(
        description=dedent(
            """
        Frequency ranking of the word. For example 'и' (and) has a
        frequency rank of 1 because it is the most used Russian word.
        2 would be the second most used russian word.
    """
        )
    )
    # breakdowns: List[Breakdown]

    @classmethod
    def from_data(cls, data: schemas.Word) -> Word:
        return Word(
            id=data.id,
            word=data.word,
            accent=data.accent,
            pos=WordPOSEnum.from_string(data.pos),
            frequency=data.frequency,
        )
