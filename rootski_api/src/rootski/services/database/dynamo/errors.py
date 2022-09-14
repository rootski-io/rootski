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
USER_NOT_FOUND_MSG = "User with email {email} was not found in Dynamo table named {dynamo_table_name}."
USER_ALREADY_REGISTERED_MSG = 'User with email "{email}" is already registered.'


##################
# --- Errors --- #
##################


class BreakdownNotFoundError(Exception):
    """Error thrown if a Breakdown isn't found."""


class UserBreakdownNotFoundError(Exception):
    """Error thrown if a User Breakdown isn't found."""


class WordNotFoundError(Exception):
    """Error thrown if a word isn't found."""


class MorphemeNotFoundError(Exception):
    """Raised when a morpheme is not found in the database"""


class MorphemeFamilyNotFoundError(Exception):
    """Error thrown if a MorphemeFamily isn't found."""


class UserNotFoundError(Exception):
    """Error thrown if a User isn't found."""


class UserAlreadyRegisteredError(Exception):
    """Error thrown if a User is already registered."""
