"""
Seed data to put into the mock DynamoDB table and test the breakdown endpoint.
"""
from decimal import Decimal

from mypy_boto3_dynamodb.service_resource import _Table

#############################
# Modified/made-up Examples #
#############################

EXAMPLE_BREAKDOWN = {
    "pk": "WORD#32",
    "sk": "BREAKDOWN",
    "gsi1pk": "USER#anonymous",
    "gsi1sk": "WORD#32",
    "gsi2pk": "WORD#32",
    "gsi2sk": "USER#anonymous",
    "__type": "BREAKDOWN",
    "word": "мочь",
    "word_id": "32",
    "submitted_by_user_email": "anonymous",
    "is_verified": False,
    "is_inference": True,
    "date_submitted": "2022-02-15 05:45:18.740114",
    "date_verified": "None",
    "breakdown_items": [{"position": 0, "morpheme_id": None, "morpheme": "мочь", "morpheme_family_id": None}],
}


EXAMPLE_BREAKDOWN_2 = {
    "pk": "WORD#61900",
    "sk": "BREAKDOWN",
    "gsi1pk": "USER#anonymous",
    "gsi1sk": "WORD#61900",
    "gsi2pk": "WORD#61900",
    "gsi2sk": "USER#anonymous",
    "__type": "BREAKDOWN",
    "word": "занавешивать",
    "word_id": "61900",
    "submitted_by_user_email": "anonymous",
    "is_verified": False,
    "is_inference": True,
    "date_submitted": "2022-02-15 05:45:18.740114",
    "date_verified": "None",
    "breakdown_items": [
        {"position": 0, "morpheme": "занавеш", "morpheme_id": None, "morpheme_family_id": None},
        {"position": 1, "morpheme": "ивать", "morpheme_id": None, "morpheme_family_id": None},
    ],
}


EXAMPLE_BREAKDOWN_ANOTHER_USER_2 = {
    "pk": "WORD#5",
    "sk": "BREAKDOWN",
    "gsi1pk": "USER#another_user@gmail.com",
    "gsi1sk": "WORD#5",
    "gsi2pk": "WORD#5",
    "gsi2sk": "USER#another_user@gmail.com",
    "__type": "BREAKDOWN",
    "word": "занавешивать",
    "word_id": "5",
    "submitted_by_user_email": "another_user@gmail.com",
    "is_verified": True,
    "is_inference": False,
    "date_submitted": "2022-02-15 05:45:18.740114",
    "date_verified": "None",
    "breakdown_items": [
        {"position": 0, "morpheme": "занавеш", "morpheme_id": None, "morpheme_family_id": None},
        {"position": 1, "morpheme": "ивать", "morpheme_id": None, "morpheme_family_id": None},
    ],
}


EXAMPLE_BREAKDOWN_ANOTHER_USER = {
    "pk": "WORD#10",
    "sk": "BREAKDOWN",
    "gsi1pk": "USER#another_user@gmail.com",
    "gsi1sk": "WORD#10",
    "gsi2pk": "WORD#10",
    "gsi2sk": "USER#another_user@gmail.com",
    "__type": "BREAKDOWN",
    "word": "занавешивать",
    "word_id": "10",
    "submitted_by_user_email": "another_user@gmail.com",
    "is_verified": False,
    "is_inference": False,
    "date_submitted": "2022-02-15 05:45:18.740114",
    "date_verified": "None",
    "breakdown_items": [
        {"position": 0, "morpheme": "занавеш", "morpheme_id": None, "morpheme_family_id": None},
        {"position": 1, "morpheme": "ивать", "morpheme_id": None, "morpheme_family_id": None},
    ],
}


EXAMPLE_BREAKDOWN_ERIC_USER = {
    "pk": "WORD#5",
    "sk": "BREAKDOWN",
    "gsi1pk": "USER#eric.riddoch@gmail.com",
    "gsi1sk": "WORD#5",
    "gsi2pk": "WORD#5",
    "gsi2sk": "USER#eric.riddoch@gmail.com",
    "__type": "BREAKDOWN",
    "word": "занавешивать",
    "word_id": "5",
    "submitted_by_user_email": "eric.riddoch@gmail.com",
    "is_verified": True,
    "is_inference": False,
    "date_submitted": "2022-02-15 05:45:18.740114",
    "date_verified": "None",
    "breakdown_items": [
        {"position": 0, "morpheme": "занавеш", "morpheme_id": None, "morpheme_family_id": None},
        {"position": 1, "morpheme": "ивать", "morpheme_id": None, "morpheme_family_id": None},
    ],
}


###############################
# Official Breakdown Examples #
###############################

EXAMPLE_BREAKDOWN_W_NULL_AND_NON_NULL_BREAKDOWN_ITEMS_IN_DB = {
    "gsi2sk": "USER#anonymous",
    "submitted_by_user_email": "anonymous",
    "gsi1sk": "WORD#7",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "7",
    "date_submitted": "2022-02-15 05:45:18.740114",
    "word": "быть",
    "sk": "BREAKDOWN",
    "pk": "WORD#7",
    "breakdown_items": [
        {"morpheme": "бы", "morpheme_family_id": "934", "position": "0", "morpheme_id": "1776"},
        {"morpheme": "ть", "morpheme_family_id": None, "position": "1", "morpheme_id": None},
    ],
    "gsi1pk": "USER#anonymous",
    "is_verified": False,
    "is_inference": True,
    "gsi2pk": "WORD#7",
}


EXAMPLE_BREAKDOWN_W_ALL_NULL_BREAKDOWN_ITEMS = {
    "gsi2sk": "USER#anonymous",
    "submitted_by_user_email": "anonymous",
    "gsi1sk": "WORD#56",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "56",
    "date_submitted": "2022-02-15 05:45:18.740114",
    "word": "самый",
    "sk": "BREAKDOWN",
    "pk": "WORD#56",
    "breakdown_items": [
        {"morpheme": "сам", "morpheme_family_id": None, "position": "0", "morpheme_id": None},
        {"morpheme": "ый", "morpheme_family_id": None, "position": "1", "morpheme_id": None},
    ],
    "gsi1pk": "USER#anonymous",
    "is_verified": False,
    "is_inference": True,
    "gsi2pk": "WORD#56",
}


EXAMPLE_BREAKDOWN_W_MORPHEME_FAMILIES_IN_DB = {
    "gsi2sk": "USER#anonymous",
    "submitted_by_user_email": "anonymous",
    "gsi1sk": "WORD#57",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "57",
    "date_submitted": "2022-02-15 05:45:18.740114",
    "word": "знать",
    "sk": "BREAKDOWN",
    "pk": "WORD#57",
    "breakdown_items": [
        {"morpheme": "зна", "morpheme_family_id": "245", "position": 0, "morpheme_id": "511"},
        {"morpheme": "ть", "morpheme_family_id": "1385", "position": 1, "morpheme_id": "2196"},
        {"morpheme": "зна", "morpheme_family_id": "245", "position": 0, "morpheme_id": "511"},
        {"morpheme": "ть", "morpheme_family_id": "1385", "position": 1, "morpheme_id": "2196"},
    ],
    "gsi1pk": "USER#anonymous",
    "is_verified": False,
    "is_inference": True,
    "gsi2pk": "WORD#57",
}


EXAMPLE_BREAKDOWN_W_NO_NULL_BREAKDOWN_ITEMS = {
    "gsi2sk": "USER#anonymous",
    "submitted_by_user_email": "anonymous",
    "gsi1sk": "WORD#438",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "438",
    "date_submitted": "2022-02-15 05:45:18.740114",
    "word": "выходить",
    "sk": "BREAKDOWN",
    "pk": "WORD#438",
    "breakdown_items": [
        {"morpheme": "вы", "morpheme_family_id": "102", "position": "0", "morpheme_id": "218"},
        {"morpheme": "ход", "morpheme_family_id": "812", "position": "1", "morpheme_id": "1577"},
        {"morpheme": "ить", "morpheme_family_id": "1333", "position": "2", "morpheme_id": "2139"},
    ],
    "gsi1pk": "USER#anonymous",
    "is_verified": False,
    "is_inference": True,
    "gsi2pk": "WORD#438",
}


EXAMPLE_VERIFIED_BREAKDOWN = {
    "gsi2sk": "USER#eric.riddoch@gmail.com",
    "submitted_by_user_email": "eric.riddoch@gmail.com",
    "gsi1sk": "WORD#771",
    "date_verified": "2022-07-23 05:42:11.985578",
    "__type": "BREAKDOWN",
    "word_id": "771",
    "date_submitted": "2022-02-15 09:00:24.068323",
    "word": "выглядеть",
    "sk": "BREAKDOWN",
    "pk": "WORD#771",
    "breakdown_items": [
        {"morpheme": "вы", "morpheme_family_id": "1401", "position": "0", "morpheme_id": "2213"},
        {"morpheme": "гляд", "morpheme_family_id": "127", "position": "1", "morpheme_id": "276"},
        {"morpheme": "еть", "morpheme_family_id": "1324", "position": "2", "morpheme_id": "2130"},
    ],
    "gsi1pk": "USER#eric.riddoch@gmail.com",
    "is_verified": True,
    "is_inference": False,
    "gsi2pk": "WORD#771",
}


EXAMPLE_NON_VERIFIED_BREAKDOWN_SUBMITTED_BY_USER = {
    "gsi2sk": "USER#dmitriy.abaimov@bengroupinc.com",
    "submitted_by_user_email": "dmitriy.abaimov@bengroupinc.com",
    "gsi1sk": "WORD#59470",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "59470",
    "date_submitted": "2022-02-23 15:38:30.049221",
    "word": "None",
    "sk": "BREAKDOWN",
    "pk": "WORD#59470",
    "breakdown_items": [
        {"morpheme": "само", "morpheme_family_id": "1107", "position": "0", "morpheme_id": "1892"},
        {"morpheme": "у", "morpheme_family_id": "1399", "position": "1", "morpheme_id": "2211"},
        {"morpheme": "со", "morpheme_family_id": "1403", "position": "2", "morpheme_id": "2219"},
        {"morpheme": "верш", "morpheme_family_id": "64", "position": "3", "morpheme_id": "124"},
        {"morpheme": "ен", "morpheme_family_id": None, "position": "4", "morpheme_id": None},
        {"morpheme": "ство", "morpheme_family_id": "1268", "position": "5", "morpheme_id": "2066"},
        {"morpheme": "ва", "morpheme_family_id": None, "position": "6", "morpheme_id": None},
        {"morpheme": "ни", "morpheme_family_id": None, "position": "7", "morpheme_id": None},
        {"morpheme": "е", "morpheme_family_id": "1189", "position": "8", "morpheme_id": "1985"},
    ],
    "gsi1pk": "USER#dmitriy.abaimov@bengroupinc.com",
    "is_verified": False,
    "is_inference": False,
    "gsi2pk": "WORD#59470",
}


#####################################
# User Submitted Breakdown Examples #
#####################################


EXAMPLE_USER_SUBMITTED_BREAKDOWN = {
    "submitted_by_user_email": "email@gmail.com",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "7",
    "date_submitted": "2022-02-15 05:45:18.740114",
    "word": "быть",
    "sk": "BREAKDOWN#7",
    "pk": "USER#email@gmail.com",
    "breakdown_items": [
        {"morpheme": "бы", "morpheme_family_id": "934", "position": "0", "morpheme_id": "1776"},
        {"morpheme": "ть", "morpheme_family_id": None, "position": "1", "morpheme_id": None},
    ],
    "is_verified": False,
    "is_inference": False,
}


EXAMPLE_USER_SUBMITTED_BREAKDOWN_COPY_W_DIFF_USER = {
    "submitted_by_user_email": "another_user@gmail.com",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "7",
    "date_submitted": "2022-02-15 05:45:18.740114",
    "word": "быть",
    "sk": "BREAKDOWN#7",
    "pk": "USER#another_user@gmail.com",
    "breakdown_items": [
        {"morpheme": "бы", "morpheme_family_id": "934", "position": "0", "morpheme_id": "1776"},
        {"morpheme": "ть", "morpheme_family_id": None, "position": "1", "morpheme_id": None},
    ],
    "is_verified": False,
    "is_inference": False,
}


###################
# Breakdown Items #
###################


EXAMPLE_BREAKDOWN_ITEM = {
    "submitted_by_user_email": "eric.riddoch@gmail.com",
    "breakdown_id": "77222",
    "morpheme_id": "2213",
    "gsi1sk": "BREAKDOWN#eric.riddoch@gmail.com",
    "__type": "BREAKDOWN_ITEM",
    "word_id": "771",
    "sk": "BREAKDOWN_ITEM#2213#0",
    "morpheme_family_id": "2213",
    "pk": "WORD#771",
    "position": 0,
    "morpheme": "вы",
    "gsi1pk": "MORPHEME_FAMILY#2213",
}


EXAMPLE_NULL_BREAKDOWN_ITEM = {
    "pk": "WORD#9203",
    "sk": "BREAKDOWN_ITEM#f4ef8326-a27e-4cb6-9cac-0089fc1eda45#8",
    "__type": "BREAKDOWN_ITEM_NULL",
    "word_id": "9203",
    "position": 8,
    "morpheme": "ся",
    "morpheme_id": None,
    "morpheme_family_id": None,
    "submitted_by_user_email": None,
}

#####################
# Morpheme Families #
#####################

EXAMPLE_MORPHEME_FAMILY_245 = {
    "morphemes": [{"morpheme": "знай", "morpheme_id": "510"}, {"morpheme": "зна", "morpheme_id": "511"}],
    "family_meanings": ["know"],
    "level": Decimal("1"),
    "__type": "MORPHEME_FAMILY",
    "sk": "MORPHEME_FAMILY#245",
    "word_pos": "any",
    "family_id": "245",
    "pk": "MORPHEME_FAMILY#245",
    "type": "root",
}


EXAMPLE_MORPHEME_FAMILY_1304 = {
    "morphemes": [
        {"morpheme": "ать", "morpheme_id": "2105"},
        {"morpheme": "ывать", "morpheme_id": "2106"},
        {"morpheme": "ивать", "morpheme_id": "2107"},
    ],
    "family_meanings": [None],
    "level": Decimal("6"),
    "__type": "MORPHEME_FAMILY",
    "sk": "MORPHEME_FAMILY#1304",
    "word_pos": "verb",
    "family_id": "1304",
    "pk": "MORPHEME_FAMILY#1304",
    "type": "suffix",
}


EXAMPLE_MORPHEME_FAMILY_1385 = {
    "morphemes": [{"morpheme": "ть", "morpheme_id": "2196"}],
    "family_meanings": [None],
    "level": Decimal("6"),
    "__type": "MORPHEME_FAMILY",
    "sk": "MORPHEME_FAMILY#1385",
    "word_pos": "verb",
    "family_id": "1385",
    "pk": "MORPHEME_FAMILY#1385",
    "type": "suffix",
}


#############
# Morphemes #
#############

EXAMPLE_MORPHEME_W_ID_2105 = {
    "morpheme_id": "2105",
    "gsi1sk": "MORPHEME#2105",
    "__type": "MORPHEME",
    "sk": "MORPHEME#2105",
    "family_id": "1304",
    "pk": "MORPHEME_FAMILY#1304",
    "morpheme": "ать",
    "gsi1pk": "MORPHEME#2105",
}


EXAMPLE_MORPHEME_W_ID_1776 = {
    "morpheme_id": "1776",
    "gsi1sk": "MORPHEME#1776",
    "__type": "MORPHEME",
    "sk": "MORPHEME#1776",
    "family_id": "934",
    "pk": "MORPHEME_FAMILY#934",
    "morpheme": "бы",
    "gsi1pk": "MORPHEME#1776",
}

########
# Word #
########

EXAMPLE_WORD_W_ID_7 = {
    "definitions": [
        {
            "pos": "verb",
            "definitions": [
                {
                    "sub_defs": [
                        {
                            "definition": "be",
                            "notes": None,
                            "sub_def_position": Decimal("1"),
                            "sub_def_id": Decimal("96"),
                        },
                        {
                            "definition": "happen",
                            "notes": None,
                            "sub_def_position": Decimal("2"),
                            "sub_def_id": Decimal("97"),
                        },
                        {
                            "definition": "(would you) please",
                            "notes": None,
                            "sub_def_position": Decimal("3"),
                            "sub_def_id": Decimal("98"),
                        },
                        {
                            "definition": "will you be so kind",
                            "notes": None,
                            "sub_def_position": Decimal("4"),
                            "sub_def_id": Decimal("99"),
                        },
                        {
                            "definition": "more are coming (on the way)",
                            "notes": None,
                            "sub_def_position": Decimal("5"),
                            "sub_def_id": Decimal("100"),
                        },
                        {
                            "definition": "a piece of a churchyard fits everybody",
                            "notes": None,
                            "sub_def_position": Decimal("6"),
                            "sub_def_id": Decimal("101"),
                        },
                        {
                            "definition": "All face one way",
                            "notes": None,
                            "sub_def_position": Decimal("7"),
                            "sub_def_id": Decimal("102"),
                        },
                    ],
                    "def_position": Decimal("1"),
                    "definition_id": Decimal("95"),
                }
            ],
        }
    ],
    "conjugations": {
        "1st_per_pl": "бу'дем",
        "past_pl": "бы'ли",
        "1st_per_sing": "бу'ду",
        "3rd_per_sing": "бу'дет",
        "past_n": "бы'ло",
        "actv_past_part": "бы'вший",
        "past_m": "был",
        "actv_part": "бы'вший",
        "past_f": "была'",
        "2nd_per_sing": "бу'дешь",
        "aspect": "impf",
        "impr": "будь",
        "pass_part": None,
        "pass_past_part": None,
        "3rd_per_pl": "бу'дут",
        "impr_pl": "бу'дьте",
        "2nd_per_pl": "бу'дете",
        "gerund": "бу'дучи",
    },
    "aspectual_pairs": [
        {"imp_accent": "быть", "pfv_word_id": None, "pfv_accent": None, "imp_word_id": Decimal("7")}
    ],
    "__type": "WORD",
    "sk": "WORD#7",
    "pk": "WORD#7",
    "word": {"word_id": "7", "word": "быть", "accent": "быть", "pos": "verb", "frequency": Decimal("7")},
    "sentences": [
        {"rus": "Быть не может.", "exact_match": True, "eng": "That's impossible."},
        {"rus": "Быть значит поступать.", "exact_match": True, "eng": "To be is to do."},
        {"rus": "Каково быть замужем?", "exact_match": True, "eng": "How does it feel being married?"},
        {"rus": "Должно быть весело.", "exact_match": True, "eng": "It should be fun."},
        {"rus": "Должно быть весело.", "exact_match": True, "eng": "That must be fun."},
        {"rus": "Может быть.", "exact_match": True, "eng": "It may be."},
        {"rus": "Не может быть!", "exact_match": True, "eng": "This is impossible!"},
        {"rus": "Не может быть!", "exact_match": True, "eng": "This can't be!"},
        {"rus": "Не может быть!", "exact_match": True, "eng": "Unbelievable!"},
        {"rus": "Хочешь быть богатым?", "exact_match": True, "eng": "Do you want to be rich?"},
        {"rus": "Хорошо быть дома.", "exact_match": True, "eng": "It's nice to be home."},
        {"rus": "Быть не может.", "exact_match": True, "eng": "That can't be."},
        {"rus": "Бытие определяет сознание.", "exact_match": False, "eng": "Being determines consciousness."},
    ],
}


EXAMPLE_WORD_W_ID_18 = {
    "definitions": [
        {
            "pos": "pronoun",
            "definitions": [
                {
                    "sub_defs": [
                        {
                            "definition": "they",
                            "notes": "пред. - них",
                            "sub_def_position": Decimal("1"),
                            "sub_def_id": Decimal("215"),
                        },
                        {
                            "definition": "them",
                            "notes": None,
                            "sub_def_position": Decimal("2"),
                            "sub_def_id": Decimal("216"),
                        },
                    ],
                    "def_position": Decimal("1"),
                    "definition_id": Decimal("214"),
                }
            ],
        }
    ],
    "__type": "WORD",
    "sk": "WORD#18",
    "pk": "WORD#18",
    "word": {"word_id": "18", "word": "они", "accent": "они'", "pos": "pronoun", "frequency": Decimal("18")},
    "sentences": [
        {"rus": "Они?", "exact_match": True, "eng": "They are?"},
        {"rus": "Они — борцы.", "exact_match": True, "eng": "They are wrestlers."},
        {"rus": "Они поженились.", "exact_match": True, "eng": "They got married."},
        {"rus": "Они поссорились.", "exact_match": True, "eng": "They had an argument."},
        {"rus": "Где они?", "exact_match": True, "eng": "Where are they?"},
        {"rus": "Они болтают.", "exact_match": True, "eng": "They are having a chat."},
        {"rus": "Они друзья?", "exact_match": True, "eng": "Are they friends?"},
        {"rus": "Они ровесники.", "exact_match": True, "eng": "They are the same age."},
        {"rus": "Они бегут.", "exact_match": True, "eng": "They run."},
        {"rus": "Они христиане.", "exact_match": True, "eng": "They are Christians."},
    ],
}


EXAMPLE_WORD_W_ID_50 = {
    "definitions": [
        {
            "pos": "verb",
            "definitions": [
                {
                    "sub_defs": [
                        {
                            "definition": "say, tell",
                            "notes": None,
                            "sub_def_position": Decimal("1"),
                            "sub_def_id": Decimal("477"),
                        },
                        {
                            "definition": "speak, talk",
                            "notes": None,
                            "sub_def_position": Decimal("2"),
                            "sub_def_id": Decimal("478"),
                        },
                        {
                            "definition": "I must say",
                            "notes": None,
                            "sub_def_position": Decimal("3"),
                            "sub_def_id": Decimal("479"),
                        },
                        {
                            "definition": "as a matter of fact",
                            "notes": None,
                            "sub_def_position": Decimal("4"),
                            "sub_def_id": Decimal("480"),
                        },
                        {
                            "definition": "not to mention",
                            "notes": None,
                            "sub_def_position": Decimal("5"),
                            "sub_def_id": Decimal("481"),
                        },
                        {
                            "definition": "well, I never (did)",
                            "notes": None,
                            "sub_def_position": Decimal("6"),
                            "sub_def_id": Decimal("482"),
                        },
                    ],
                    "def_position": Decimal("1"),
                    "definition_id": Decimal("476"),
                }
            ],
        }
    ],
    "conjugations": {
        "1st_per_pl": "ска'жем",
        "past_pl": "сказа'ли",
        "1st_per_sing": "скажу'",
        "3rd_per_sing": "ска'жет",
        "past_n": "сказа'ло",
        "actv_past_part": "сказа'вший",
        "past_m": "сказа'л",
        "actv_part": None,
        "past_f": "сказа'ла",
        "2nd_per_sing": "ска'жешь",
        "aspect": "perf",
        "impr": "скажи'",
        "pass_part": None,
        "pass_past_part": "ска'занный",
        "3rd_per_pl": "ска'жут",
        "impr_pl": "скажи'те",
        "2nd_per_pl": "ска'жете",
        "gerund": "сказа'в",
    },
    "aspectual_pairs": [
        {
            "imp_accent": "говори'ть",
            "pfv_word_id": Decimal("50"),
            "pfv_accent": "сказа'ть",
            "imp_word_id": Decimal("55"),
        },
        {
            "imp_accent": "ска'зывать",
            "pfv_word_id": Decimal("50"),
            "pfv_accent": "сказа'ть",
            "imp_word_id": Decimal("16029"),
        },
    ],
    "__type": "WORD",
    "sk": "WORD#50",
    "pk": "WORD#50",
    "word": {
        "word_id": "50",
        "word": "сказать",
        "accent": "сказа'ть",
        "pos": "verb",
        "frequency": Decimal("50"),
    },
    "sentences": [
        {"rus": "Сказать?", "exact_match": True, "eng": "Should I tell?"},
        {"rus": "Как сказать... ?", "exact_match": True, "eng": "How do you say...?"},
        {"rus": "Сказать ему?", "exact_match": True, "eng": "Should I tell him?"},
        {"rus": "Сказать ему?", "exact_match": True, "eng": "Ought I to tell it to him?"},
        {"rus": "Дай сказать.", "exact_match": True, "eng": "Let me speak."},
        {"rus": "Дайте сказать.", "exact_match": True, "eng": "Let me talk."},
        {"rus": "Сложно сказать.", "exact_match": True, "eng": "It's hard to say."},
        {"rus": "Сказано — сделано.", "exact_match": False, "eng": "No sooner said than done."},
        {"rus": "Сказано — сделано.", "exact_match": False, "eng": "Immediately said, immediately done."},
        {"rus": "Отлично сказано!", "exact_match": False, "eng": "Well said!"},
        {"rus": "Вам сказали.", "exact_match": False, "eng": "You've been told."},
    ],
}


#########
# Users #
#########

ADMIN_USER = {
    "pk": "USER#eric.riddoch@gmail.com",
    "sk": "USER#eric.riddoch@gmail.com",
    "email": "eric.riddoch@gmail.com",
    "is_admin": True,
}

NON_ADMIN_USER = {
    "pk": "USER#dmitriy.abaimov@bengroupinc.com",
    "sk": "USER#dmitriy.abaimov@bengroupinc.com",
    "email": "dmitriy.abaimov@bengroupinc.com",
    "is_admin": False,
}

TEST_USER_NOT_AS_ADMIN = {
    "pk": "USER#email@gmail.com",
    "sk": "USER#email@gmail.com",
    "email": "email@gmail.com",
    "is_admin": False,
}

TEST_USER_AS_ADMIN = {
    "pk": "USER#super_user@batcave.com",
    "sk": "USER#super_user@batcave.com",
    "email": "super_user@batcave.com",
    "is_admin": True,
}


####################
# User Submissions #
####################

EXAMPLE_USER_SUBMISSION_REPLACING_CURRENT_BREAKDOWN = {
    "word_id": 7,
    "breakdown_items": [
        {"morpheme_id": 1776, "position": 0},
        {"morpheme": "ть", "position": 1, "morpheme_id": None},
    ],
}


EXAMPLE_SUCCESSFUL_BREAKDOWN_SUBMISSION = {
    "word_id": 50,
    "breakdown_items": [
        {"morpheme": "сказ", "position": 0, "morpheme_id": None},
        {"morpheme_id": 2105, "position": 1},
    ],
}


EXAMPLE_BREAKDOWN_DOESNT_ADD_UP = {
    "word_id": 50,
    "breakdown_items": [
        {"morpheme": "сказe", "position": 0, "morpheme_id": None},
        {"morpheme_id": 2105, "position": 1},
    ],
}


EXAMPLE_SUCCESSFUL_BREAKDOWN_W_ALL_NULL_BREAKDOWN_ITEMS = {
    "word_id": 18,
    "breakdown_items": [
        {"morpheme": "он", "position": 0, "morpheme_id": None},
        {"morpheme": "и", "position": 1, "morpheme_id": None},
    ],
}


EXAMPLE_USER_SUBMISSION_MISSING_MORPHEME_IDS = {
    "word_id": 438,
    "breakdown_items": [
        {"position": 0, "morpheme_id": 218},
        {"position": 1, "morpheme_id": 1577},
        {"position": 2, "morpheme_id": 2139},
    ],
}


EXAMPLE_USER_SUBMISSION_MISSING_WORD = {
    "word_id": 150,
    "breakdown_items": [{"morpheme": "именно", "position": 0, "morpheme_id": None}],
}


#################
# Seed Database #
#################

EXAMPLE_DATA = [
    # Hand-crafted/Modified examples for testing
    EXAMPLE_BREAKDOWN,
    EXAMPLE_BREAKDOWN_2,
    EXAMPLE_BREAKDOWN_ANOTHER_USER,
    EXAMPLE_BREAKDOWN_ANOTHER_USER_2,
    EXAMPLE_BREAKDOWN_ERIC_USER,
    # Offical Beakdown Examples based on real data
    EXAMPLE_BREAKDOWN_W_NULL_AND_NON_NULL_BREAKDOWN_ITEMS_IN_DB,  # inferenced example
    EXAMPLE_BREAKDOWN_W_ALL_NULL_BREAKDOWN_ITEMS,  # inferenced example with all null breakdown items
    EXAMPLE_BREAKDOWN_W_NO_NULL_BREAKDOWN_ITEMS,  # inferenced example with no null breakdown items
    EXAMPLE_BREAKDOWN_W_MORPHEME_FAMILIES_IN_DB,  # inferenced example with duplicate breakdown_items
    EXAMPLE_VERIFIED_BREAKDOWN,  # Verified example by user eric.riddoch@gmail.com
    EXAMPLE_NON_VERIFIED_BREAKDOWN_SUBMITTED_BY_USER,  # Non-verified example by user dmitriy.abaimov@bengroupinc.com
    # User Submitted Breakdown Examples
    EXAMPLE_USER_SUBMITTED_BREAKDOWN,
    # Breakdown Items
    EXAMPLE_BREAKDOWN_ITEM,
    EXAMPLE_NULL_BREAKDOWN_ITEM,
    # Morpheme Families
    EXAMPLE_MORPHEME_FAMILY_245,
    EXAMPLE_MORPHEME_FAMILY_1304,
    EXAMPLE_MORPHEME_FAMILY_1385,
    # Morphemes
    EXAMPLE_MORPHEME_W_ID_2105,
    EXAMPLE_MORPHEME_W_ID_1776,
    # Words
    EXAMPLE_WORD_W_ID_7,
    EXAMPLE_WORD_W_ID_18,
    EXAMPLE_WORD_W_ID_50,
    # Users
    ADMIN_USER,
    NON_ADMIN_USER,
    TEST_USER_NOT_AS_ADMIN,
    TEST_USER_AS_ADMIN,
]


USER_SUBMISSION_DATA = [
    EXAMPLE_USER_SUBMISSION_REPLACING_CURRENT_BREAKDOWN,
    EXAMPLE_SUCCESSFUL_BREAKDOWN_SUBMISSION,
    EXAMPLE_BREAKDOWN_DOESNT_ADD_UP,
    EXAMPLE_SUCCESSFUL_BREAKDOWN_W_ALL_NULL_BREAKDOWN_ITEMS,
    EXAMPLE_USER_SUBMISSION_MISSING_MORPHEME_IDS,
    EXAMPLE_USER_SUBMISSION_MISSING_WORD,
]


# Helper Function
def seed_data(rootski_dynamo_table: _Table) -> None:
    for data in EXAMPLE_DATA:
        rootski_dynamo_table.put_item(Item=data)


if __name__ == "__main__":
    from rootski.services.database.dynamo.db_service import DBService

    db: DBService = DBService("rootski-table")
    db.init()
    table = db.rootski_table
    # get_item_response = table.get_item(Key={"pk": "MORPHEME_FAMILY#934", "sk": "MORPHEME#1776"})
    get_item_response = table.get_item(Key={"pk": "WORD#150", "sk": "WORD#150"})
    print(get_item_response["Item"])
######################
# Official Breakdown Examples #
######################

EXAMPLE_BREAKDOWN_W_NULL_AND_NON_NULL_BREAKDOWN_ITEMS_IN_DB = {
    "gsi2sk": "USER#anonymous",
    "submitted_by_user_email": "anonymous",
    "gsi1sk": "WORD#7",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "7",
    "date_submitted": "2022-02-15 05:45:18.740114",
    "word": "быть",
    "sk": "BREAKDOWN",
    "pk": "WORD#7",
    "breakdown_items": [
        {"morpheme": "бы", "morpheme_family_id": "934", "position": "0", "morpheme_id": "1776"},
        {"morpheme": "ть", "morpheme_family_id": None, "position": "1", "morpheme_id": None},
    ],
    "gsi1pk": "USER#anonymous",
    "is_verified": False,
    "is_inference": True,
    "gsi2pk": "WORD#7",
}


EXAMPLE_BREAKDOWN_W_ALL_NULL_BREAKDOWN_ITEMS = {
    "gsi2sk": "USER#anonymous",
    "submitted_by_user_email": "anonymous",
    "gsi1sk": "WORD#56",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "56",
    "date_submitted": "2022-02-15 05:45:18.740114",
    "word": "самый",
    "sk": "BREAKDOWN",
    "pk": "WORD#56",
    "breakdown_items": [
        {"morpheme": "сам", "morpheme_family_id": None, "position": "0", "morpheme_id": None},
        {"morpheme": "ый", "morpheme_family_id": None, "position": "1", "morpheme_id": None},
    ],
    "gsi1pk": "USER#anonymous",
    "is_verified": False,
    "is_inference": True,
    "gsi2pk": "WORD#56",
}


EXAMPLE_BREAKDOWN_W_MORPHEME_FAMILIES_IN_DB = {
    "gsi2sk": "USER#anonymous",
    "submitted_by_user_email": "anonymous",
    "gsi1sk": "WORD#57",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "57",
    "date_submitted": "2022-02-15 05:45:18.740114",
    "word": "знать",
    "sk": "BREAKDOWN",
    "pk": "WORD#57",
    "breakdown_items": [
        {"morpheme": "зна", "morpheme_family_id": "245", "position": 0, "morpheme_id": "511"},
        {"morpheme": "ть", "morpheme_family_id": "1385", "position": 1, "morpheme_id": "2196"},
        {"morpheme": "зна", "morpheme_family_id": "245", "position": 0, "morpheme_id": "511"},
        {"morpheme": "ть", "morpheme_family_id": "1385", "position": 1, "morpheme_id": "2196"},
    ],
    "gsi1pk": "USER#anonymous",
    "is_verified": False,
    "is_inference": True,
    "gsi2pk": "WORD#57",
}


EXAMPLE_BREAKDOWN_W_NO_NULL_BREAKDOWN_ITEMS = {
    "gsi2sk": "USER#anonymous",
    "submitted_by_user_email": "anonymous",
    "gsi1sk": "WORD#438",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "438",
    "date_submitted": "2022-02-15 05:45:18.740114",
    "word": "выходить",
    "sk": "BREAKDOWN",
    "pk": "WORD#438",
    "breakdown_items": [
        {"morpheme": "вы", "morpheme_family_id": "102", "position": "0", "morpheme_id": "218"},
        {"morpheme": "ход", "morpheme_family_id": "812", "position": "1", "morpheme_id": "1577"},
        {"morpheme": "ить", "morpheme_family_id": "1333", "position": "2", "morpheme_id": "2139"},
    ],
    "gsi1pk": "USER#anonymous",
    "is_verified": False,
    "is_inference": True,
    "gsi2pk": "WORD#438",
}


EXAMPLE_VERIFIED_BREAKDOWN = {
    "gsi2sk": "USER#eric.riddoch@gmail.com",
    "submitted_by_user_email": "eric.riddoch@gmail.com",
    "gsi1sk": "WORD#771",
    "date_verified": "2022-07-23 05:42:11.985578",
    "__type": "BREAKDOWN",
    "word_id": "771",
    "date_submitted": "2022-02-15 09:00:24.068323",
    "word": "выглядеть",
    "sk": "BREAKDOWN",
    "pk": "WORD#771",
    "breakdown_items": [
        {"morpheme": "вы", "morpheme_family_id": "1401", "position": "0", "morpheme_id": "2213"},
        {"morpheme": "гляд", "morpheme_family_id": "127", "position": "1", "morpheme_id": "276"},
        {"morpheme": "еть", "morpheme_family_id": "1324", "position": "2", "morpheme_id": "2130"},
    ],
    "gsi1pk": "USER#eric.riddoch@gmail.com",
    "is_verified": True,
    "is_inference": False,
    "gsi2pk": "WORD#771",
}


EXAMPLE_NON_VERIFIED_BREAKDOWN_SUBMITTED_BY_USER = {
    "gsi2sk": "USER#dmitriy.abaimov@bengroupinc.com",
    "submitted_by_user_email": "dmitriy.abaimov@bengroupinc.com",
    "gsi1sk": "WORD#59470",
    "date_verified": "None",
    "__type": "BREAKDOWN",
    "word_id": "59470",
    "date_submitted": "2022-02-23 15:38:30.049221",
    "word": "None",
    "sk": "BREAKDOWN",
    "pk": "WORD#59470",
    "breakdown_items": [
        {"morpheme": "само", "morpheme_family_id": "1107", "position": "0", "morpheme_id": "1892"},
        {"morpheme": "у", "morpheme_family_id": "1399", "position": "1", "morpheme_id": "2211"},
        {"morpheme": "со", "morpheme_family_id": "1403", "position": "2", "morpheme_id": "2219"},
        {"morpheme": "верш", "morpheme_family_id": "64", "position": "3", "morpheme_id": "124"},
        {"morpheme": "ен", "morpheme_family_id": None, "position": "4", "morpheme_id": None},
        {"morpheme": "ство", "morpheme_family_id": "1268", "position": "5", "morpheme_id": "2066"},
        {"morpheme": "ва", "morpheme_family_id": None, "position": "6", "morpheme_id": None},
        {"morpheme": "ни", "morpheme_family_id": None, "position": "7", "morpheme_id": None},
        {"morpheme": "е", "morpheme_family_id": "1189", "position": "8", "morpheme_id": "1985"},
    ],
    "gsi1pk": "USER#dmitriy.abaimov@bengroupinc.com",
    "is_verified": False,
    "is_inference": False,
    "gsi2pk": "WORD#59470",
}


###################
# Breakdown Items #
###################


EXAMPLE_BREAKDOWN_ITEM = {
    "submitted_by_user_email": "eric.riddoch@gmail.com",
    "breakdown_id": "77222",
    "morpheme_id": "2213",
    "gsi1sk": "BREAKDOWN#eric.riddoch@gmail.com",
    "__type": "BREAKDOWN_ITEM",
    "word_id": "771",
    "sk": "BREAKDOWN_ITEM#2213#0",
    "morpheme_family_id": "2213",
    "pk": "WORD#771",
    "position": 0,
    "morpheme": "вы",
    "gsi1pk": "MORPHEME_FAMILY#2213",
}


EXAMPLE_NULL_BREAKDOWN_ITEM = {
    "pk": "WORD#9203",
    "sk": "BREAKDOWN_ITEM#f4ef8326-a27e-4cb6-9cac-0089fc1eda45#8",
    "__type": "BREAKDOWN_ITEM_NULL",
    "word_id": "9203",
    "position": 8,
    "morpheme": "ся",
    "morpheme_id": None,
    "morpheme_family_id": None,
    "submitted_by_user_email": None,
}

#####################
# Morpheme Families #
#####################

EXAMPLE_MORPHEME_FAMILY_245 = {
    "morphemes": [{"morpheme": "знай", "morpheme_id": "510"}, {"morpheme": "зна", "morpheme_id": "511"}],
    "family_meanings": ["know"],
    "level": Decimal("1"),
    "__type": "MORPHEME_FAMILY",
    "sk": "MORPHEME_FAMILY#245",
    "word_pos": "any",
    "family_id": "245",
    "pk": "MORPHEME_FAMILY#245",
    "type": "root",
}


EXAMPLE_MORPHEME_FAMILY_1304 = {
    "morphemes": [
        {"morpheme": "ать", "morpheme_id": "2105"},
        {"morpheme": "ывать", "morpheme_id": "2106"},
        {"morpheme": "ивать", "morpheme_id": "2107"},
    ],
    "family_meanings": [None],
    "level": Decimal("6"),
    "__type": "MORPHEME_FAMILY",
    "sk": "MORPHEME_FAMILY#1304",
    "word_pos": "verb",
    "family_id": "1304",
    "pk": "MORPHEME_FAMILY#1304",
    "type": "suffix",
}


EXAMPLE_MORPHEME_FAMILY_1385 = {
    "morphemes": [{"morpheme": "ть", "morpheme_id": "2196"}],
    "family_meanings": [None],
    "level": Decimal("6"),
    "__type": "MORPHEME_FAMILY",
    "sk": "MORPHEME_FAMILY#1385",
    "word_pos": "verb",
    "family_id": "1385",
    "pk": "MORPHEME_FAMILY#1385",
    "type": "suffix",
}


#############
# Morphemes #
#############

EXAMPLE_MORPHEME_W_ID_2105 = {
    "morpheme_id": "2105",
    "gsi1sk": "MORPHEME#2105",
    "__type": "MORPHEME",
    "sk": "MORPHEME#2105",
    "family_id": "1304",
    "pk": "MORPHEME_FAMILY#1304",
    "morpheme": "ать",
    "gsi1pk": "MORPHEME#2105",
}


EXAMPLE_MORPHEME_W_ID_1776 = {
    "morpheme_id": "1776",
    "gsi1sk": "MORPHEME#1776",
    "__type": "MORPHEME",
    "sk": "MORPHEME#1776",
    "family_id": "934",
    "pk": "MORPHEME_FAMILY#934",
    "morpheme": "бы",
    "gsi1pk": "MORPHEME#1776",
}

########
# Word #
########

EXAMPLE_WORD_W_ID_7 = {
    "definitions": [
        {
            "pos": "verb",
            "definitions": [
                {
                    "sub_defs": [
                        {
                            "definition": "be",
                            "notes": None,
                            "sub_def_position": Decimal("1"),
                            "sub_def_id": Decimal("96"),
                        },
                        {
                            "definition": "happen",
                            "notes": None,
                            "sub_def_position": Decimal("2"),
                            "sub_def_id": Decimal("97"),
                        },
                        {
                            "definition": "(would you) please",
                            "notes": None,
                            "sub_def_position": Decimal("3"),
                            "sub_def_id": Decimal("98"),
                        },
                        {
                            "definition": "will you be so kind",
                            "notes": None,
                            "sub_def_position": Decimal("4"),
                            "sub_def_id": Decimal("99"),
                        },
                        {
                            "definition": "more are coming (on the way)",
                            "notes": None,
                            "sub_def_position": Decimal("5"),
                            "sub_def_id": Decimal("100"),
                        },
                        {
                            "definition": "a piece of a churchyard fits everybody",
                            "notes": None,
                            "sub_def_position": Decimal("6"),
                            "sub_def_id": Decimal("101"),
                        },
                        {
                            "definition": "All face one way",
                            "notes": None,
                            "sub_def_position": Decimal("7"),
                            "sub_def_id": Decimal("102"),
                        },
                    ],
                    "def_position": Decimal("1"),
                    "definition_id": Decimal("95"),
                }
            ],
        }
    ],
    "conjugations": {
        "1st_per_pl": "бу'дем",
        "past_pl": "бы'ли",
        "1st_per_sing": "бу'ду",
        "3rd_per_sing": "бу'дет",
        "past_n": "бы'ло",
        "actv_past_part": "бы'вший",
        "past_m": "был",
        "actv_part": "бы'вший",
        "past_f": "была'",
        "2nd_per_sing": "бу'дешь",
        "aspect": "impf",
        "impr": "будь",
        "pass_part": None,
        "pass_past_part": None,
        "3rd_per_pl": "бу'дут",
        "impr_pl": "бу'дьте",
        "2nd_per_pl": "бу'дете",
        "gerund": "бу'дучи",
    },
    "aspectual_pairs": [
        {"imp_accent": "быть", "pfv_word_id": None, "pfv_accent": None, "imp_word_id": Decimal("7")}
    ],
    "__type": "WORD",
    "sk": "WORD#7",
    "pk": "WORD#7",
    "word": {"word_id": "7", "word": "быть", "accent": "быть", "pos": "verb", "frequency": Decimal("7")},
    "sentences": [
        {"rus": "Быть не может.", "exact_match": True, "eng": "That's impossible."},
        {"rus": "Быть значит поступать.", "exact_match": True, "eng": "To be is to do."},
        {"rus": "Каково быть замужем?", "exact_match": True, "eng": "How does it feel being married?"},
        {"rus": "Должно быть весело.", "exact_match": True, "eng": "It should be fun."},
        {"rus": "Должно быть весело.", "exact_match": True, "eng": "That must be fun."},
        {"rus": "Может быть.", "exact_match": True, "eng": "It may be."},
        {"rus": "Не может быть!", "exact_match": True, "eng": "This is impossible!"},
        {"rus": "Не может быть!", "exact_match": True, "eng": "This can't be!"},
        {"rus": "Не может быть!", "exact_match": True, "eng": "Unbelievable!"},
        {"rus": "Хочешь быть богатым?", "exact_match": True, "eng": "Do you want to be rich?"},
        {"rus": "Хорошо быть дома.", "exact_match": True, "eng": "It's nice to be home."},
        {"rus": "Быть не может.", "exact_match": True, "eng": "That can't be."},
        {"rus": "Бытие определяет сознание.", "exact_match": False, "eng": "Being determines consciousness."},
    ],
}


EXAMPLE_WORD_W_ID_18 = {
    "definitions": [
        {
            "pos": "pronoun",
            "definitions": [
                {
                    "sub_defs": [
                        {
                            "definition": "they",
                            "notes": "пред. - них",
                            "sub_def_position": Decimal("1"),
                            "sub_def_id": Decimal("215"),
                        },
                        {
                            "definition": "them",
                            "notes": None,
                            "sub_def_position": Decimal("2"),
                            "sub_def_id": Decimal("216"),
                        },
                    ],
                    "def_position": Decimal("1"),
                    "definition_id": Decimal("214"),
                }
            ],
        }
    ],
    "__type": "WORD",
    "sk": "WORD#18",
    "pk": "WORD#18",
    "word": {"word_id": "18", "word": "они", "accent": "они'", "pos": "pronoun", "frequency": Decimal("18")},
    "sentences": [
        {"rus": "Они?", "exact_match": True, "eng": "They are?"},
        {"rus": "Они — борцы.", "exact_match": True, "eng": "They are wrestlers."},
        {"rus": "Они поженились.", "exact_match": True, "eng": "They got married."},
        {"rus": "Они поссорились.", "exact_match": True, "eng": "They had an argument."},
        {"rus": "Где они?", "exact_match": True, "eng": "Where are they?"},
        {"rus": "Они болтают.", "exact_match": True, "eng": "They are having a chat."},
        {"rus": "Они друзья?", "exact_match": True, "eng": "Are they friends?"},
        {"rus": "Они ровесники.", "exact_match": True, "eng": "They are the same age."},
        {"rus": "Они бегут.", "exact_match": True, "eng": "They run."},
        {"rus": "Они христиане.", "exact_match": True, "eng": "They are Christians."},
    ],
}


EXAMPLE_WORD_W_ID_50 = {
    "definitions": [
        {
            "pos": "verb",
            "definitions": [
                {
                    "sub_defs": [
                        {
                            "definition": "say, tell",
                            "notes": None,
                            "sub_def_position": Decimal("1"),
                            "sub_def_id": Decimal("477"),
                        },
                        {
                            "definition": "speak, talk",
                            "notes": None,
                            "sub_def_position": Decimal("2"),
                            "sub_def_id": Decimal("478"),
                        },
                        {
                            "definition": "I must say",
                            "notes": None,
                            "sub_def_position": Decimal("3"),
                            "sub_def_id": Decimal("479"),
                        },
                        {
                            "definition": "as a matter of fact",
                            "notes": None,
                            "sub_def_position": Decimal("4"),
                            "sub_def_id": Decimal("480"),
                        },
                        {
                            "definition": "not to mention",
                            "notes": None,
                            "sub_def_position": Decimal("5"),
                            "sub_def_id": Decimal("481"),
                        },
                        {
                            "definition": "well, I never (did)",
                            "notes": None,
                            "sub_def_position": Decimal("6"),
                            "sub_def_id": Decimal("482"),
                        },
                    ],
                    "def_position": Decimal("1"),
                    "definition_id": Decimal("476"),
                }
            ],
        }
    ],
    "conjugations": {
        "1st_per_pl": "ска'жем",
        "past_pl": "сказа'ли",
        "1st_per_sing": "скажу'",
        "3rd_per_sing": "ска'жет",
        "past_n": "сказа'ло",
        "actv_past_part": "сказа'вший",
        "past_m": "сказа'л",
        "actv_part": None,
        "past_f": "сказа'ла",
        "2nd_per_sing": "ска'жешь",
        "aspect": "perf",
        "impr": "скажи'",
        "pass_part": None,
        "pass_past_part": "ска'занный",
        "3rd_per_pl": "ска'жут",
        "impr_pl": "скажи'те",
        "2nd_per_pl": "ска'жете",
        "gerund": "сказа'в",
    },
    "aspectual_pairs": [
        {
            "imp_accent": "говори'ть",
            "pfv_word_id": Decimal("50"),
            "pfv_accent": "сказа'ть",
            "imp_word_id": Decimal("55"),
        },
        {
            "imp_accent": "ска'зывать",
            "pfv_word_id": Decimal("50"),
            "pfv_accent": "сказа'ть",
            "imp_word_id": Decimal("16029"),
        },
    ],
    "__type": "WORD",
    "sk": "WORD#50",
    "pk": "WORD#50",
    "word": {
        "word_id": "50",
        "word": "сказать",
        "accent": "сказа'ть",
        "pos": "verb",
        "frequency": Decimal("50"),
    },
    "sentences": [
        {"rus": "Сказать?", "exact_match": True, "eng": "Should I tell?"},
        {"rus": "Как сказать... ?", "exact_match": True, "eng": "How do you say...?"},
        {"rus": "Сказать ему?", "exact_match": True, "eng": "Should I tell him?"},
        {"rus": "Сказать ему?", "exact_match": True, "eng": "Ought I to tell it to him?"},
        {"rus": "Дай сказать.", "exact_match": True, "eng": "Let me speak."},
        {"rus": "Дайте сказать.", "exact_match": True, "eng": "Let me talk."},
        {"rus": "Сложно сказать.", "exact_match": True, "eng": "It's hard to say."},
        {"rus": "Сказано — сделано.", "exact_match": False, "eng": "No sooner said than done."},
        {"rus": "Сказано — сделано.", "exact_match": False, "eng": "Immediately said, immediately done."},
        {"rus": "Отлично сказано!", "exact_match": False, "eng": "Well said!"},
        {"rus": "Вам сказали.", "exact_match": False, "eng": "You've been told."},
    ],
}


#########
# Users #
#########

ADMIN_USER = {
    "pk": "USER#eric.riddoch@gmail.com",
    "sk": "USER#eric.riddoch@gmail.com",
    "email": "eric.riddoch@gmail.com",
    "is_admin": True,
}

NON_ADMIN_USER = {
    "pk": "USER#dmitriy.abaimov@bengroupinc.com",
    "sk": "USER#dmitriy.abaimov@bengroupinc.com",
    "email": "dmitriy.abaimov@bengroupinc.com",
    "is_admin": False,
}

TEST_USER_NOT_AS_ADMIN = {
    "pk": "USER#email@gmail.com",
    "sk": "USER#email@gmail.com",
    "email": "email@gmail.com",
    "is_admin": False,
}

TEST_USER_AS_ADMIN = {
    "pk": "USER#super_user@batcave.com",
    "sk": "USER#super_user@batcave.com",
    "email": "super_user@batcave.com",
    "is_admin": True,
}


####################
# User Submissions #
####################

EXAMPLE_USER_SUBMISSION_REPLACING_CURRENT_BREAKDOWN = {
    "word_id": 7,
    "breakdown_items": [
        {"morpheme_id": 1776, "position": 0},
        {"morpheme": "ть", "position": 1, "morpheme_id": None},
    ],
}


EXAMPLE_SUCCESSFUL_BREAKDOWN_SUBMISSION = {
    "word_id": 50,
    "breakdown_items": [
        {"morpheme": "сказ", "position": 0, "morpheme_id": None},
        {"morpheme_id": 2105, "position": 1},
    ],
}


EXAMPLE_BREAKDOWN_DOESNT_ADD_UP = {
    "word_id": 50,
    "breakdown_items": [
        {"morpheme": "сказe", "position": 0, "morpheme_id": None},
        {"morpheme_id": 2105, "position": 1},
    ],
}


EXAMPLE_SUCCESSFUL_BREAKDOWN_W_ALL_NULL_BREAKDOWN_ITEMS = {
    "word_id": 18,
    "breakdown_items": [
        {"morpheme": "он", "position": 0, "morpheme_id": None},
        {"morpheme": "и", "position": 1, "morpheme_id": None},
    ],
}


EXAMPLE_USER_SUBMISSION_MISSING_MORPHEME_IDS = {
    "word_id": 438,
    "breakdown_items": [
        {"position": 0, "morpheme_id": 218},
        {"position": 1, "morpheme_id": 1577},
        {"position": 2, "morpheme_id": 2139},
    ],
}


EXAMPLE_USER_SUBMISSION_MISSING_WORD = {
    "word_id": 150,
    "breakdown_items": [{"morpheme": "именно", "position": 0, "morpheme_id": None}],
}


#################
# Seed Database #
#################

EXAMPLE_DATA = [
    # Hand-crafted/Modified examples for testing
    EXAMPLE_BREAKDOWN,
    EXAMPLE_BREAKDOWN_2,
    EXAMPLE_BREAKDOWN_ANOTHER_USER,
    EXAMPLE_BREAKDOWN_ANOTHER_USER_2,
    EXAMPLE_BREAKDOWN_ERIC_USER,
    # Offical Beakdown Examples based on real data
    EXAMPLE_BREAKDOWN_W_NULL_AND_NON_NULL_BREAKDOWN_ITEMS_IN_DB,  # inferenced example
    EXAMPLE_BREAKDOWN_W_ALL_NULL_BREAKDOWN_ITEMS,  # inferenced example with all null breakdown items
    EXAMPLE_BREAKDOWN_W_NO_NULL_BREAKDOWN_ITEMS,  # inferenced example with no null breakdown items
    EXAMPLE_BREAKDOWN_W_MORPHEME_FAMILIES_IN_DB,  # inferenced example with duplicate breakdown_items
    EXAMPLE_VERIFIED_BREAKDOWN,  # Verified example by user eric.riddoch@gmail.com
    EXAMPLE_NON_VERIFIED_BREAKDOWN_SUBMITTED_BY_USER,  # Non-verified example by user dmitriy.abaimov@bengroupinc.com
    # User Submitted Breakdown Examples
    EXAMPLE_USER_SUBMITTED_BREAKDOWN,
    # Breakdown Items
    EXAMPLE_BREAKDOWN_ITEM,
    EXAMPLE_NULL_BREAKDOWN_ITEM,
    # Morpheme Families
    EXAMPLE_MORPHEME_FAMILY_245,
    EXAMPLE_MORPHEME_FAMILY_1304,
    EXAMPLE_MORPHEME_FAMILY_1385,
    # Morphemes
    EXAMPLE_MORPHEME_W_ID_2105,
    EXAMPLE_MORPHEME_W_ID_1776,
    # Words
    EXAMPLE_WORD_W_ID_7,
    EXAMPLE_WORD_W_ID_18,
    EXAMPLE_WORD_W_ID_50,
    # Users
    ADMIN_USER,
    NON_ADMIN_USER,
    TEST_USER_NOT_AS_ADMIN,
    TEST_USER_AS_ADMIN,
]


USER_SUBMISSION_DATA = [
    EXAMPLE_USER_SUBMISSION_REPLACING_CURRENT_BREAKDOWN,
    EXAMPLE_SUCCESSFUL_BREAKDOWN_SUBMISSION,
    EXAMPLE_BREAKDOWN_DOESNT_ADD_UP,
    EXAMPLE_SUCCESSFUL_BREAKDOWN_W_ALL_NULL_BREAKDOWN_ITEMS,
    EXAMPLE_USER_SUBMISSION_MISSING_MORPHEME_IDS,
    EXAMPLE_USER_SUBMISSION_MISSING_WORD,
]


# Helper Function
def seed_data(rootski_dynamo_table: _Table) -> None:
    for data in EXAMPLE_DATA:
        rootski_dynamo_table.put_item(Item=data)


if __name__ == "__main__":
    from rootski.services.database.dynamo.db_service import DBService

    db: DBService = DBService("rootski-table")
    db.init()
    table = db.rootski_table
    # get_item_response = table.get_item(Key={"pk": "MORPHEME_FAMILY#934", "sk": "MORPHEME#1776"})
    get_item_response = table.get_item(Key={"pk": "WORD#150", "sk": "WORD#150"})
    print(get_item_response["Item"])
