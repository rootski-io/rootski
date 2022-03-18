"""
Utility functions written using xonsh.
"""

import os

def export_dot_env_vars(env_file):
    # export environment variables from .env; all ${VAR?default} type values
    # in the docker-compose.yml file will be interpolated with these values
    print(env_file)
    for line in $(cat @(env_file) | grep '=').splitlines():
        key, value = line.split("=")
        os.environ[key] = value
        ${key} = value
