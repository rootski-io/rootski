# WARNING! DO NOT MODIFY THIS FILE! It was generated automatically
# from the make.xsh file.



# install python dependencies needed to run database migrations;
# creating/activating a Python virtual environment is recommended!
install:
	# install python dependencies needed to execute various makefile targets
	python -m pip install -e "../make_utils"
	python -m pip install -e .




####################
# --- MAKEFILE --- #
####################

# Show a list of available Makefile targets AKA commands.
#
# Run this! The output is nice and colorful ✨ 🎨 ✨
help:
	python -m xonsh make.xsh help


# Generate a makefile from the targets registered with this Makefile instance.
make:
	python -m xonsh make.xsh make


###############################
# --- CREATING MIGRATIONS --- #
###############################

# Use the 'alembic' CLI to create a blank '.py' file that can be used
# to define logic for a change to the rootski database schema.
#
# [blue]Note[/blue]: you need to have 'alembic' and other dependencies
# installed for this to run. Run 'make install' to install those 😉.
create-migration-file:
	python -m xonsh make.xsh create-migration-file


##############################
# --- RUNNING MIGRATIONS --- #
##############################

# Attempt to run all of the "alembic" migrations against a database
# starting from whichever migration the database is currently on.
#
# You can find the current alembic revision that a database is on
# by looking for an "alembic_version" table. If the table doesn't exist
# in the database, no revisions have been run.
#
# The connection information for the database will be taken from
# the "rootski/dev.env" file.
run-all-migrations-from-current--dev:
	python -m xonsh make.xsh run-all-migrations-from-current--dev


# Execute the database migrations using docker.
run-all-migrations-from-current--dev--docker:
	python -m xonsh make.xsh run-all-migrations-from-current--dev--docker


#################
# --- UTILS --- #
#################

# Build the docker image for running database migrations.
build-image:
	python -m xonsh make.xsh build-image


# Print env var prefix for running alembic commands against the local dev database.
#
# The idea is that you could use the string printed to the console to execute
# alembic commands against a local database like this:
#
# .. code-block:: bash
#
# cd rootski_api/migrations/src
# POSTGRES_USER=rootski \
# POSTGRES_PASSWORD=pass \
# POSTGRES_HOST=localhost \
# POSTGRES_PORT=5432 \
# POSTGRES_DB=rootski_db \
# alembic --config ../alembic.ini <some subcommand> [ARGS]
#
# .. code-block:: bash
#
# POSTGRES_USER=rootski POSTGRES_PASSWORD=pass POSTGRES_HOST=localhost POSTGRES_PORT=5432 POSTGRES_DB=rootski_db alembic --config ../alembic.ini
print-dev-alembic-env-vars:
	python -m xonsh make.xsh print-dev-alembic-env-vars
