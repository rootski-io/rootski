import pytest

from rootski.errors import BadBreakdownItemError
from rootski.schemas import MORPHEME_TYPE_ROOT, BreakdownItem
from rootski.schemas.morpheme import MORPHEME_WORD_POS_NOUN


def test__breakdown_item__insufficient_data():
    with pytest.raises(BadBreakdownItemError):
        BreakdownItem(position=0, morpheme_id=1, morpheme="dobby")


def test__breakdown_item__bad_morpheme_word_pos():
    with pytest.raises(BadBreakdownItemError):
        # word_pos will remain unset because "dobby-word-pos" is not a MorphemeWordPOS value
        BreakdownItem(
            position=0,
            morpheme_id=1,
            morpheme="dobby",
            word_pos="dobby-word-pos",
            family_id=1,
            family_meanings=["a house elf", "a free elf"],
            level=1,
            family="dobbus minimus",
            type=MORPHEME_TYPE_ROOT,
        )


def test__breakdown_item__success():
    # pydantic does some validation when creating this "model"; this tests that
    # we can instantiate a BreakdownItem successfully with typical data
    BreakdownItem(
        position=0,
        morpheme_id=1,
        morpheme="dobby",
        word_pos=MORPHEME_WORD_POS_NOUN,
        family_id=1,
        family_meanings=["a house elf", "a free elf"],
        level=1,
        family="dobby,dobbus minimus,dobbinator",
        type=MORPHEME_TYPE_ROOT,
    )
