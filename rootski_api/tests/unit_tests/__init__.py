"""Test units of the system that have no external dependencies."""

import sys
from pathlib import Path

# Added project to the system path to allow importing between test-categories
tests_path = Path(sys.path[0])
sys.path.append(str(tests_path.parent))
