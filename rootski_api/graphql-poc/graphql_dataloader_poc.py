from __future__ import annotations

import asyncio
from asyncio import Future
from typing import List
import strawberry
from strawberry.dataloader import DataLoader
from strawberry.types import Info

from pydantic import BaseModel
from strawberry.types.execution import ExecutionResult
from dataclasses import dataclass

from rich import print
from rich import traceback

traceback.install()


#################
# --- Types --- #
#################


class BookData(BaseModel):
    """Book as it is represented in the data store. Not database specific."""

    id: str
    name: str


class TagData(BaseModel):
    """Tag as it is represented in the data store. Not database specific."""

    id: str
    label: str


class BookTagAssociation(BaseModel):
    """
    define a named tuple for an "association table" that relates books to tags;
    note that this file is trying to database agnostic. Association tables
    are mainly a SQL concept. We won't end up creating an analagous strawberry
    type for this table, so this won't show up directly in strawberry objects--
    only in dataloaders
    """

    book_id: str
    tag_id: str


@dataclass
class GraphQLContext:
    """Global values that are accessible in all resolvers."""

    tag_loader: DataLoader[str, TagData]
    book_ids_for_tag_loader: DataLoader[str, List[str]]
    book_loader: DataLoader[str, BookData]
    tag_ids_for_book_loader: DataLoader[str, List[str]]


#########################################
# --- Totally Realistic Database 🤣 --- #
#########################################


# it's good to have these IDs (the keys) be strings because GraphQL usually thinks
# of IDs as strings. I believe the reason for this is because UUIDs are often the ID
# style of choice for GraphQL. One purpose of GraphQL is to be able to query and join
# data from multiple sources--including multiple databases. If you have two databases
# that need to cooperate with each other, it's helpful to have IDs be UUIDs. The title
# of this article is a bit strong, but it covers the main reasons for UUIDs in the db world:
# https://www.clever-cloud.com/blog/engineering/2015/05/20/Why-Auto-Increment-Is-A-Terrible-Idea/
BOOK_DATA = {
    "1": BookData(
        **{
            "id": "1",
            "name": "Pride and Prejudice",
        }
    ),
    "2": BookData(
        **{
            "id": "2",
            "name": "Lord of the Rings",
        }
    ),
    "3": BookData(
        **{
            "id": "3",
            "name": "Of Mice and Men",
        }
    ),
}

TAG_DATA = {
    "1": TagData(
        **{
            "id": "1",
            "label": "Romance",
        }
    ),
    "2": TagData(
        **{
            "id": "2",
            "label": "Fantasy",
        }
    ),
    "3": TagData(
        **{
            "id": "3",
            "label": "British",
        }
    ),
    "4": TagData(
        **{
            "id": "4",
            "label": "American",
        }
    ),
}

# if you think about it, an association table facilitates a bi-directional graph 🤔
BOOK_TAG_ASSOCIATIONS = [
    BookTagAssociation(book_id="1", tag_id="1"),
    BookTagAssociation(book_id="1", tag_id="2"),
    BookTagAssociation(book_id="2", tag_id="3"),
    BookTagAssociation(book_id="2", tag_id="4"),
    BookTagAssociation(book_id="3", tag_id="4"),
]


########################
# --- Data Loaders --- #
########################

# TODO if at least one ID doesn't exist when loading a batch,
# how should we handle this? Is that an appropriate time to return an error object?
# In that case, do we need to set up a union-type (the GraphQL concept)?


async def load_books(ids: List[str]) -> List[BookData]:
    print(f"Loading books: {ids}")
    books: List[BookData] = [BOOK_DATA[book_id] for book_id in ids]
    return books


async def load_tag_ids_for_book(ids: List[str]) -> List[List[str]]:
    print("Loading tag ids for books", ids)
    tag_id_groups = []
    for book_id in ids:
        tag_ids = [assoc.tag_id for assoc in BOOK_TAG_ASSOCIATIONS if assoc.book_id == book_id]
        tag_id_groups.append(tag_ids)
    return tag_id_groups


async def load_tags(ids: List[str]) -> List[TagData]:
    print("Loading tags:", ids)
    tags: List[TagData] = [TAG_DATA[tag_id] for tag_id in ids]
    return tags


async def load_book_ids_for_tag(ids: List[str]) -> List[List[str]]:
    print("Loading book ids for tags", ids)
    book_id_groups = []
    for tag_id in ids:
        book_ids = [assoc.book_id for assoc in BOOK_TAG_ASSOCIATIONS if assoc.tag_id == tag_id]
        book_id_groups.append(book_ids)
    return book_id_groups


####################################
# --- Strawberry GraphQL Types --- #
####################################

# Naming the strawberry classes "<type>Type" frees up the non-suffixed name ("<type>")
# for other models. However, normally this problem is solved by putting:
#
# pydantic models in a schemas module (namespace) -- schemas.Tag
# orm/odm/ogm models in a orm/odm/ogm module (namespace) -- orm.Tag
# strawberry models in a graphql module (namespace) -- gql.Tag
#
# I prefer that approach because it makes it easier to see which model you're
# using in a given file without having to scroll up to the imports. Saves time!
#
# Having pydantic models could be useful for making abstract data loaders.
# It looks like there are reasons you don't want to have a dataloader return
# a strawberry object directly (I could be wrong on that), but if dataloaders
# return pydantic models AKA *not* orm/odm/ogm models, then our data access is
# abstracted away which means we can freely interchange/mix databases simply by
# swapping out individual dataloaders. Very cool!
#
# So many models... so little time! 🤣
@strawberry.type(name="Tag")
class TagType:
    id: str
    label: str

    @strawberry.field
    async def books(self, info: Info) -> List[BookType]:
        """Load each of the books belonging to this tag."""
        ctx: GraphQLContext = info.context
        book_ids: List[str] = await ctx.book_ids_for_tag_loader.load(self.id)
        future_book_datas: List[Future[BookData]] = [ctx.book_loader.load(_id) for _id in book_ids]
        book_datas: List[BookData] = await asyncio.gather(*future_book_datas)
        books: List[BookType] = [BookType.from_data(data) for data in book_datas]
        return books

    @classmethod
    def from_data(cls, data: TagData):
        """
        Construct a Tag populating only fields that do not need to be fetched.

        This initialization will trigger any resolvers to execute that have
        complex functions. TODO: is this statement correct?
        """
        return TagType(id=data.id, label=data.label)


@strawberry.type(name="Book")
class BookType:
    id: str
    name: str

    @strawberry.field
    async def tags(self, info: Info) -> List[TagType]:
        ctx: GraphQLContext = info.context
        tag_ids: List[str] = await ctx.tag_ids_for_book_loader.load(self.id)
        future_tag_datas: List[Future[TagData]] = [ctx.tag_loader.load(_id) for _id in tag_ids]
        tag_datas: List[TagData] = await asyncio.gather(*future_tag_datas)
        tags: List[TagType] = [TagType.from_data(data) for data in tag_datas]
        return tags

    @classmethod
    def from_data(cls, data: BookData) -> BookType:
        return BookType(
            id=data.id,
            name=data.name,
        )


@strawberry.type
class Query:
    @strawberry.field
    async def get_book(self, info: Info, id: str) -> BookType:
        ctx: GraphQLContext = info.context
        data: BookData = await ctx.book_loader.load(id)
        return BookType.from_data(data)

    @strawberry.field
    async def get_all_books(self, info: Info) -> List[BookType]:
        ctx: GraphQLContext = info.context

        # query all books from the database, fetch all their fields while we're at it
        # fields that require "joins" will be resolved afterwards; NOTE, we can't write
        # a DataLoader for this part because DataLoaders require us to already have the
        # IDs of all the books we want to query. Pagination would also be implemented
        # here. TODO but how would we take care of pagination in subobjects which are?
        # fetched by DataLoaders? NOTE ideally, we'd want this query to be async
        book_datas = [data for _, data in BOOK_DATA.items()]
        books: List[BookType] = [BookType.from_data(data) for data in book_datas]
        return books

    @strawberry.field
    async def get_books(self, info: Info, offset: int, limit: int) -> List[BookType]:
        """
        Fetch a page of books from the data store.

        Typically the 'getAllBooks' resolver would be no different from a 'getBooks'
        resolver like this. Fetching ALL books would simply be the default for 'getBooks'
        (which honestly, would be better named 'books'). However, there are cases when you
        want to *force* the user to paginate because there are MANY records in the data store.
        That would be a further reason not to have two separate resolvers. You would have
        ONE resolver called 'books' or 'getBooks' with required arguments for pagination
        AND enforcement via returning errors.

        TODO this should return a BookConnection object as per the Relay spec.
        This way we can communicate our PageInfo.
        """
        ctx: GraphQLContext = info.context
        book_datas = [data for _, data in BOOK_DATA.items()][offset : offset + limit]
        books: List[BookType] = [BookType.from_data(data) for data in book_datas]

        return books


schema = strawberry.Schema(Query)


################
# --- Main --- #
################


async def main():
    one_book_query = """
        query {
            getBook(id: "1") {
                name
                tags {
                    label
                    books {
                        name
                    }
                }
            }
        }
    """

    all_books_query = """
        query {
            getAllBooks {
                name
                tags {

                    label
                    books {
                        name
                    }
                }
            }
        }
    """

    many_books_query = """
        query {
            getBooks(offset: 0, limit: 2) {
                __typename
                name
                tags {
                    __typename
                    label
                    books {
                        __typename
                        name
                    }
                }
            }
        }
    """

    result: ExecutionResult = await schema.execute(
        all_books_query,
        context_value=GraphQLContext(
            tag_loader=DataLoader(load_fn=load_tags),
            book_ids_for_tag_loader=DataLoader(load_fn=load_book_ids_for_tag),
            book_loader=DataLoader(load_fn=load_books),
            tag_ids_for_book_loader=DataLoader(load_fn=load_tag_ids_for_book),
        ),
    )

    assert not result.errors
    print(result.data)


if __name__ == "__main__":
    asyncio.run(main())
