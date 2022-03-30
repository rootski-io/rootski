"""
Xonsh script for gene
"""

import sys
import os
from pathlib import Path
from textwrap import dedent
from typing import Optional

from make_utils.utils_without_dependencies import get_localhost

# make tracebacks beautiful when errors occur 😃
from rich import traceback, print
traceback.install()

from make_utils.makefile import Makefile
from make_utils.utils_with_dependencies import log, MakeXshError


# import appears invalid because xsh_utils.xsh ends in the ".xsh" extension
from make_utils.xsh_utils import export_dot_env_vars

THIS_DIR = Path(__file__).parent.resolve().absolute()
ROOTSKI_ROOT_DIR = (THIS_DIR / "../").resolve().absolute()
DEV_ENV_FILE_NAME = "dev.env"

CUSTOM_MAKE_TEXT = dedent("""
# install python dependencies needed to run database migrations;
# creating/activating a Python virtual environment is recommended!
install:
\t# install python dependencies needed to execute various makefile targets
\tpython -m pip install -e "../make_utils"
\tpython -m pip install -e .
""")

# use this to turn python functions into makefile targets
makefile = Makefile(
    makefile_script_fname="make.xsh",
    makefile_fpath=THIS_DIR / "Makefile",
    help_message_extra="",
    makefile_header=CUSTOM_MAKE_TEXT
)

@makefile.target(tag="creating migrations")
def create_migration_file():
    """
    Use the 'alembic' CLI to create a blank '.py' file that can be used
    to define logic for a change to the rootski database schema.

    [blue]Note[/blue]: you need to have 'alembic' and other dependencies
        installed for this to run. Run 'make install' to install those 😉.
    """
    from migrations.utils.get_new_revision_id import get_new_revision_id

    log("Enter a SHORT name describing the database migration (spaces are replaced with underscores):")
    migration_fname: str = input().strip().replace(" ", "_")
    new_revision_id: str = get_new_revision_id()
    alembic_config_fpath: str = str(THIS_DIR / "alembic.ini")

    cd ./src \
    && alembic \
        --config @(alembic_config_fpath) \
        revision \
        -m @(migration_fname) \
        --rev-id @(new_revision_id)


@makefile.target(tag="running migrations")
def run_all_migrations_from_current__dev():
    """
    Attempt to run all of the "alembic" migrations against a database
    starting from whichever migration the database is currently on.

    You can find the current alembic revision that a database is on
    by looking for an "alembic_version" table. If the table doesn't exist
    in the database, no revisions have been run.

    The connection information for the database will be taken from
    the "rootski/dev.env" file.
    """
    localhost = "localhost"
    run_all_alembic_migrations(
        db_host=localhost,
        env_file_fpath=ROOTSKI_ROOT_DIR / DEV_ENV_FILE_NAME
    )


@makefile.target(tag="utils")
def build_image():
    """Build the docker image for running database migrations."""
    docker build -t rootski/database-migrations @(str(THIS_DIR))



@makefile.target(tag="running migrations")
def run_all_migrations_from_current__dev__docker():
    """
    Execute the database migrations using docker.
    """
    log("Using dev.env vars to connect to a local database")
    export_dot_env_vars(env_file=str(ROOTSKI_ROOT_DIR / DEV_ENV_FILE_NAME))
    localhost: str = get_localhost()

    log("Executing database migrations...")
    docker run --rm -it \
        -v @(str(THIS_DIR)):/migrations \
        -e CONFIRM_CONNECTION_STRING_WITH_USER=true \
        -e POSTGRES_USER=$POSTGRES_USER \
        -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
        -e POSTGRES_DB=$POSTGRES_DB \
        -e POSTGRES_PORT=$POSTGRES_PORT \
        -e POSTGRES_HOST=@(localhost) \
        rootski/database-migrations --config ../alembic.ini upgrade head


@makefile.target(tag="utils")
def print_dev_alembic_env_vars():
    """
    Print env var prefix for running alembic commands against the local dev database.

    The idea is that you could use the string printed to the console to execute
    alembic commands against a local database like this:

    .. code-block:: bash

        cd rootski_api/migrations/src
        POSTGRES_USER=rootski \\
            POSTGRES_PASSWORD=pass \\
            POSTGRES_HOST=localhost \\
            POSTGRES_PORT=5432 \\
            POSTGRES_DB=rootski_db \\
            alembic --config ../alembic.ini <some subcommand> [ARGS]

    .. code-block:: bash

        POSTGRES_USER=rootski POSTGRES_PASSWORD=pass POSTGRES_HOST=localhost POSTGRES_PORT=5432 POSTGRES_DB=rootski_db alembic --config ../alembic.ini
    """
    export_dot_env_vars(env_file=str(ROOTSKI_ROOT_DIR / DEV_ENV_FILE_NAME))

    dev_env_vars: str = "POSTGRES_USER={user} POSTGRES_PASSWORD={passwd} POSTGRES_HOST={host} POSTGRES_PORT={port} POSTGRES_DB={db}".format(
        user=os.environ["POSTGRES_USER"],
        passwd=os.environ["POSTGRES_PASSWORD"],
        host="localhost",
        db=os.environ["POSTGRES_DB"],
        port=os.environ["POSTGRES_PORT"],
    )
    print(dev_env_vars)


def run_all_alembic_migrations(db_host, env_file_fpath):

    if not env_file_fpath:
        env_file_fpath = ROOTSKI_ROOT_DIR / DEV_ENV_FILE_NAME

    # export the env vars in rootski/dev.env
    export_dot_env_vars(env_file=str(env_file_fpath))

    # export the correct version of localhost
    $POSTGRES_HOST = db_host
    os.environ["POSTGRES_HOST"] = db_host

    # read connection string from environment variables and perform upgrade;
    # see the env.py file for information about how this is happening
    cd ./src \
    && alembic \
        --config @(str(THIS_DIR / "alembic.ini")) \
        upgrade head || MakeXshError("Failed to execute migrations")

if __name__ == "__main__":
    makefile.run()
