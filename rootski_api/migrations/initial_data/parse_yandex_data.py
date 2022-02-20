"""
This python file is not meant to work. It is copy/pasted output from a jupyter notebook
that we were experimenting with. There is *some* good code in here that we can
use actually processing our json files that we cached from Yandex.
"""

from rich import print
from pathlib import Path
from typing import List, Literal, Optional
import pandas as pd

from sqlalchemy import create_engine

import json

translations_dir = Path(
    "/Users/eric/repos/extra/rootski/rootski/rootski_api/migrations/initial_data/yandex_data"
)

json_fpaths: List[Path] = list(translations_dir.glob("*.json"))

# json_txt = json_fpaths[0].read_text()
# json_dict: dict = json.loads(json_txt)


def parse_data_from_word_json_file(fpath: Path, delimiter="///", verbose=False) -> Optional[dict]:
    """
    :returns:
        - pos
        - delimeter concatenated english translations
    """
    json_txt = fpath.read_text()
    json_dict: dict = json.loads(json_txt)

    # return if there are no defs
    if len(json_dict["def"]) == 0:
        if verbose:
            print(f"{fpath.name} has no 'def's")
        return None

    # return if the first def has an empty 'tr'
    elif len(json_dict["def"][0]["tr"]) == 0:
        if verbose:
            print(f"{fpath.name} has 'defs', but one or more 'def's have no 'tr's")
        return None

    pos = json_dict["def"][0]["pos"]

    return {
        "pos": pos,
        # "eng": delimiter.join([tr["text"] for tr in json_dict["def"][0]["tr"]])
        "eng": json_dict["def"][0]["tr"][0]["text"],
    }


for i in range(10):
    text: Optional[str] = parse_data_from_word_json_file(json_fpaths[i])
    if text is not None:
        print(text)


words_csv_fpath = "/Users/eric/repos/extra/rootski/rootski/rootski_api/migrations/initial_data/data/words.csv"
df: pd.DataFrame = pd.read_csv(words_csv_fpath)

cached_words = [fpath.name.split(".")[0] for fpath in json_fpaths]

df = df[df.word.isin(cached_words)]


def func(row):
    word: str = row["word"]
    pos: str = row["pos"]


def make_fpath_from_word(word: str):
    return translations_dir / f"{word}.json"


def get_yandex_data_for_word(word: str, field: Literal["pos", "text"]) -> Optional[str]:
    word_yandex_fpath: Path = make_fpath_from_word(word)
    data: Optional[dict] = parse_data_from_word_json_file(word_yandex_fpath)
    return data[field] if data is not None else None


get_yandex_data_for_word("на", field="eng")

df["eng"] = df.word.apply(lambda word: get_yandex_data_for_word(word=word, field="eng"))
df.head()


from sqlalchemy import (
    TIMESTAMP,
    Column,
    DateTime,
    Integer,
    Enum,
    ForeignKey,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base

# Base object which will contain all proto table declarations
Base = declarative_base()

# re-used types
POS_ENUM = Enum(
    "preposition",
    "interjection",
    "participle",
    "particle",
    "adjective",
    "pronoun",
    "verb",
    "noun",
    "conjunction",
    "adverb",
    name="parts_of_speech",
)


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    word = Column(String(256), nullable=False, comment="russian word in cyrillic characters")
    accent = Column(
        String(256),
        nullable=False,
        comment="russian word in cyrillic characters, which may include a ''' or 'ё' on the stressed syllable",
    )
    pos = Column(POS_ENUM, nullable=False, comment="part of speech (noun, adjective, etc.")
    frequency = Column(Integer, nullable=True, comment="frequency rank of the word")
    eng = Column(String(256), nullable=True, comment="english translations of the word used for search")


sqlite_engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(bind=sqlite_engine)

df = df.rename(columns={"type": "pos"})
df.to_sql(con=sqlite_engine, name="words", if_exists="append", index=False)


pd.read_sql(
    """
    SELECT *
    FROM words
    WHERE eng = 'hi'

    UNION ALL

    SELECT *
    FROM words
    WHERE eng LIKE '%hi%'
""",
    con=sqlite_engine,
)
