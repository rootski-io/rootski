"""
Utility functions written using xonsh.
"""

def export_dot_env_vars(env_file):
    # export environment variables from .env; all ${VAR?default} type values
    # in the docker-compose.yml file will be interpolated with these values
    for line in $(cat @(env_file) | grep '=').splitlines():
        key, value = line.split("=")
        ${key} = value
