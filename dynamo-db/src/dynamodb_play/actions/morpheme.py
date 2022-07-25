from dynamodb_play.dynamo import get_rootski_dynamo_table
from dynamodb_play.models.morpheme import Morpheme
from dynamodb_play.models.morpheme_family import MorphemeFamily


def upsert_morpheme_family(family: MorphemeFamily):
    family.family


def upsert_morpheme(morpheme: Morpheme):
    table = get_rootski_dynamo_table()

    table.put_item(morpheme.to_item())
