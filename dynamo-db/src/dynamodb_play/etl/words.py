"""
Script to ETL "word" entities from the rootski postgres database into DynamoDB.
"""

import json
from pathlib import Path
from typing import Generator, List, Set

import pandas as pd
import requests
from dynamodb_play.etl.utils import batchify, bulk_upload_to_dynamo
from dynamodb_play.models.word import Word

THIS_DIR = Path(__file__).parent

ROOTSKI_API_BASE_URL = "http://localhost:3333"

WORDS_OUT_DIR = THIS_DIR / "../words"
WORDS_CSV_FPATH = WORDS_OUT_DIR / "../../../../rootski_db_migrations/src/migrations/initial_data/data/words.csv"

#################
# --- Words --- #
#################


def populate_words_dir_with_dynamo_objects(pickup_where_left_off: bool = False, reverse: bool = False):
    WORDS_OUT_DIR.mkdir(exist_ok=True)

    words_df = pd.read_csv(WORDS_CSV_FPATH)
    num_words = len(words_df)

    already_requested_word_ids: Set[int] = get_already_written_ids(dir=WORDS_OUT_DIR)

    rows_iter = words_df[::-1].iterrows() if reverse else words_df.iterrows()

    print(words_df.head())

    for idx, row in rows_iter:
        word_id = row["id"]
        word_pos = row["type"]

        if pickup_where_left_off and word_id in already_requested_word_ids:
            continue

        try:
            request_and_save_word_data(word_id=word_id, pos=word_pos)
            print(f"Success on {idx}/{num_words}\t\tword_id={word_id}\tword_pos={word_pos}")
        except:
            print(f"FAILED \t\tword_id={word_id}\tword_pos={word_pos}")


def get_already_written_ids(dir: Path) -> Set[int]:
    files: List[Path] = dir.glob("*.json")
    file_ids: Set[int] = set(map(lambda fpath: int(fpath.name.strip(".json")), files))
    return file_ids


def request_word_data(word_id: int, pos: str) -> dict:
    return requests.get(f"{ROOTSKI_API_BASE_URL}/word/{word_id}/{pos}").json()


def request_and_save_word_data(word_id: int, pos: str):
    word_data: dict = request_word_data(word_id=word_id, pos=pos)
    jsonified_word_data: str = json.dumps(word_data, indent=4, ensure_ascii=False)
    word_data_outfile_fpath: Path = WORDS_OUT_DIR / f"{word_id}.json"
    word_data_outfile_fpath.write_text(jsonified_word_data, encoding="utf-8")


def extract(batch_size: int) -> Generator[List[dict], None, None]:
    print("Reading all morphemes dicts from disk")
    word_json_fpaths: List[Path] = list(WORDS_OUT_DIR.glob("*.json"))
    for fpaths_batch in batchify(word_json_fpaths, batch_size=batch_size):
        yield [json.loads(fpath.read_text()) for fpath in fpaths_batch]


def transform(word_json_dicts: List[dict]) -> List[dict]:
    results = []
    for d in word_json_dicts:
        try:
            results.append(Word(d).to_item())
        except:
            print(f"Failed to transform word {str(d)}")
    return results


def load(items: List[dict]):
    bulk_upload_to_dynamo(items=items)


def etl():
    raw_word_json_dicts__batch: List[dict]
    for index, raw_word_json_dicts__batch in enumerate(extract(batch_size=500)):
        print(f"processing batch {index}")
        word_items: List[dict] = transform(word_json_dicts=raw_word_json_dicts__batch)
        load(items=word_items)


if __name__ == "__main__":
    # populate_words_dir_with_dynamo_objects(pickup_where_left_off=True, reverse=True)
    etl()
