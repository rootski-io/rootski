import os
from contextlib import contextmanager
from copy import deepcopy
from typing import Dict


@contextmanager
def scoped_env_vars(env_vars: Dict[str, str]) -> Dict[str, str]:
    """Temporarily set environment variables. Unset them when the context exits."""
    # save the current environment variables to put them back later
    current_env_vars: Dict[str, str] = dict(deepcopy(os.environ))
    try:
        os.environ.update(env_vars)
        # TODO remove this

        yield
    finally:
        for key in env_vars.keys():
            del os.environ[key]
    os.environ.update(current_env_vars)
