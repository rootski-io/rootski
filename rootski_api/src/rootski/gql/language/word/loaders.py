from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select, select

import rootski.services.database.models as orm
from rootski import schemas


def make__word_by_id__load_fn(db: AsyncSession):
    """
    Make a DataLoader load function for loading batches of words by their IDs.

    :param db: The async SQLAlchemy ORM session used to fulfill batches
        of :class:`schemas.Word`s from batches of word IDs.
    """

    async def load_words_by_ids(word_ids: List[str]) -> List[schemas.Word]:

        words_ids_as_ints = [int(id_) for id_ in word_ids]
        stmt: Select = select(orm.Word).filter(orm.Word.id.in_(words_ids_as_ints))

        # TODO - what if some of the IDs are invalid and therefore don't exist
        #     in the database? We could handle that by having this dataloader return a mixed
        #     list of:
        #         Errors - for the IDs that were not found
        #         Data Objects - for the IDs that were found
        # TODO - what if this function fails to connect to the database or has
        #     some other error that is raised from SQLAlchemy? Currently, the error message
        #     is taken and displayed to the User in the payload. That is bad. We don't
        #     want the clients that make requests to this API to know anything about the
        #     internal workings of this API. For all they (should) know, it could be written in Golang
        #     using some other GraphQL framework. We need a way to catch any errors that are raised in
        #     our strawberry app and alter the error messages before the strawberry framework takes over
        #     and shows them to the user.
        result = await db.execute(stmt)
        orm_words: List[orm.Word] = result.scalars().all()

        words: List[schemas.Word] = [schemas.Word.from_orm(orm_word) for orm_word in orm_words]
        return words

    return load_words_by_ids
