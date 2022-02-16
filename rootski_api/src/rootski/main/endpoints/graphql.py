from strawberry.fastapi import GraphQLRouter

from rootski.gql.schema import SCHEMA
from rootski.main.deps import get_graphql_context

router = GraphQLRouter(path="/graphql", schema=SCHEMA, context_getter=get_graphql_context, graphiql=True)
