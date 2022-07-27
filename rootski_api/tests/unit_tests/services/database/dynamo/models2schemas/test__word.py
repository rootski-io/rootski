from rootski.services.database.dynamo.models import Word
from rootski.services.database.dynamo.models2schemas.word import dynamo_to_pydantic__word

from rootski import schemas

EXAMPLE_VERB = {
    "word": {"word_id": 2004, "word": "запретить", "accent": "запрети'ть", "pos": "verb", "frequency": 2004},
    "definitions": [
        {
            "pos": "verb",
            "definitions": [
                {
                    "def_position": 1,
                    "definition_id": 12149,
                    "sub_defs": [
                        {
                            "sub_def_id": 12150,
                            "sub_def_position": 1,
                            "definition": "forbid, prohibit, interdict, ban, outlaw",
                            "notes": None,
                        },
                        {
                            "sub_def_id": 12151,
                            "sub_def_position": 2,
                            "definition": "suppress",
                            "notes": "(публикацию)",
                        },
                    ],
                }
            ],
        }
    ],
    "sentences": [
        {
            "rus": "Книга, которую нужно запретить прежде всего, - это каталог запрещённых книг.",
            "eng": "A book which, above all others in the world, should be forbidden, is a catalogue of forbidden books.",
            "exact_match": True,
        },
        {
            "rus": "Львовский городской совет ещё раз обращает ваше внимание на ложную информацию относительно намерения запретить разговаривать во Львове по-русски.",
            "eng": "The Lvov city council is once more drawing attention to False information regarding the intention to ban speaking Russian in Lvov.",
            "exact_match": True,
        },
        {"rus": "Это надо запретить.", "eng": "That should be prohibited.", "exact_match": True},
        {
            "rus": "Нужно запретить рекламу, нацеленную на детей.",
            "eng": "We should ban advertising aimed towards children.",
            "exact_match": True,
        },
        {
            "rus": "Вам благословляется всё, что не в состоянии запретить церковь.",
            "eng": "What the church can't prohibit it blesses.",
            "exact_match": True,
        },
        {
            "rus": "Ему запретили заниматься медициной.",
            "eng": "He was banned from practising medicine.",
            "exact_match": False,
        },
        {"rus": "Эта тема здесь под запретом.", "eng": "The topic is taboo here.", "exact_match": False},
        {
            "rus": "Запрет никем не принимается всерьёз.",
            "eng": "Prohibition isn't taken seriously by anyone.",
            "exact_match": False,
        },
        {
            "rus": "Врачи запретили Тому дальние поездки.",
            "eng": "The doctors prohibited Tom from taking any long trips.",
            "exact_match": False,
        },
        {
            "rus": "Отец запретил мне заводить кота.",
            "eng": "My father forbade me from having a pet cat.",
            "exact_match": False,
        },
        {
            "rus": "Автостоп в Австралии под запретом?",
            "eng": "Is hitchhiking prohibited in Australia?",
            "exact_match": False,
        },
        {
            "rus": "Им запретили покидать отель.",
            "eng": "They were prohibited from leaving the hotel.",
            "exact_match": False,
        },
        {"rus": "Вы не запрете дверь?", "eng": "Would you please lock the door?", "exact_match": False},
    ],
    "conjugations": {
        "aspect": "perf",
        "1st_per_sing": "запрещу'",
        "2nd_per_sing": "запре'тишь",
        "3rd_per_sing": "запрети'т",
        "1st_per_pl": "запрети'м",
        "2nd_per_pl": "запрети'те",
        "3rd_per_pl": "запре'тят",
        "past_m": "запрети'л",
        "past_f": "запрети'ла",
        "past_n": "запрети'ло",
        "past_pl": "запрети'ли",
        "actv_part": None,
        "pass_part": None,
        "actv_past_part": "запрети'вший",
        "pass_past_part": "запрещённый",
        "gerund": "запрети'в",
        "impr": "запрети'",
        "impr_pl": "запрети'те",
    },
    "aspectual_pairs": [
        {"imp_word_id": 4674, "imp_accent": "запреща'ть", "pfv_word_id": 2004, "pfv_accent": "запрети'ть"}
    ],
}

EXAMPLE_ADVERB = {
    "word": {"word_id": 2005, "word": "жаль", "accent": "жаль", "pos": "adverb", "frequency": 2005},
    "definitions": [
        {
            "pos": "adverb",
            "definitions": [
                {
                    "def_position": 1,
                    "definition_id": 12152,
                    "sub_defs": [
                        {
                            "sub_def_id": 12153,
                            "sub_def_position": 1,
                            "definition": "be/feel sorry (for smb.)",
                            "notes": "(кого-л./что-л.)",
                        },
                        {"sub_def_id": 12154, "sub_def_position": 2, "definition": "pity", "notes": None},
                        {"sub_def_id": 12155, "sub_def_position": 3, "definition": "regret", "notes": None},
                    ],
                },
                {
                    "def_position": 2,
                    "definition_id": 12156,
                    "sub_defs": [
                        {
                            "sub_def_id": 12157,
                            "sub_def_position": 1,
                            "definition": "it is a pity",
                            "notes": "(прискорбно)",
                        }
                    ],
                },
                {
                    "def_position": 3,
                    "definition_id": 12158,
                    "sub_defs": [
                        {
                            "sub_def_id": 12159,
                            "sub_def_position": 1,
                            "definition": "grudge",
                            "notes": "(чего-л.; делать что-л.)",
                        }
                    ],
                },
            ],
        }
    ],
    "sentences": [
        {"rus": "Очень жаль.", "eng": "That's too bad.", "exact_match": True},
        {"rus": "Жаль.", "eng": "That's a shame.", "exact_match": True},
        {"rus": "Жаль.", "eng": "This is unfortunate.", "exact_match": True},
        {"rus": "Жаль...", "eng": "Pity...", "exact_match": True},
        {"rus": "Мне жаль!", "eng": "Sorry!", "exact_match": True},
        {"rus": "Мне жаль.", "eng": "I feel sorry.", "exact_match": True},
        {"rus": "Мне жаль.", "eng": "I apologize.", "exact_match": True},
        {"rus": "Мне жаль.", "eng": "Excuse me.", "exact_match": True},
        {"rus": "Нам жаль.", "eng": "We're sorry.", "exact_match": True},
        {"rus": "Тому жаль.", "eng": "Tom's sorry.", "exact_match": True},
        {"rus": "Не жалуйся.", "eng": "Don't complain.", "exact_match": False},
        {"rus": "Кто жалуется?", "eng": "Who's complaining?", "exact_match": False},
    ],
}

EXAMPLE_NOUN = {
    "word": {"word_id": 2006, "word": "демократия", "accent": "демокра'тия", "pos": "noun", "frequency": 2006},
    "definitions": [
        {
            "pos": "noun",
            "definitions": [
                {
                    "def_position": 1,
                    "definition_id": 12160,
                    "sub_defs": [
                        {"sub_def_id": 12161, "sub_def_position": 1, "definition": "democracy", "notes": None}
                    ],
                }
            ],
        }
    ],
    "sentences": [
        {
            "rus": "В Испании демократия с 1975 года.",
            "eng": "Spain has been a democracy since 1975.",
            "exact_match": True,
        },
        {
            "rus": "Представительная демократия — это одна из форм государственной власти.",
            "eng": "Representative democracy is one form of government.",
            "exact_match": True,
        },
        {
            "rus": "Демократия — наихудшая форма правления, если не считать всех остальных.",
            "eng": "Democracy is the worst form of government, except all the others that have been tried.",
            "exact_match": True,
        },
        {
            "rus": "Демократия — это форма правления.",
            "eng": "Democracy is one form of government.",
            "exact_match": True,
        },
        {
            "rus": "Демократия - это диктатура большинства.",
            "eng": "Democracy is the dictatorship of the majority.",
            "exact_match": True,
        },
        {
            "rus": "Когда возникла демократия?",
            "eng": "When did Democracy come into existence?",
            "exact_match": True,
        },
        {
            "rus": "Германия - парламентская демократия.",
            "eng": "Germany is a parliamentary democracy.",
            "exact_match": True,
        },
        {"rus": "Демократия поощряет свободу.", "eng": "Democracy encourages freedom.", "exact_match": True},
        {
            "rus": "Демократия возникла в Древней Греции.",
            "eng": "Democracy originated in Ancient Greece.",
            "exact_match": True,
        },
        {"rus": "Мы защищаем демократию.", "eng": "We stand for democracy.", "exact_match": False},
        {"rus": "Я демократ.", "eng": "I'm a democrat.", "exact_match": False},
        {"rus": "Он убеждённый демократ.", "eng": "He is heart and soul a Democrat.", "exact_match": False},
        {"rus": "Том демократ.", "eng": "Tom is a democrat.", "exact_match": False},
    ],
    "declensions": {
        "gender": "f",
        "animate": False,
        "indeclinable": False,
        "nom": "демокра'тия",
        "acc": "демокра'тию",
        "prep": "демокра'тии",
        "gen": "демокра'тии",
        "dat": "демокра'тии",
        "inst": "демокра'тией",
        "nom_pl": "демокра'тии",
        "acc_pl": "демокра'тии",
        "prep_pl": "демокра'тиях",
        "gen_pl": "демокра'тий",
        "dat_pl": "демокра'тиям",
        "inst_pl": "демокра'тиями",
    },
}

EXAMPLE_ADJECTIVE = {
    "word": {"word_id": 2017, "word": "судебный", "accent": "суде'бный", "pos": "adjective", "frequency": 2017},
    "definitions": [
        {
            "pos": "adjective",
            "definitions": [
                {
                    "def_position": 1,
                    "definition_id": 12208,
                    "sub_defs": [
                        {
                            "sub_def_id": 12209,
                            "sub_def_position": 1,
                            "definition": "judicial, legal, forensic",
                            "notes": None,
                        },
                        {"sub_def_id": 12210, "sub_def_position": 2, "definition": "law", "notes": None},
                        {"sub_def_id": 12211, "sub_def_position": 3, "definition": "court", "notes": None},
                        {"sub_def_id": 12212, "sub_def_position": 4, "definition": "coroner", "notes": None},
                    ],
                }
            ],
        }
    ],
    "sentences": [
        {
            "rus": "Расклеивание рекламы запрещено. Нарушители будут преследоваться в судебном порядке.",
            "eng": "Bill posting prohibited. Offenders will be prosecuted.",
            "exact_match": False,
        },
        {
            "rus": "Судебно-медицинский эксперт не обнаружил огнестрельных ранений ни у одного из трупов.",
            "eng": "The coroner didn't find any gunshot wounds on any of the bodies.",
            "exact_match": False,
        },
        {
            "rus": "В США просто потрясающая судебная система и пресса: сегодня ты являешь собой пример бедной домохозяйки, жертвы изнасилования, а завтра ты нелегальная мигрантка, совершившая лжесвидетельство и подозреваемая в отмывании денег, связанных с наркоторговлей.",
            "eng": "The US judicial system and press are incredible: One day you're a poor examplary housewife, victim of a rape, the next, you're an illegal immigrant, having committed perjury and being suspected of whitewashing drug money.",
            "exact_match": False,
        },
        {
            "rus": 'Слово "okazo" изначально значило на эсперанто как "то, что случается", так и "конкретное происшествие" - так же, как русское "случай", а "kazo" значило лишь "падеж в склонении". Под западным влиянием "kazo" стало значить "судебное дело", а потом и "случай вообще".',
            "eng": "The Esperanto word ‘okazo’ originally meant both ‘occasion’ and ‘case’, as the Russian ‘случай’ does, while ‘kazo’ only meant ‘case in declension’. Owing to Western influence, ‘kazo’ started to mean ‘case in court’, then ‘case in general’.",
            "exact_match": False,
        },
        {
            "rus": "Правительство США имеет три ветви власти: исполнительную, законодательную и судебную.",
            "eng": "The U.S. government has three branches: the executive, the legislative, and the judicial.",
            "exact_match": False,
        },
        {
            "rus": "Мне нужно судебное дело, составленное по этому материалу.",
            "eng": "I want a suit made of this material.",
            "exact_match": False,
        },
        {
            "rus": "Я предпочту любую альтернативу судебному процессу.",
            "eng": "I would prefer any alternative to a lawsuit.",
            "exact_match": False,
        },
        {
            "rus": "Вы когда-нибудь выступали свидетелем на судебном процессе?",
            "eng": "Have you ever been a witness in a court case?",
            "exact_match": False,
        },
        {
            "rus": "Я не имею никакого понятия о судебной процедуре.",
            "eng": "I have no acquaintance with court procedure.",
            "exact_match": False,
        },
        {
            "rus": "Татоэба вдохновила Мэри, известного судебного психолога, на написание романа о Томе, серийном убийце из Бостона.",
            "eng": "Mary, the famous forensic psychologist and writer, was inspired by Tatoeba to write a novel about Tom, the serial killer from Boston.",
            "exact_match": False,
        },
    ],
    "short_forms": {
        "comp": "суде'бнее",
        "fem_short": "суде'бна",
        "masc_short": "суде'бен",
        "neut_short": "суде'бно",
        "plural_short": "суде'бны",
    },
}


def test__dynamo_to_pydantic__word__verb():
    verb = Word(data=EXAMPLE_VERB)
    verb_response: schemas.VerbResponse = dynamo_to_pydantic__word(word=verb)
    assert type(verb_response) is schemas.VerbResponse

    verb_response_dict = verb_response.dict(by_alias=True)
    assert all(field in verb_response_dict.keys() for field in ["aspectual_pairs", "conjugations"])


def test__dynamo_to_pydantic__word__noun():
    noun = Word(data=EXAMPLE_NOUN)
    noun_response: schemas.NounResponse = dynamo_to_pydantic__word(word=noun)
    assert type(noun_response) is schemas.NounResponse

    noun_response_dict = noun_response.dict(by_alias=True)
    assert all(field in noun_response_dict.keys() for field in ["declensions"])


def test__dynamo_to_pydantic__word__adjective():
    adjective = Word(data=EXAMPLE_ADJECTIVE)
    adjective_response: schemas.AdjectiveResponse = dynamo_to_pydantic__word(word=adjective)
    assert type(adjective_response) is schemas.AdjectiveResponse

    adjective_response_dict = adjective_response.dict(by_alias=True)
    assert all(field in adjective_response_dict.keys() for field in ["short_forms"])


def test__dynamo_to_pydantic__word__adverb():
    adverb = Word(data=EXAMPLE_ADVERB)
    adverb_response: schemas.WordResponse = dynamo_to_pydantic__word(word=adverb)
    assert type(adverb_response) is schemas.WordResponse

    adverb_response_dict = adverb_response.dict(by_alias=True)
    assert all(
        field not in adverb_response_dict.keys()
        for field in ["aspectual_pairs", "conjugations", "declensions", "short_forms"]
    )
