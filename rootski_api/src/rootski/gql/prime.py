from asyncio import AbstractEventLoop, Future
from typing import TypeVar

from strawberry.dataloader import DataLoader

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")


def prime(loader: DataLoader[TKey, TValue], key: TKey, value: TValue) -> None:
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

    .. note::

        This function is an official part of the GraphQL JavaScript
        reference implementation. The subset of the GraphQL Dataloader
        API that has to do with this is called the "Prime API".
        Unfortunately, it has not been included in ``strawberry-graphql``
        as of Nov 1, 2021.

        You can think of this function as "priming" a DataLoader's cache
        with a value we acquired by some means other than calling
        ``DataLoader.load()``.

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
