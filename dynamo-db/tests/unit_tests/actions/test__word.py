import pytest

from mypy_boto3_dynamodb.service_resource import _Table

from dynamodb_play.models.word import Word
from dynamodb_play.actions.word import get_word_by_id

SAMPLE_WORD = {
    "word": {
        "word_id": str(689),
        "word": "сознание",
        "accent": "созна'ние",
        "pos": "noun",
        "frequency": 689
    },
    "definitions": [
        {
            "pos": "noun",
            "definitions": [
                {
                    "def_position": 1,
                    "definition_id": 4999,
                    "sub_defs": [
                        {
                            "sub_def_id": 5000,
                            "sub_def_position": 1,
                            "definition": "consciousness",
                            "notes": None
                        },
                        {
                            "sub_def_id": 5001,
                            "sub_def_position": 2,
                            "definition": "realization, perception, awareness",
                            "notes": None
                        }
                    ]
                },
                {
                    "def_position": 2,
                    "definition_id": 5002,
                    "sub_defs": [
                        {
                            "sub_def_id": 5003,
                            "sub_def_position": 1,
                            "definition": "confession",
                            "notes": "(признание)"
                        }
                    ]
                }
            ]
        }
    ],
    "sentences": [
        {
            "rus": "Я потерял сознание.",
            "eng": "I passed out.",
            "exact_match": True
        },
        {
            "rus": "Я потерял сознание.",
            "eng": "I blacked out.",
            "exact_match": True
        },
        {
            "rus": "Я потерял сознание.",
            "eng": "I fainted.",
            "exact_match": True
        },
        {
            "rus": "Бытие определяет сознание.",
            "eng": "Being determines consciousness.",
            "exact_match": True
        },
        {
            "rus": "Том потерял сознание.",
            "eng": "Tom blacked out.",
            "exact_match": True
        },
        {
            "rus": "Том потерял сознание.",
            "eng": "Tom lost consciousness.",
            "exact_match": True
        },
        {
            "rus": "Том потерял сознание.",
            "eng": "Tom has fainted.",
            "exact_match": True
        },
        {
            "rus": "Том потерял сознание.",
            "eng": "Tom passed out.",
            "exact_match": True
        },
        {
            "rus": "Том теряет сознание.",
            "eng": "Tom is losing consciousness.",
            "exact_match": True
        },
        {
            "rus": "Они потеряли сознание.",
            "eng": "They passed out.",
            "exact_match": True
        },
        {
            "rus": "Они потеряли сознание.",
            "eng": "You fainted.",
            "exact_match": True
        },
        {
            "rus": "Ты потерял сознание?",
            "eng": "Did you pass out?",
            "exact_match": True
        },
        {
            "rus": "Она без сознания.",
            "eng": "She is unconscious.",
            "exact_match": False
        },
        {
            "rus": "Он без сознания.",
            "eng": "He's out cold.",
            "exact_match": False
        },
        {
            "rus": "Он без сознания.",
            "eng": "He's unconscious.",
            "exact_match": False
        },
        {
            "rus": "Том без сознания?",
            "eng": "Is Tom unconscious?",
            "exact_match": False
        },
        {
            "rus": "Том без сознания.",
            "eng": "Tom's unconscious.",
            "exact_match": False
        }
    ],
    "declensions": {
        "gender": "n",
        "animate": False,
        "indeclinable": False,
        "nom": "созна'ние",
        "acc": "созна'ние",
        "prep": "созна'нии",
        "gen": "созна'ния",
        "dat": "созна'нию",
        "inst": "созна'нием",
        "nom_pl": "созна'ния",
        "acc_pl": "созна'ния",
        "prep_pl": "созна'ниях",
        "gen_pl": "созна'ний",
        "dat_pl": "созна'ниям",
        "inst_pl": "созна'ниями"
    }
}

@pytest.fixture
def table_with_sample_word(rootski_dynamo_table: _Table) -> _Table:

    word = Word(word_id=SAMPLE_WORD["word"]["word_id"])
    rootski_dynamo_table.put_item(Item={
        **word.keys,
        **SAMPLE_WORD,
        "__type": "WORD",
    })

    yield rootski_dynamo_table


# pylint: disable=unused-argument,redefined-outer-name
def test__get_word_by_id(table_with_sample_word: _Table):
    expected_result = { **SAMPLE_WORD, "PK": "WORD#689", "SK": "WORD#689", "__type": "WORD"}
    actual_result = get_word_by_id(word_id=SAMPLE_WORD["word"]["word_id"])
    assert expected_result == actual_result


# pylint: disable=unused-argument,redefined-outer-name
def test__get_word_by_id__word_not_found(table_with_sample_word: _Table):
    word = get_word_by_id(word_id="bad id that doesn't exist")
    assert word is None
