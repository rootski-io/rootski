from typing import List

from rootski.errors import RootskiApiError

##########################
# --- Error Messages --- #
##########################

MORPHEME_FAMILY_IDS_NOT_FOUND_MSG = "One of your morpheme family IDs {not_found_ids} was not found in Dynamo."
MORPHEME_IDS_NOT_FOUND_MSG = "One of your morpheme IDs {not_found_ids} was not found in Dynamo."
PARTS_DONT_SUM_TO_WHOLE_WORD_MSG = 'Breakdown "{submitted_breakdown}" does not sum to the word "{word}"'
WORD_ID_NOT_FOUND = "No word with ID {word_id} was found in Dynamo."
BREAKDOWN_NOT_FOUND = "No breakdown for word with ID {word_id} was found in Dynamo."
USER_BREAKDOWN_NOT_FOUND = (
    "No breakdown for word with ID {word_id} and for user {user_email} was found in Dynamo."
)

##################
# --- Errors --- #
##################

# TODO: Add factory methods for each of the errors, and replace the formatted error messages in the code base.


class BreakdownNotFoundError(RootskiApiError):
    """Error thrown if a Breakdown isn't found."""


class UserBreakdownNotFoundError(RootskiApiError):
    """Error thrown if a User Breakdown isn't found."""


class WordNotFoundError(RootskiApiError):
    """Error thrown if a word isn't found."""


class MorphemeNotFoundError(RootskiApiError):
    """Raised when a morpheme is not found in the database"""

    @staticmethod
    def make_error_message(morpheme_ids: List[str]):
        morpheme_ids.sort()
        return MORPHEME_IDS_NOT_FOUND_MSG.format(not_found_ids=morpheme_ids)


class MorphemeFamilyNotFoundError(RootskiApiError):
    """Error thrown if a MorphemeFamily isn't found."""


class BadBreakdownError(RootskiApiError):
    """Raised when a breakdown is malformed or invalid."""


class DuplicateExampleTitle(RootskiApiError):
    """
    Raised when an HTTP route has two documented example responses
    in one HTTP status code with the same title
    """
