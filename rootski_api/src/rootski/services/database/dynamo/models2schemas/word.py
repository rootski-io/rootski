from typing import List, TypedDict, Union

import rootski.services.database.dynamo.models as dynamo
from rootski.schemas import word as schemas


class CommonWordSchemas(TypedDict):
    word: schemas.Word
    definitions: List[schemas.DefinitionForPOS]
    sentences: List[schemas.ExampleSentence]


def dynamo_to_pydantic__word(
    word: dynamo.Word,
) -> Union[schemas.WordResponse, schemas.AdjectiveResponse, schemas.NounResponse, schemas.VerbResponse]:

    common_word_fields = parse_common_word_schemas(word=word)

    if word.word_pos in ["noun", "pronoun"]:
        return schemas.NounResponse(
            declensions=schemas.NounDeclensions(**word.data["declensions"]),
            **common_word_fields,
        )

    if word.word_pos == "verb":
        return schemas.VerbResponse(
            aspectual_pairs=[schemas.VerbAspectualPair(**pair) for pair in word.data["aspectual_pairs"]],
            conjugations=schemas.VerbConjugations.parse_obj(word.data["conjugations"]),
            **common_word_fields,
        )

    if word.word_pos == "adjective":
        return schemas.AdjectiveResponse(
            short_forms=schemas.AdjectiveShortForms(**word.data["short_forms"]), **common_word_fields
        )

    return schemas.WordResponse(**common_word_fields)


def parse_common_word_schemas(word: dynamo.Word) -> CommonWordSchemas:
    word_ = schemas.Word(**word.data["word"])

    definitions = [
        schemas.DefinitionForPOS(
            pos=d["pos"],
            definitions=[
                schemas.Definition(
                    def_position=def_["def_position"],
                    definition_id=def_["definition_id"],
                    sub_defs=[
                        schemas.SubDefinition(
                            sub_def_id=sub_def["sub_def_id"],
                            notes=sub_def["notes"],
                            definition=sub_def["definition"],
                            sub_def_position=sub_def["sub_def_position"],
                        )
                        for sub_def in def_["sub_defs"]
                    ],
                )
                for def_ in d["definitions"]
            ],
        )
        for d in word.data["definitions"]
    ]

    sentences = [
        schemas.ExampleSentence(
            eng=s["eng"],
            rus=s["rus"],
            exact_match=s["exact_match"],
        )
        for s in word.data["sentences"]
    ]

    return {
        "word": word_,
        "definitions": definitions,
        "sentences": sentences,
    }
