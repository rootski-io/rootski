"""
Test components of the system that have external dependencies.

Functional tests mean different things for different organizations. For BEN-DE, functional tests
refer to those tests that require external dependencies or that my require a complex sequence
of operations.
"""

import sys
from pathlib import Path

# Added project to the system path to allow importing between test-categories
tests_path = Path(sys.path[0])
sys.path.append(str(tests_path.parent))
