from rootski.errors import RootskiApiError


class RootskiGraphQLError(RootskiApiError):
    """
    Base exception for any errors manually raised
    in Rootski logic related to GraphQL
    """

    ...
