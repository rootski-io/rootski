"""
Tests specifically for the purpose of user examples.

Example tests differ from most in that the target audience is the user. The unit of test for example tests
is an action. An action may consist of calling multiple methods in an attempt to show a complete usage
example.

These tests should be replete with comments describing what steps are being taken, why they are being taken,
and why the results are as they are.
"""

import sys
from pathlib import Path

# Added project to the system path to allow importing between test-categories
tests_path = Path(sys.path[0])
sys.path.append(str(tests_path.parent))
