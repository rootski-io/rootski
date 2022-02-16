from __future__ import annotations

import asyncio
import enum
import json
from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop, Future
from base64 import b64decode, b64encode
from dataclasses import dataclass
from enum import Enum
from typing import (
    Generic,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import strawberry
from pydantic import BaseModel, conint, root_validator
from rich import print, traceback
from strawberry.dataloader import DataLoader
from strawberry.types import Info
from strawberry.types.execution import ExecutionResult

traceback.install(show_locals=True)

############################
# --- Helper Functions --- #
############################

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")


def add_kv_to_dataloader_cache(loader: DataLoader[TKey, TValue], key: TKey, value: TValue) -> None:
    """
    Manually add a key-value pair to a :class:`DataLoader` cache.

    This is useful for reducing hits to a backend data store that is
    hit by the DataLoader in question. For example, if we want to query
    a database for a "page" of records, we will not know the IDs of those
    records in advance. Since DataLoaders are (usually) used to fetch
    records by ID, we cannot use DataLoaders to fetch pages.

    Therefore, the query for these objects must be done outside of the
    DataLoader. However, once we've queried a page of records (not using
    the DataLoader), we will want to make the DataLoader aware of our
    fetched objects so that we will not needlessly fetch the same objects
    again. This function can be used to accomplish that.

    :param loader: The DataLoader whose cache will have the key-value pair added to
    :param key: The same type of key used in a call to ``DataLoader.load_fn(key)``
    :param value: The value that ``DataLoader.load_fn(key)`` should return.
        This should not be an Awaitable or a :class:`Future`, but the actual value
        that would be the result of the ``Future`` after being awaited.
    """
    loop: AbstractEventLoop = loader.loop
    future_value: Future = loop.create_future()
    future_value.set_result(value)
    loader.cache_map[key] = future_value


####################################
# --- Strawberry GraphQL Types --- #
####################################


@dataclass
class GraphQLContext:
    """Global values that are accessible in all resolvers."""

    genre_loader: DataLoader[str, GenreData]
    book_ids_for_genre_loader: DataLoader[str, List[str]]
    book_loader: DataLoader[str, BookData]
    genre_ids_for_book_loader: DataLoader[str, List[str]]


# Naming the strawberry classes "<type>Type" frees up the non-suffixed name ("<type>")
# for other models. However, normally this problem is solved by putting:
#
# pydantic models in a schemas module (namespace) -- schemas.Genre
# orm/odm/ogm models in a orm/odm/ogm module (namespace) -- orm.Genre
# strawberry models in a graphql module (namespace) -- gql.Genre
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
@strawberry.type(name="Genre")
class GenreType:
    id: str
    genre: str
    reading_level: str

    @strawberry.field
    async def books(self, info: Info, first: int = None, last: int = None, after: str = None) -> List[BookType]:
        """Load each of the books belonging to this Genre."""
        ctx: GraphQLContext = info.context
        book_ids: List[str] = await ctx.book_ids_for_genre_loader.load(self.id)
        future_book_datas: List[Future[BookData]] = [ctx.book_loader.load(_id) for _id in book_ids]
        book_datas: List[BookData] = await asyncio.gather(*future_book_datas)
        books: List[BookType] = [BookType.from_data(data) for data in book_datas]
        return books

    @classmethod
    def from_data(cls, data: GenreData):
        """
        Construct a Genre populating only fields that do not need to be fetched.

        This initialization will trigger any resolvers to execute that have
        complex functions. TODO: is this statement correct?
        """
        return GenreType(
            id=data.id,
            genre=data.genre,
            reading_level=data.reading_level,
        )


@strawberry.type(name="Book")
class BookType:
    id: str
    name: str
    rating: float

    @strawberry.field
    async def genres(self, info: Info) -> List[GenreType]:
        ctx: GraphQLContext = info.context
        genre_ids: List[str] = await ctx.genre_ids_for_book_loader.load(self.id)
        future_genre_datas: List[Future[GenreData]] = [ctx.genre_loader.load(_id) for _id in genre_ids]
        genre_datas: List[GenreData] = await asyncio.gather(*future_genre_datas)
        genres: List[GenreType] = [GenreType.from_data(data) for data in genre_datas]
        return genres

    @classmethod
    def from_data(cls, data: BookData) -> BookType:
        return BookType(
            id=data.id,
            name=data.name,
            rating=data.rating,
        )


############################
# --- Data Store Types --- #
############################


class BookData(BaseModel):
    """Book as it is represented in the data store. Not database specific."""

    id: str
    name: str
    rating: float


GENRE_ENUM = Literal["HISTORY", "MATH", "SCIENCE", "FICTION"]


class GenreData(BaseModel):
    """Genre as it is represented in the data store. Not database specific."""

    id: str
    genre: GENRE_ENUM
    reading_level: str


class BookGenreAssociation(BaseModel):
    """
    define a named tuple for an "association table" that relates books to genres;
    note that this file is trying to database agnostic. Association tables
    are mainly a SQL concept. We won't end up creating an analagous strawberry
    type for this table, so this won't show up directly in strawberry objects--
    only in dataloaders
    """

    book_id: str
    genre_id: str


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
            "rating": 5.5,
        }
    ),
    "2": BookData(
        **{
            "id": "2",
            "name": "Lord of the Rings",
            "rating": 6.5,
        }
    ),
    "3": BookData(
        **{
            "id": "3",
            "name": "Of Mice and Men",
            "rating": 8.8,
        }
    ),
}

GENRE_DATA = {
    "1": GenreData(**{"id": "1", "genre": "HISTORY", "reading_level": "children"}),
    "2": GenreData(**{"id": "2", "genre": "HISTORY", "reading_level": "young adult"}),
    "3": GenreData(**{"id": "3", "genre": "HISTORY", "reading_level": "mature"}),
    "4": GenreData(**{"id": "4", "genre": "MATH", "reading_level": "children"}),
    "5": GenreData(
        **{
            "id": "5",
            "genre": "MATH",
            "reading_level": "teen",
        }
    ),
    "6": GenreData(
        **{
            "id": "6",
            "genre": "FICTION",
            "reading_level": "young adult",
        }
    ),
    "7": GenreData(
        **{
            "id": "7",
            "genre": "SCIENCE",
            "reading_level": "young adult",
        }
    ),
}

# if you think about it, an association table facilitates a many-to-many, bi-directional graph 🤔
BOOK_TAG_ASSOCIATIONS = [
    BookGenreAssociation(book_id="1", genre_id="1"),
    BookGenreAssociation(book_id="1", genre_id="2"),
    BookGenreAssociation(book_id="2", genre_id="3"),
    BookGenreAssociation(book_id="2", genre_id="4"),
    BookGenreAssociation(book_id="3", genre_id="4"),
]

#################################
# --- Data Loader Functions --- #
#################################

# TODO if at least one ID doesn't exist when loading a batch,
# how should we handle this? Is that an appropriate time to return an error object?
# In that case, do we need to set up a union-type (the GraphQL concept)?


async def load_books(ids: List[str]) -> List[BookData]:
    print(f"Loading books: {ids}")
    books: List[BookData] = [BOOK_DATA[book_id] for book_id in ids]
    return books


async def load_genre_ids_for_book(ids: List[str]) -> List[List[str]]:
    print("Loading Genre ids for books", ids)
    genre_id_groups = []
    for book_id in ids:
        genre_ids = [assoc.genre_id for assoc in BOOK_TAG_ASSOCIATIONS if assoc.book_id == book_id]
        genre_id_groups.append(genre_ids)
    return genre_id_groups


async def load_genres(ids: List[str]) -> List[GenreData]:
    print("Loading genres:", ids)
    genres: List[GenreData] = [GENRE_DATA[genre_id] for genre_id in ids]
    return genres


async def load_book_ids_for_genre(ids: List[str]) -> List[List[str]]:
    print("Loading book ids for genres", ids)
    book_id_groups = []
    for genre_id in ids:
        book_ids = [assoc.book_id for assoc in BOOK_TAG_ASSOCIATIONS if assoc.genre_id == genre_id]
        book_id_groups.append(book_ids)
    return book_id_groups


################################
# --- Page Query Functions --- #
################################


def base64encode(string: str) -> str:
    """
    Return a base64 encoded version of a ``string``.

    >>> base64encode("hi")
    'aGk='

    Base 64 encoded strings make great cursors 😉
    """
    return b64encode(string.encode()).decode()


def base64decode(string: str) -> str:
    return b64decode(string).decode()


class Cursor(BaseModel, ABC):
    """
    A cursor contains information about a *single record* in a data store
    AND information about the query that was used to get that record. This
    information is used to re-run *almost* the same query, but fetch more
    records immediately before or after the record in the cursor.

    For example, say we made a SQL query to load a "page" of Book records:

    .. code-block:: sql

        SELECT *
        FROM books
        WHERE books.title LIKE '%Potter%' -- you know? for the Harry Potter books?
        ORDER BY
            books.release_date ASC,
            books.title DESC -- order books by title in reverse alphabetical order
        OFFSET 0 -- here, offset and limit get us the first 3 books in this result set
        LIMIT 3

    This query would sort all of the Harry Potter books in ascending order of
    their release date and break any ties (you know, like if two HP books had
    the exact same release date down to the day!) by sorting them in reverse
    alphabetical order by title. Of this result set, it would return the first 3
    books (a "page" of 3 books).

    If we wanted to get the next page of 3 books, we would need to sort all of
    the Harry Potter books in *exactly* the same esoteric way, and then get
    OFFSET 3 LIMIT 3. So... the client requesting the books from this API
    needs to communicate to this API the same sort order when it's asking for
    the next page. Therefore, the client somehow needs to tell the API
    what all the WHERE clauses and ORDER BY clauses are for a given page.

    Rather than expose ``where`` or ``orderBy`` arguments in the GraphQL ``getBooks()``
    query, we will have the client pass a single string that encodes enough information
    for us to build such a SQL query on the backend. Of course, we aren't forced to
    use SQL on the backend. We can use any data store.

    For *every* record in the result set, we will create a "cursor" string that encodes
    (1) exactly which sort and filter options were used to make the result set and
    (2) which number in the result set this record is so that we can query more records
    before or after that, i.e. previous and subsequent pages :D

    Note that SQL queries using ``OFFSET`` and ``LIMIT`` for pagination get slower and
    slower the higher you make your ``OFFSET``. The reason is that the SQL database must
    find and order at *least* ``OFFSET + LIMIT`` records before it can return the last
    ``LIMIT`` of them back to us. "Keyset pagination" is an alternative that is trickier
    trickier to implement, but has the same performance no matter how high the page number
    is that is being queried for.
    """

    def to_cursor(self) -> str:
        """Encode data about a cursor in a string."""
        model_dict: dict = self.dict()
        model_json: str = json.dumps(model_dict)
        return model_json

    @classmethod
    def from_cursor(cls: Type[Cursor], cursor: str) -> Cursor:
        """Decode data about a cursor from a previously encoded cursor string."""
        cursor_dict = json.loads(cursor)
        model: Cursor = cls(**cursor_dict)
        return model

    @classmethod
    @abstractmethod
    def from_model(cls: Type[Cursor], model: Type[BaseModel], **kwargs) -> Cursor:
        """Take a *Data pydantic representation of a model in the database and make it into a cursor."""
        ...


class GenreCursor(Cursor):
    genre_filter: Optional[GENRE_ENUM]
    genre_id: str

    @classmethod
    def from_model(cls: Type[GenreCursor], model: GenreData, genre_filter: Optional[GENRE_ENUM]) -> GenreCursor:
        return GenreCursor(
            genre_id=model.id,
            genre_filter=genre_filter.name if genre_filter else None,
        )


class BookCursor(Cursor):
    title_contains: Optional[str]
    book_id: str

    @classmethod
    def from_model(cls: Type[BookCursor], model: BookData, title_contains: Optional[str]) -> GenreCursor:
        raise NotImplementedError("todo")
        # return GenreCursor(
        #     genre_id=model.id,
        #     genre_filter=genre_filter,
        # )


############################
# --- Pagination Types --- #
############################


class PaginationError(Exception):
    """
    A custom exception to raise for any reason related to pagination.

    .. note::

        Raising a custom exception rather than :class:`pydantic.ValidationError`
        in ``@validator`` and ``@root_validator`` ``pydantic`` validators
        makes it easier to see your custom error messages when you raise exceptions.
    """

    ...


@strawberry.enum
class GenreEnum(Enum):
    HISTORY = enum.auto()
    FICTION = enum.auto()
    SCIENCE = enum.auto()
    MATH = enum.auto()


class PageInputSchema(BaseModel):
    """Pydantic schema that performs validation on the 4 standard pagination inputs."""

    first: Optional[conint(ge=1, le=10)] = None
    last: Optional[conint(ge=1, le=10)] = None
    before: Optional[str] = None
    after: Optional[str] = None

    @root_validator()
    def validate_combinations_of_attrs(cls: Type[PageInputSchema], v: dict) -> dict:
        """Ensure"""
        if v.get("first") and v.get("last"):
            raise PaginationError("'first' and 'last' cannot be set together.")
        if v.get("before") and v.get("after"):
            raise PaginationError("'before' and 'after' cannot be set together.")
        return v


class GenrePageInputSchema(PageInputSchema):
    genre: Optional[GenreEnum] = None

    @root_validator()
    def validate_genre_attr_with_others(cls: Type[GenrePageInputSchema], v: dict) -> dict:
        if (v.get("before") or v.get("after")) and v.get("genre"):
            raise PaginationError(
                "filters and sorts such as 'genre' cannot be set if 'before' or 'after' are set"
                + " because 'before' and 'after' come with their own set of filters and sorts."
            )
        return v


# BUG - GenrePageInput does not throw any pydantic validations errors :(
# This is because @strawberry.experimental.pydantic.input() converts
# a pydantic type to a strawberry type--which of course does not support
# pydantic validation rules. The workaround is we can convert this input
# to the pydantic type manually after it is received when parsing the GraphQL query
@strawberry.experimental.pydantic.input(
    model=GenrePageInputSchema,
    fields=["first", "last", "before", "after", "genre"],
    name="GenrePageInput",
)
class GenrePageInput:
    """Conversion of Pydantic :class:`PageInputSchema` to a strawberry GraphQL type."""

    ...


@strawberry.type
class PageInfo:
    start_cursor: str = strawberry.field(
        description="Cursor of first edge in page; is used in a 'before' or 'after' pagination query."
    )
    end_cursor: str = strawberry.field(
        description="Cursor of last edge in page; is used in a 'before' or 'after' pagination query."
    )
    has_previous_page: bool = strawberry.field(
        description="Whether there are more edges before the the start cursor."
    )
    has_next_page: bool = strawberry.field(description="Whether there are more edges after the the end cursor.")

    @classmethod
    def from_edges(
        cls: Type[PageInfo], edges: List[Edge], has_prev_page: bool, has_next_page: bool
    ) -> PageInfo:
        return PageInfo(
            start_cursor=edges[0].cursor,
            end_cursor=edges[-1].cursor,
            has_previous_page=has_prev_page,
            has_next_page=has_next_page,
        )


# A generic type that is a placeholder for any of our strawberry types
TNode = TypeVar("TNode")
TEdge = TypeVar("TEdge")


@strawberry.type
class Edge(Generic[TNode]):
    cursor: str = strawberry.field(
        description="Cursor for this particular edge; is used in a 'before' or 'after' pagination query."
    )
    node: TNode = strawberry.field(description="The actual GraphQL type contained in this Edge.")


@strawberry.type
class Connection(Generic[TNode]):
    total_count: int = strawberry.field(description="Total number of edges that can be paginated over.")
    page_info: PageInfo
    edges: List[Edge[TNode]]


def query_genres(
    first: Optional[int] = None,
    last: Optional[int] = None,
    before: Optional[str] = None,
    after: Optional[str] = None,
    genre: Optional[GENRE_ENUM] = None,
) -> Connection[GenreType]:
    """
    Fetch a page of Genre records from the backend data store.

    Sorry about the length and intensity of this function. Even though this is
    a toy example, the concepts here are the same used when querying records
    from a real data store. Reading through this function line by line
    will be helpful for understanding those concepts.

    All of the input parameters are assumed to be valid. See :class:`PageInfoSchema`

    :param genre_loader: DataLoader for genre objects. This is used to cache
        the page of genres that is returned.
    :param first: if set, the first ``first`` records of the result set are fetched.
    :param last: if set, the last ``last`` records of the result set are fetched.
    :param before: A cursor string; if set, the sort and filter information to build
        the result set from a database query will be derived as well as the index
        of the record embedded in the cursor. The result of this query will be
        the first or last N records before the derived record in the result set
        created by applying the derived filter and sort information.
    :param after: same as ``before`` except results are taken from *after* the
        record derived from this cursor.

    :return: A GenreConnection describing all the Genres that were fetched.
    """
    # set defaults if necessary
    if not first and not last:
        first = 10

    # parse query information from the cursor if provided;
    # Pydantic may throw an error if the required information
    # is not present in the cursor
    cursor: Optional[str] = before or after
    genre_cursor: Optional[GenreCursor] = None
    if cursor:
        genre_cursor = GenreCursor.from_cursor(cursor)

    # fetch genre records applying the sorts and filters in the GenreCursor
    result_set: List[GenreData] = get_genres_result_set(
        genre_cursor_or_filter=genre_cursor or genre, fetch_before=bool(before), fetch_last=bool(last)
    )

    # if 'before' or 'after' are set, we need to select an
    # extra element, because we will remove the cursor element later
    extra = 1 if bool(before) or bool(after) else 0
    num_genres: int = (first or last) + extra
    genres: List[GenreData] = result_set[:num_genres]

    # if there are no genres in the result set, there is no previous or next page of results
    if len(genres) == 0:
        return make_genre_connection(
            genre_datas=[], genre_filter=genre, has_prev_page=False, has_next_page=False, total_count=0
        )

    # calculate whether there is a next/previous page
    has_prev_page, has_next_page = get_next_and_prev_page_info(
        result_set=result_set, num_genres=num_genres, genre_cursor=genre_cursor
    )

    return make_genre_connection(
        genre_datas=genres,
        genre_filter=genre,
        has_prev_page=has_prev_page,
        has_next_page=has_next_page,
        total_count=len(result_set),
        before_or_after=bool(before) or bool(after),
    )


def get_genres_result_set(
    genre_cursor_or_filter: Optional[Union[GenreCursor, GenreEnum]] = None,
    fetch_before: bool = False,
    fetch_last: bool = False,
) -> List[GenreData]:
    """
    Use the ``genre_cursor`` to fetch all of the :class:`GenreData` representations
    that are before the genre record pointed to by the cursor (if ``before``),
    or that are after the genre record pointed to by the cursor (if ``after``).

    Note, this result set INCLUDES the genre record pointed to by the cursor.

    :param genre_cursor: Data about a specific genre record in the data store
        along with any sort or filter constraints that were applied when the
        genre in the cursor was initially fetched.
    :param fetch_before: if ``True``, all GenreData representations
    :param fetch_last: if ``True``, the result set is reversed
    """
    # equivalent of a SQL SELECT statement or other data store query
    result_set: List[GenreData] = list(GENRE_DATA.values())
    # apply any filters
    if genre_cursor_or_filter:
        genre_filter = (
            genre_cursor_or_filter.genre_filter
            if isinstance(genre_cursor_or_filter, GenreCursor)
            else genre_cursor_or_filter.name
        )
        result_set = [r for r in result_set if r.genre == genre_filter]
    # apply any sorts (we don't have any for genres)

    # implement before or after: get records before or after the record that appeared in the cursor
    if isinstance(genre_cursor_or_filter, GenreCursor):
        genre_id: str = genre_cursor_or_filter.genre_id
        genre_id_idx = -1
        try:
            genre_id_idx: int = [g.id for g in result_set].index(genre_id)
        except ValueError:
            raise PaginationError(f"Invalid cursor. Genre with ID {genre_id} does not exist.")

        # get the records before or after the cursor genre INCLUDING the cursor genre itself
        if fetch_before:
            result_set = result_set[: min(genre_id_idx + 1, len(result_set))]
        else:
            result_set = result_set[genre_id_idx:]

    # implement first and last; "last" is easiest
    # to implement by reversing the order of the result set; you could do this in
    # SQL by reversing all ASC and DESC statements
    if fetch_last:
        result_set = reversed(result_set)

    return result_set


def get_next_and_prev_page_info(
    num_genres: int, result_set: List[GenreData], genre_cursor: Optional[GenreCursor] = None
) -> Tuple[bool, bool]:
    # we'll use the ol' +2 trick to calculate has_next_page and has_prev_page without
    # having to do extra hits on the database ✨ fancy ✨
    # https://stackoverflow.com/questions/66293431/how-to-implement-graphql-cursor-in-sql-query-with-sort-by
    genres_plus_two: List[GenreData] = result_set[: num_genres + 2]

    has_prev_page = has_next_page = False
    # genres_plus_two: [cursor genre, first result, second result, ..., last result, extra genre]
    if genre_cursor and genre_cursor.genre_id == genres_plus_two[0].id:
        has_prev_page = True
    if len(genres_plus_two) == num_genres + 2:
        has_next_page = True
    if len(genres_plus_two) == num_genres + 1 and not has_prev_page:
        has_next_page = True

    return has_prev_page, has_next_page


def make_genre_connection(
    genre_datas: List[GenreData],
    genre_filter: Optional[GENRE_ENUM],
    has_prev_page: Optional[bool] = False,
    has_next_page: Optional[bool] = False,
    total_count: Optional[int] = None,
    before_or_after: bool = False,
) -> Connection[GenreType]:

    if not total_count:
        total_count = len(genre_datas)

    # create GenreType objects from the data from the data store. Note that
    # non-scalar resolvers, AKA resolvers that actually have resolver functions
    # won't be called at this time. Those are called by strawberry as it traverses
    # the Abstract Syntax Tree of the GraphQL query itself. If that didn't make sense:
    # the @strawberry.field(resolver=...) functions on GenreData will be called later.
    genres: List[GenreType] = [GenreType.from_data(data) for data in genre_datas]

    # construct the edges
    edges: List[Edge[GenreType]] = []
    for genre in genres:
        cursor: GenreCursor = GenreCursor.from_model(model=genre, genre_filter=genre_filter)
        cursor_str: str = cursor.to_cursor()
        edge = Edge[GenreType](
            cursor=cursor_str,
            node=genre,
        )
        edges.append(edge)

    # we need to exclude the first edge when 'before' or 'after'
    # was present in the search input. For example, if the client requested
    # all the records 'after' the record the cursor is pointing at... then
    # they only want the records 'after'. The first edge *is* the record
    # that the cursor pointed at.
    if before_or_after:
        edges = edges[1:]

    # construct the PageInfo
    page_info: PageInfo = PageInfo.from_edges(
        edges=edges, has_prev_page=has_prev_page, has_next_page=has_next_page
    )

    return Connection[GenreType](edges=edges, page_info=page_info, total_count=total_count)


#####################
# --- Resolvers --- #
#####################

# These resolvers fetch data, but they may or may not use the dataloaders.
# In the case of pagination, they may do special SELECT type statements against
# the backend data store. They will do this WITHOUT using the dataloaders.
# In this special case, they will manually add fetched pages of data objects
# to the appropriate DataLoader cache so we won't need to fetch them next time.


#############################
# --- Strawberry Schema --- #
#############################


@strawberry.type
class Query:
    @strawberry.field
    async def get_genres(
        self, info: Info, page_input: Optional[GenrePageInput] = None
    ) -> Connection[GenreType]:

        print(page_input)

        genres_connection: Optional[Connection[GenreType]] = None
        if not page_input:
            genres_connection = query_genres(first=2)
        else:
            page_input: GenrePageInputSchema = page_input.to_pydantic()
            genres_connection = query_genres(
                first=page_input.first,
                last=page_input.last,
                before=page_input.before,
                after=page_input.after,
                genre=page_input.genre,
            )

        return genres_connection

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

    many_genres_query = """
        query getGenres {
            getGenres {
                totalCount
                pageInfo {
                    hasPreviousPage
                    hasNextPage
                    startCursor
                    endCursor
                }
                edges {
                    cursor
                    node {
                        id
                        readingLevel
                        genre
                    }
                }
            }
        }
    """

    filter_on_genre_query = """
        query getGenres {
            getGenres(
                pageInput: {
                    first:10
                    genre:HISTORY
                }
            ) {
                totalCount
                pageInfo {
                    hasPreviousPage
                    hasNextPage
                    startCursor
                    endCursor
                }
                edges {
                    cursor
                    node {
                        id
                        readingLevel
                        genre
                    }
                }
            }
        }
    """

    ctx = GraphQLContext(
        genre_loader=DataLoader(load_fn=load_genres),
        book_ids_for_genre_loader=DataLoader(load_fn=load_book_ids_for_genre),
        book_loader=DataLoader(load_fn=load_books),
        genre_ids_for_book_loader=DataLoader(load_fn=load_genre_ids_for_book),
    )
    result: ExecutionResult = await schema.execute(filter_on_genre_query, context_value=ctx)

    print(result)
    assert not result.errors


if __name__ == "__main__":
    asyncio.run(main())
