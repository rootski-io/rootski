from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, constr, root_validator
from rootski.errors import BadBreakdownItemError
from rootski.schemas.morpheme import MORPHEME_TYPE_ENUM, MORPHEME_WORD_POS_ENUM, Morpheme


class NullMorphemeBreakdownItem(BaseModel):
    """
    Use this type to include a piece of text in a
    breakdown that does not have a morpheme id.
    """

    morpheme: constr(max_length=256)
    position: int

    # these values should always be none
    morpheme_id: None = None

    @staticmethod
    def from_morpheme(morpheme: Morpheme, position: int):
        return NullMorphemeBreakdownItem(morpheme=morpheme.morpheme, position=position)


class MorphemeBreakdownItemInRequest(BaseModel):
    morpheme_id: int
    position: int


class MorphemeBreakdownItemInResponse(MorphemeBreakdownItemInRequest):
    """
    Use this type to include the morpheme associated with
    the given morpheme_id in the breakdown.

    Each of these fields are in BreakdownItem
    """

    # these fields are not necessary in the request body but should be present otherwise
    type: Optional[MORPHEME_TYPE_ENUM]
    word_pos: Optional[MORPHEME_WORD_POS_ENUM]
    morpheme: Optional[str]
    family_id: Optional[int]
    family_meanings: Optional[List[str]]
    level: Optional[int]
    family: Optional[str]

    class Config:
        use_enum_values = True

    @staticmethod
    def from_morpheme(morpheme: Morpheme, position: int):
        return MorphemeBreakdownItemInResponse(
            morpheme_id=morpheme.morpheme_id,
            position=position,
            word_pos=morpheme.word_pos,
            family_id=morpheme.family_id,
            type=morpheme.type,
        )


class BreakdownItemCommon(BaseModel):
    morpheme: Optional[
        constr(
            max_length=256,
        )
    ]
    position: int
    family_id: Optional[int]
    family_meanings: Optional[List[str]]
    morpheme_id: Optional[int]
    type: Optional[MORPHEME_TYPE_ENUM]

    @staticmethod
    def from_null_morpheme_breakdown_item(item: NullMorphemeBreakdownItem):
        return BreakdownItem(type=None, morpheme=item.morpheme, position=item.position)

    @staticmethod
    def from_morpheme_breakdown_item(item: MorphemeBreakdownItemInResponse):
        return BreakdownItem(position=item.position, **MorphemeBreakdownItemInResponse.dict())

    @staticmethod
    def from_morpheme(morpheme: Morpheme, position: int):
        """
        If ``type`` is ``None``, this is a "null" morpheme. It is not a morpheme, but we
        need to store the text.

        Otherwise, this is a real morpheme. In this case, we only need the ``morpheme_id``.
        The rest of the morpheme attributes can be looked up in the database.

        In both cases, the morpheme position is required.
        """
        if not morpheme.type:
            return BreakdownItem(
                position=position,
                morpheme=morpheme.morpheme,
                morpheme_id=morpheme.morpheme_id,
            )
        else:
            return BreakdownItem(position=position, morpheme_id=morpheme.morpheme_id)


class BreakdownItem(BreakdownItemCommon):
    """Contains attributes that are not in BreakdownItemInDb"""

    word_pos: Optional[MORPHEME_WORD_POS_ENUM]
    level: Optional[int]  # level of difficulty
    family: Optional[str]  # string of the actual family corresponding to the family id

    @root_validator
    def enforce_non_null_morpheme_data_is_set(cls, values: Dict[str, Any]):
        """If the morpheme ID is set, this is a non-null morpheme breakdown item."""
        if values.get("morpheme_id") is not None:
            required_morpheme_non_null_b_item_fields = ["word_pos", "family_id", "type", "level"]
            for field in required_morpheme_non_null_b_item_fields:
                if values.get(field) is None:
                    raise BadBreakdownItemError(
                        f'Field "{field}" is not set in non-null morpheme breakdown item.'
                    )
            required_nullable_fields = ["family_meanings"]
            for field in required_nullable_fields:
                if field not in values.keys():
                    raise BadBreakdownItemError(
                        f'Field "{field}" is unset. Is can be None, but it must be explicitly set to None.'
                    )
        return values

    def to_null_or_morpheme_breakdown_item(
        self,
    ) -> Union[NullMorphemeBreakdownItem, MorphemeBreakdownItemInResponse]:
        """Cast this BreakdownItem to the correct sub-type. This is useful for creating an API response."""
        if self.morpheme_id is not None:
            return MorphemeBreakdownItemInResponse(**self.dict())
        else:
            return NullMorphemeBreakdownItem(**self.dict())


class BreakdownItemInDb(BreakdownItemCommon):
    # If this is a null_breakdown, expect breakdown_id to be none.
    # formerly, breakdown_id: Optional[int] = None, when using SQLAlchemy
    breakdown_id: str = "deprecated"



class BreakdownCommon(BaseModel):
    word_id: int
    word: constr(max_length=256)
    is_verified: bool
    is_inference: bool
    date_submitted: datetime
    date_verified: Optional[datetime]
    breakdown_items: List[BreakdownItemCommon]



class Breakdown(BreakdownCommon):
    breakdown_items: List[BreakdownItem]
    submitted_by_current_user: bool = False



class BreakdownInDB(BreakdownCommon):
    submitted_by_user_email: Optional[EmailStr]
    verified_by_user_email: Optional[EmailStr]
    id: Optional[int] = None


##################################
# --- HTTP Request/Responses --- #
##################################


class GetBreakdownResponse(Breakdown):
    # all fields should be the same as Breakdown, but the datatypes of
    # breakdown_items should be more specific
    breakdown_items: List[Union[NullMorphemeBreakdownItem, MorphemeBreakdownItemInResponse]]

    @staticmethod
    def from_breakdown(breakdown: Breakdown):
        breakdown_items: List[Union[NullMorphemeBreakdownItem, MorphemeBreakdownItemInResponse]] = [
            b_item.to_null_or_morpheme_breakdown_item() for b_item in breakdown.breakdown_items
        ]
        to_return = GetBreakdownResponse(**breakdown.dict())
        to_return.breakdown_items = breakdown_items
        return to_return


class BreakdownUpsert(BaseModel):
    word_id: int = Field(description="ID of the word the breakdown is for.")
    breakdown_items: List[Union[NullMorphemeBreakdownItem, MorphemeBreakdownItemInRequest]]


class SubmitBreakdownResponse(BaseModel):
    word_id: int
    is_verified: bool
    breakdown_id: int = Field(-1, description="Always `-1` since this field is deprecated.")


############################
# --- Helper functions --- #
############################

# This is used to create request payloads in unit tests
def make_specific_breakdown_item(
    morpheme: Morpheme, position: int
) -> Union[NullMorphemeBreakdownItem, MorphemeBreakdownItemInResponse]:
    if not morpheme.morpheme_id:
        return NullMorphemeBreakdownItem.from_morpheme(morpheme=morpheme, position=position)
    else:
        return MorphemeBreakdownItemInResponse.from_morpheme(morpheme=morpheme, position=position)
