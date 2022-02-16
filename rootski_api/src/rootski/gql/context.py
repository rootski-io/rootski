from dataclasses import dataclass
from typing import Callable, List, Optional, TypeVar

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader
from strawberry.types import Info

from rootski import schemas
from rootski.gql.language.word.loaders import make__word_by_id__load_fn


@dataclass
class RootskiDataLoaders:
    word_by_id__loader: DataLoader[str, schemas.Word]


@dataclass
class RootskiGraphQLContext:
    user: schemas.User
    request: Request
    session: AsyncSession
    __loaders: Optional[RootskiDataLoaders] = None

    @property
    def loaders(self) -> RootskiDataLoaders:
        """
        Lazy create the :class:`RootskiDataLoaders`.

        Initializing the DataLoader instances in this way allows
        the DataLoader instances to be aware of the other
        :class:`RootskiGraphQLContext` attributes such as the
        ``request``, ``user``, and ``session``.

        This approach was deemed appropriate because it allows the
        DataLoaders to be able to connect to the appropriate backend
        database or fetch data based on the logged in user WITHOUT
        needing to rely on global variables.
        """
        # only initialize the DataLoaders once
        if self.__loaders is not None:
            return self.__loaders

        # create the load_fn functions for the DataLoaders using
        # factory wrappers that wrap the necessary request context inside
        load_words_by_id: Callable[[List[str]], List[schemas.Word]] = make__word_by_id__load_fn(db=self.session)

        # initialize the DataLoaders
        word_by_id__loader: DataLoader[str, schemas.Word] = DataLoader(load_fn=load_words_by_id)

        self.__loaders = RootskiDataLoaders(word_by_id__loader=word_by_id__loader)

        return self.__loaders


# Info type specific to Rootski
# TODO -- what is TRootValue actually supposed to be? I just included
# it here because the Info Generic type requires it
TRootValue = TypeVar("TRootValue")
TInfo = Info[RootskiGraphQLContext, TRootValue]
