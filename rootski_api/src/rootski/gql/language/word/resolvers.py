import strawberry
from strawberry import field
from strawberry.dataloader import DataLoader

from rootski import schemas
from rootski.gql.context import TInfo

from .types import Word


@strawberry.type
class WordQuery:
    @field
    async def get_word_by_id(info: TInfo, id: str) -> Word:
        """Fetch the word corresponding with the given word id."""
        word_by_id__loader: DataLoader[str, schemas.Word] = info.context.loaders.word_by_id__loader

        # load the word and convert it to the appropriate graphql type
        word_data: schemas.Word = await word_by_id__loader.load(id)
        word: Word = Word.from_data(data=word_data)

        return word
