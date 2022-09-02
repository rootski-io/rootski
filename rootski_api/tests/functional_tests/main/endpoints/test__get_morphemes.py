from typing import Dict
import pytest
from starlette.testclient import TestClient


@pytest.mark.parametrize(["disable_auth", "act_as_admin"], [(True, False)])
def test__get_morphemees_json(
    dynamo_client: TestClient,
):
    response = dynamo_client.get("/morpheme/morphemes.json")
    morphemes_json: Dict[str, dict] = response.json()
    for key_index, morpheme_data in morphemes_json.items():
        {"morpheme_id", "morpheme", "type", "word_pos", "family_id", "meanings", "level", "family"}.issubset(
            morpheme_data.keys()
        )
