"""Helper functions used when the "alembic" CLI is executed."""

import os
import sys
from typing import Dict

from alembic.environment import EnvironmentContext


def get_conn_string_from_env_vars(confirm_url_with_user=True):
    """
    Retrieves the connection string for the desired environment and region.

    :param get_conn_string_from_env_vars: if ``True`` ask user if they wish to continue
        and exit with a nonzero status code they do not. This is useful for preventing
        any downstream operations against a database which would use the connection
        string provided by this function.
    """
    # build the database connection string from environment variables
    conn_string: str = "postgresql://{user}:{passwd}@{host}:{port}/{db}".format(
        user=os.environ["POSTGRES_USER"],
        passwd=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        db=os.environ["POSTGRES_DB"],
        port=os.environ["POSTGRES_PORT"],
    )

    # confirm with the user before returning
    if confirm_url_with_user:
        answer = input(f"[rootski] Using connection string: {conn_string}. Do you want to continue? (y/n)")
        if answer != "y":
            sys.exit(1)

    return conn_string


def get_x_arguments(context: EnvironmentContext) -> Dict[str, str]:
    """
    Parse "x-arguments" from calls to the alembic CLI.

    Extract a dictionary of key value arguments passed to alembic like this:

    .. code-block:: bash

        $ alembic -x env=local -x db=russian_db ... upgrade ae9813df

    :param context: the context variable created
        in the env.py script. It has information inside of it about the
        arguments passed into the "alembic" CLI tool.

    :return: dictionary of all the key-value x argument pairs
    """
    return context.get_x_argument(as_dictionary=True)
