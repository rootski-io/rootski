from typing import List, Literal

from pydantic import BaseModel


class SearchWord(BaseModel):
    word: str
    word_id: str
    frequency: int
    pos: Literal["deprecated"]


class SearchResponse(BaseModel):
    words: List[SearchWord]
