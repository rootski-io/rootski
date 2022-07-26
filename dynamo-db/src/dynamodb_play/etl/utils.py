from typing import Generator, List, TypeVar

from dynamodb_play.dynamo import get_rootski_dynamo_table

TListItem = TypeVar("TListItem")


def batchify(lst: List[TListItem], batch_size: int) -> Generator[List[TListItem], None, None]:
    """Return a generator that returns sublists of up to ``batch_size`` at a time of ``lst``."""
    num_batches = len(lst) // batch_size
    for batch_index in range(num_batches + 1):
        batch_start_index = batch_index * batch_size
        batch_stop_index = batch_start_index + batch_size
        yield lst[batch_start_index:batch_stop_index]


def bulk_upload_to_dynamo(items: List[dict]):
    table = get_rootski_dynamo_table()
    with table.batch_writer() as batch_writer:
        for item in items:
            batch_writer.put_item(item)


def batch_load_into_dynamo(items: List[dict], batch_size: int):
    """Upload each dict in ``item`` to dynamodb with ``batch_size`` items at a time."""
    for batch_index, batch in enumerate(batchify(items, batch_size=batch_size)):
        print(f"Writing batch {batch_index} to dynamo")
        bulk_upload_to_dynamo(items=batch)
