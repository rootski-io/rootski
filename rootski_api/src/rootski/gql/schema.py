from strawberry import Schema
from strawberry.tools import merge_types

from rootski.gql.language.word.resolvers import WordQuery

Query = merge_types(name="Root", types=(WordQuery,))

SCHEMA = Schema(query=Query)
