import json
from pathlib import Path
from typing import Any, Dict, List, Union

from sqlalchemy.orm import Session

from rootski.schemas.morpheme import CompleteMorpheme
from rootski.services.database import models as orm


def make_morphemes_json(session: Session, morphemes_json_fpath: Union[Path, str]) -> None:
    """Query all morphemes and their adjoining tables from the database at once.

    Cache all of this information in a JSON file on local disk."""

    # query all morphemes from the database, eagerly-loading all joining tables
    morphemes: List[orm.Morpheme] = (
        session.query(orm.Morpheme).join(orm.MorphemeFamily).join(orm.MorphemeFamilyMeaning).all()
    )

    # collect the data from each of the tables into one object
    complete_morphemes: List[CompleteMorpheme] = [CompleteMorpheme.from_orm_morpheme(m) for m in morphemes]

    # create a dictionary containing all of the data for each of the morphemes
    m: CompleteMorpheme

    def morpheme_to_dict(m: CompleteMorpheme) -> Dict[str, Any]:
        """The frontend currently expects the meanings field to be a list of dictionaries."""
        to_return = m.dict()
        to_return["meanings"] = [{"meaning": meaning for meaning in m.meanings}]
        return to_return

    morphemes_json: Dict[int, Dict[str, Union[str, List[str]]]] = {
        m.morpheme_id: morpheme_to_dict(m) for m in complete_morphemes
    }

    # write the dictionary to a json file
    with open(morphemes_json_fpath, "w") as file:
        json.dump(morphemes_json, file)
