# pylint: disable=invalid-name
"""
This script is a configuration file for ``alembic``.

This script executes at the beginning of all ``alembic`` commands.
Some reasons to modify this script include:

- doing something with custom ``alembic`` arguments (x-arguments)
- dynamically overriding values set in ``alembic.ini``
- running any custom logic BEFORE migrations are executed
- configuring values that can be accessed at migration time
"""
import os
from logging.config import fileConfig
from typing import Dict

from alembic import context
from alembic.config import Config
from alembic.environment import EnvironmentContext
from migrations.utils.alembic_x_args import get_db_connection_string_from_env_vars, get_x_arguments
from sqlalchemy import engine_from_config, pool

#: require that this env var be set explicity to "false" to skip verifying the database connection
CONFIRM_CONNECTION_STRING_WITH_USER: bool = (
    os.environ.get("CONFIRM_CONNECTION_STRING_WITH_USER", "false").lower() != "false"
)

# this variable is already set when env.py runs
context: EnvironmentContext

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config: Config = context.config

# parse "x-arguments" from alembic commands of the form "alembic -x custom_key=custom_val -x ... upgrade"
x_args: Dict[str, str] = get_x_arguments(context)

# get the connection string from this environment
conn_string: str = get_db_connection_string_from_env_vars(
    confirm_url_with_user=CONFIRM_CONNECTION_STRING_WITH_USER
)

# override the alembic.ini->sqlalchemy.url config with the connection string
config.set_main_option("sqlalchemy.url", conn_string)

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
