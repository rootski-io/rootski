from typing import Any, Dict, List

from pydantic import BaseModel

from rootski.main.endpoints.breakdown.errors import (
    PARTS_DONT_SUM_TO_WHOLE_WORD_MSG,
    DuplicateExampleTitle,
)


class ExampleResponse(BaseModel):
    title: str
    body: Dict[str, Any]  # jsonable dict


def make_apidocs_responses_obj(examples: List[ExampleResponse]):
    """
    Return a dictionary used to document the possible responses
    for a single HTTP status code.
    """
    swagger_example_responses_obj = {
        "content": {
            "application/json": {
                "examples": {
                    # "Invalid breakdown": {
                    #     "value": {
                    #         "detail": PARTS_DONT_SUM_TO_WHOLE_WORD_MSG.format(
                    #             submitted_breakdown="при-каз-ывать", word="приказать"
                    #         )
                    #     }
                    # }
                }
            }
        }
    }
    for example_response in examples:
        examples = swagger_example_responses_obj["content"]["application/json"]["examples"]
        if example_response.title in examples.keys():
            raise DuplicateExampleTitle(
                f"Example response title {example_response.title} appears twice for this endpoint."
            )
        examples[example_response.title] = {
            "value": example_response.body,
        }

    return swagger_example_responses_obj
