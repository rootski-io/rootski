from pathlib import Path
from rich import print
import pandas as pd
import requests
import json
import time


def get_yandex_word(src_lang: str, trg_lang: str, word: str, api_key: str):
    url = f"https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key={api_key}&lang={src_lang}-{trg_lang}&text={word}"
    r = requests.get(url)
    return r


def write_json_to_file(word: str, _json: dict, _dir: Path):
    fname = f"{word}.json"
    json_fpath: Path = _dir / fname
    json_txt: str = json.dumps(_json, ensure_ascii=False)
    json_fpath.write_text(json_txt)


def cache_yandex_word(src_lang: str, trg_lang: str, word: str, api_key: str, _dir: Path):
    response = get_yandex_word(src_lang=src_lang, trg_lang=trg_lang, word=word, api_key=api_key)

    try:
        if response.status_code == 200:
            _json = response.json()
            write_json_to_file(word=word, _json=_json, _dir=_dir)
        else:
            (_dir / f"{word}.non-200-error").touch()
    except Exception as e:
        print(f"runtime error on word {word}")
        error_msg: str = str(e)
        (_dir / f"{word}.runtime-error").write_text(error_msg)
        raise e


def main():
    api_key = "dict.1.1.20211022T215127Z.167139b1aa0ee365.3565619e97ac2f33668eac91eccb3dbbacea4754"
    src_lang = "ru"
    trg_lang = "en"
    sleep_time_seconds = 0.2

    # ensure translation dir exists
    translations_dir = Path(
        "/Users/eric/repos/extra/rootski/rootski/rootski_api/migrations/initial_data/yandex_data"
    )
    translations_dir.mkdir(exist_ok=True, parents=True)

    # read in the words.csv data
    words_csv_fpath = (
        "/Users/eric/repos/extra/rootski/rootski/rootski_api/migrations/initial_data/data/words.csv"
    )
    df: pd.DataFrame = pd.read_csv(words_csv_fpath)

    # cache yandex data for each of the words
    for word in df.word:
        try:
            time.sleep(sleep_time_seconds)
            cache_yandex_word(
                src_lang=src_lang, trg_lang=trg_lang, word=word, api_key=api_key, _dir=translations_dir
            )
        except Exception as e:
            print(e)
            break
