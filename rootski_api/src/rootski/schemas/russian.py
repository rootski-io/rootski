from typing import List, Optional

from pydantic import BaseModel, StrictInt, conint

from rootski.schemas.morpheme import MORPHEME_TYPE_ENUM, MORPHEME_TYPE_NULL


class Meaning(BaseModel):
    meaning: str


class BreakdownItem(BaseModel):
    # id of morpheme in backend database; null if not an actual morpheme
    morpheme_id: Optional[int]
    # morpheme text
    morpheme: str
    # position of morpheme in word
    position: StrictInt
    type: MORPHEME_TYPE_ENUM  # type of morpheme; null if not an actual morpheme
    # family which the morpheme is a member of
    family_id: Optional[StrictInt]
    # description="level 1-6 of how common/difficult the root is; 6 is uncommon and/or difficult",
    level: int = conint(
        gt=0,
        lt=7,
    )
    meanings: List[Meaning]  # descriptions of what the root means
    # comma separated string of other morpheme variants in the family
    family: Optional[str]


class SubDefinition(BaseModel):
    sub_def_id: int  # definition id of the sub definition in the backend database
    sub_def_position: int  # position of the subdefinition with in the whole definition
    definition: str  # body of the definition
    notes: Optional[str]  # extra notes (sometimes in russian) about the subdefinition; often not present


class Definition(BaseModel):
    definition_id: int  # definition id in backend database
    def_position: int  # position of main definition
    sub_defs: List[SubDefinition]


if __name__ == "__main__":
    breakdown_item = BreakdownItem(
        morpheme_id=1,
        morpheme="привет",
        position=0,
        type=MORPHEME_TYPE_NULL,
        family_id=1,
        level=1.1,
        meanings=[Meaning(meaning="hello")],
        # family="привет, приветствие",
    )
    from pprint import pprint

    pprint(breakdown_item.json(exclude_unset=True))
