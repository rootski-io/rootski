"""
Test units of the system that have no external dependencies.

For BEN-DE, unit tests are limited to tests that do not cross the network barrier of the
computer on which they are being executed.
"""

import sys
from pathlib import Path

# Added project to the system path to allow importing between test-categories
tests_path = Path(sys.path[0])
sys.path.append(str(tests_path.parent))
