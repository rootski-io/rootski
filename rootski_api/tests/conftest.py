"""Specify fixtures and constants used during pytest tests."""

import sys
from pathlib import Path

from dotenv import load_dotenv

THIS_DIR = Path(__file__).parent
sys.path.append(str(THIS_DIR))

DOT_ENV_FPATH = THIS_DIR / "resources" / "test.env"

# set contents of test.env as environment variables on the system;
# if they are already set on the system, they are not overridden
load_dotenv(dotenv_path=DOT_ENV_FPATH, override=False)

# Tell pytest where fixtures are located
# There should be single entry for each fixture (python) file in tests/fixtures
pytest_plugins = [
    "fixtures.general_fixtures",
    "fixtures.rootski_dynamo_table",
]
