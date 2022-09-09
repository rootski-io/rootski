from rootski.errors import RootskiApiError

##########################
# --- Error Messages --- #
##########################

MORPHEME_IDS_NOT_FOUND_MSG = "Could not find morphemes with the following ids: {not_found_ids}"
PARTS_DONT_SUM_TO_WHOLE_WORD_MSG = 'Breakdown "{submitted_breakdown}" does not sum to the word "{word}"'
WORD_ID_NOT_FOUND = "No word with id {word_id} exists."
BREAKDOWN_NOT_FOUND = "No breakdown for word with ID {word_id} exists."
VERIFIED_BREAKDOWN_EXISTS = "A verified breakdown for word with ID {word_id} already exists."

##################
# --- Errors --- #
##################


class WordNotFoundError(RootskiApiError):
    """Error thrown if a word isn't found."""


class MorphemeNotFoundError(RootskiApiError):
    """Raised when a morpheme is not found in the database"""


class BadBreakdownError(RootskiApiError):
    """Raised when a breakdown is malformed or invalid."""


class DuplicateExampleTitle(RootskiApiError):
    """
    Raised when an HTTP route has two documented example responses
    in one HTTP status code with the same title
    """
