"""
Script to ETL "word" entities from the rootski postgres database into DynamoDB.
"""

import json
from pathlib import Path
from typing import List, Set

import pandas as pd
import requests

THIS_DIR = Path(__file__).parent

ROOTSKI_API_BASE_URL = "http://localhost:3333"

WORDS_OUT_DIR = THIS_DIR / "words"
WORDS_CSV_FPATH = THIS_DIR / "../../../rootski_db_migrations/src/migrations/initial_data/data/words.csv"

#################
# --- Words --- #
#################


def populate_words_dir_with_dynamo_objects(pickup_where_left_off: bool = False, reverse: bool = False):
    WORDS_OUT_DIR.mkdir(exist_ok=True)

    words_df = pd.read_csv(WORDS_CSV_FPATH)
    num_words = len(words_df)

    already_requested_word_ids: Set[int] = get_already_written_ids(dir=WORDS_OUT_DIR)

    rows_iter = words_df[::-1].iterrows() if reverse else words_df.iterrows()

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


if __name__ == "__main__":
    populate_words_dir_with_dynamo_objects(pickup_where_left_off=True, reverse=True)
