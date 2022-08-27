from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from loguru import logger
from pydantic import BaseModel, EmailStr, Field, constr, root_validator
from rootski.errors import BadBreakdownItemError
from rootski.schemas.morpheme import MORPHEME_TYPE_ENUM, MORPHEME_WORD_POS_ENUM, Morpheme
from rootski.services.database import models as orm


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

    class Config:
        orm_mode = True

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

    @staticmethod
    def from_orm_breakdown_item(b_item: orm.BreakdownItem):
        # fetch a few fields that are not directly on the SQL tables, but required by the pydantic schema

        # morpheme fields
        morpheme: Optional[orm.Morpheme] = b_item.morpheme_
        if morpheme:
            word_pos: Optional[MORPHEME_WORD_POS_ENUM] = morpheme.word_pos
            family_id: int = morpheme.family_id
            type: str = morpheme.type
            level: int = morpheme.family.level
            family: str = morpheme.family.family

            # family meanings
            orm_meaning: orm.MorphemeFamilyMeaning
            family_meanings: List[str] = [
                orm_meaning.meaning
                for orm_meaning in b_item.morpheme_.family.meanings
                if orm_meaning.meaning is not None
            ]

            # create a BreakdownItem from the BreakdownItemInDb, overwriting any of the fields we just fetched
            b_item_db = BreakdownItemInDb.from_orm(b_item)
            logger.info("Breakdown Item")
            logger.info(b_item_db.dict())
            b_item_kwargs = {
                **b_item_db.dict(),
                **dict(
                    word_pos=word_pos,
                    family_id=family_id,
                    level=level,
                    type=type,
                    family=family,
                    family_meanings=family_meanings,
                ),
            }
            print("b_item_kwargs", b_item_kwargs)
            logger.info(b_item_kwargs)
            return BreakdownItem(**b_item_kwargs)

        else:
            # for null morphemes, we only care about the position and the morpheme text
            to_return = BreakdownItem.from_orm(b_item)
            to_return.morpheme_id = None
            return to_return

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

    class Config:
        orm_mode = True

    def to_orm(self, breakdown_id: Optional[int] = None) -> orm.BreakdownItem:
        """Returns an orm representation of the breakdown item.

        :param breakdown_id:
        """
        return orm.BreakdownItem(
            breakdown_id=breakdown_id,
            morpheme_id=self.morpheme_id,
            position=self.position,
            type=self.type,
            morpheme=self.morpheme,
        )


class BreakdownCommon(BaseModel):
    word_id: int
    word: constr(max_length=256)
    is_verified: bool
    is_inference: bool
    date_submitted: datetime
    date_verified: Optional[datetime]
    breakdown_items: List[BreakdownItemCommon]

    class Config:
        orm_mode = True


class Breakdown(BreakdownCommon):
    breakdown_items: List[BreakdownItem]
    submitted_by_current_user: bool = False

    @staticmethod
    def from_orm_breakdown(orm_breakdown: orm.Breakdown):
        """Initialize a breakdown object from an orm.Breakdown object with the proper intermediate steps."""
        # fetch some data not present in the Breakdown db table, but required by the pydantic schema
        breakdown_common = BreakdownCommon.from_orm(orm_breakdown)
        breakdown_items = [
            BreakdownItem.from_orm_breakdown_item(b_item) for b_item in orm_breakdown.breakdown_items
        ]

        # create a Breakdown schema overwriting the orm_breakdown with the ones we just fetched
        breakdown_kwargs = {**breakdown_common.dict(), **dict(breakdown_items=breakdown_items)}
        print("breakdown kwargs", breakdown_kwargs)
        return Breakdown(**breakdown_kwargs)


class BreakdownInDB(BreakdownCommon):
    submitted_by_user_email: Optional[EmailStr]
    verified_by_user_email: Optional[EmailStr]
    id: Optional[int] = None

    class Config:
        orm_mode = True


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
    breakdown_id: int
    is_verified: bool


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
