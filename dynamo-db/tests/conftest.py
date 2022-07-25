"""Specify fixtures and constants used during pytest tests."""

import sys
from pathlib import Path

THIS_DIR = Path(__file__)
TESTS_PARENT_DIR = THIS_DIR / ".."

sys.path.insert(0, str(TESTS_PARENT_DIR))

# Tell pytest where fixtures are located
# There should be single entry for each fixture (python) file in tests/fixtures
pytest_plugins = [
    "fixtures.rootski_dynamo_table",
]
