"""
Xonsh script for gene
"""

import sys
import os
from pathlib import Path
from textwrap import dedent

from make_utils.utils_without_dependencies import get_localhost

# make tracebacks beautiful when errors occur 😃
from rich import traceback, print
traceback.install()

from make_utils.makefile import Makefile
from make_utils.utils_with_dependencies import log, MakeXshError

from migrations.utils.get_new_revision_id import get_new_revision_id


# import appears invalid because xsh_utils.xsh ends in the ".xsh" extension
from make_utils.xsh_utils import export_dot_env_vars

THIS_DIR = Path(__file__).parent.resolve().absolute()
ROOTSKI_ROOT_DIR = (THIS_DIR / "../../").resolve().absolute()
DEV_ENV_FILE_NAME = "dev.env"

CUSTOM_MAKE_TEXT = dedent("""
# install python dependencies needed to run database migrations;
# creating/activating a Python virtual environment is recommended!
install:
\t# install python dependencies needed to execute various makefile targets
\tpython -m pip install -e "../../make_utils"
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
    log("Enter a SHORT name describing the database migration (spaces are replaced with underscores):")
    migration_fname: str = input().strip().replace(" ", "_")
    new_revision_id: str = get_new_revision_id()

    # env var: specify location of alembic config file for the alembic CLI
    $ALEMBIC_CONFIG = str(THIS_DIR / "alembic.ini")

    cd ./src \
    && alembic revision \
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

    # export the env vars in rootski/dev.env
    export_dot_env_vars(env_file=str(ROOTSKI_ROOT_DIR / DEV_ENV_FILE_NAME))

    import os
    # export the correct version of localhost
    host = "localhost"
    $POSTGRES_HOST = host
    os.environ["POSTGRES_HOST"] = host

    # env var: specify location of alembic config file for the alembic CLI
    $ALEMBIC_CONFIG = str(THIS_DIR / "alembic.ini")

    # read connection string from environment variables and perform upgrade;
    # see the env.py file for information about how this is happening
    cd ./src \
    && alembic upgrade head


@makefile.target(tag="utils")
def print_dev_alembic_env_vars():
    """Print env var prefix for running alembic commands against the local dev database."""
    export_dot_env_vars(env_file=str(ROOTSKI_ROOT_DIR / DEV_ENV_FILE_NAME))

    dev_env_vars: str = "POSTRES_USER={user} POSTGRES_PASSWORD={passwd} POSTGRES_HOST={host} POSTGRES_PORT={port} POSTGRES_DB={db}".format(
        user=os.environ["POSTGRES_USER"],
        passwd=os.environ["POSTGRES_PASSWORD"],
        host="localhost",
        db=os.environ["POSTGRES_DB"],
        port=os.environ["POSTGRES_PORT"],
    )
    print(dev_env_vars)


if __name__ == "__main__":
    makefile.run()
