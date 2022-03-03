# WARNING! DO NOT MODIFY THIS FILE! It was generated automatically
# from the make.xsh file.



# install dependencies for running other makefile targets;
# also install the rootski_api project
install:
	python -m pip install xonsh colorama pre-commit
	python -m pip install -e .[dev]




####################
# --- MAKEFILE --- #
####################

# Show a list of available Makefile targets AKA commands.
#
# Run this! The output is nice and colorful ✨ 🎨 ✨
help:
	python -m xonsh make.xsh help


# Generate a makefile from the targets registered with this instance of
# the Makefile decorator.
make:
	python -m xonsh make.xsh make


###########################
# --- RUNNING ROOTSKI --- #
###########################

# Run the rootski api using the config values in config/rootski-config.yml
run:
	python -m xonsh make.xsh run


# Run a local postgres database for REAL queries. Don't run tests against this!
run-local-db:
	python -m xonsh make.xsh run-local-db


# Run a local postgres instance for running tests (on port 8432). This one can be wiped.
run-test-db:
	python -m xonsh make.xsh run-test-db


# Run the docker-compose file.
run-compose:
	python -m xonsh make.xsh run-compose


###################
# --- TESTING --- #
###################

# Helper target for building the special rootski docker image used in
# the functional tests.
#
# If you don't run this, 'full-test' and 'full-test-local' will build
# the image automatically anyway.
build-test-image:
	python -m xonsh make.xsh build-test-image


# Execute only the unit tests.
#
# You should run this often as you make changes. Running this command
# is easy and the unit tests execute very quickly. 🚀 🎉
#
# Regularly running these as you code will make it easy to see if you've
# accidentally broken the intended behavior of existing code. The sooner
# you catch errors that you have introduced, the easier it will be to
# fix them.
unit-test:
	python -m xonsh make.xsh unit-test


# Execute ALL of the rootski API tests.
#
# NOTE: The "auth_service.py" tests require your [rootski] AWS profile
# credentials to have permissions to programattically create/delete
# a test user.
#
# This particular test may fail locally due to your credentials lacking
# sufficient permissions, but it may still pass in CI. This is because
# the CI pipeline has its own AWS credentials.
#
# NOTE: Even if you *do* have sufficient credentials, you should know
# that the functional tests require the AWS credentials to be
# present in environment variables. Run 'full-test-local' to
# have these credentials automatically added to your environment 😃
full-test-ci:
	python -m xonsh make.xsh full-test-ci


# Same as 'full-test' but tries to load your [rootski] credentials in ~/aws/credentials
# as environment variables before running the tests. 😃
full-test:
	python -m xonsh make.xsh full-test


# Execute the functional and unit tests without docker.
#
# The tests will read the values in 'tests/resources/test.env',
# but the ROOTSKI__POSTGRES_HOST variable will be set to localhost.
#
# Note that these tests require a PostgreSQL database to be available
# at localhost:<port> where port is the ROOTSKI__POSTGRES_PORT value
# found in 'tests/resources/test.env'.
#
# This can be achieved by running 'run_test_db' before running this
# target.
#
# Note that if you want to set breakpoints to debug your tests,
# you will need to need to launch the tests from your editor.
# Unfortunately, we can't write a target that stops on breakpoints
# for you :(
#
# If you are using VS Code and would like to set breakpoints for tests:
#
# 1. create a .vscode/launch.json file
# 2. create a new launch configuration
# 3. set the ROOTSKI__POSTGRES_HOST variable to localhost
# in the launch configuration
# 4. run the 'run_db' target to start up a PostgreSQL instance
# 5. (Optional) use [Command/Ctrl] + [Shift] + P to open the command palette
# and use the "Testing: Focus on test explorer view" command to
# open up the test explorer AKA a menu to browse the python tests.
# 6. Select the test you want to run in VS Code and run it
# in "debug mode".
#
# Happy testing!
full-test-no-docker:
	python -m xonsh make.xsh full-test-no-docker


# Host a local webpage for exploring test coverage.
#
# The test coverage shown is in the ./test-reports/ folder. This folder
# is created/overwritten each time pytest is run with the '--cov' argument.
#
# The 'full-test' and 'unit-test' targets both include '--cov'.
serve-coverage-report:
	python -m xonsh make.xsh serve-coverage-report


#################
# --- UTILS --- #
#################

# Install the docker-compose CLI using pip.
install-docker-compose:
	python -m xonsh make.xsh install-docker-compose


# Read the [rootski] profile ~/.aws/credentials and export then as environment variables.
export-aws-credentials-as-env-vars:
	python -m xonsh make.xsh export-aws-credentials-as-env-vars


# Remove unnecessary artifacts created while running/developing/testing the rootski API.
clean:
	python -m xonsh make.xsh clean


########################
# --- CODE QUALITY --- #
########################

# Run code quality checks against the codebase.
# Automatically fix code formatting and other things! 🚀 🎉
# The included code checks are:
#
# - black (code formatter)
# - pylint (code syntax and style checker)
# - isort (sorts imports)
# - radon (measures code complexity)
#
# Automatic fixes applied in this target are:
#
# - black will autoformat the codebase
# - isort will autosort import statements
#
# Any other issues must found by the tools must be fixed by hand
# or else the build (CI) will fail.
lint:
	python -m xonsh make.xsh lint


# Exactly the same as 'lint' except no fixes will be applied.
#
# This is the target run in CI. If you didn't run 'lint' to format the
# code and also resolve any other code quality issues discovered by
# 'lint' or 'lint-report' locally... the build will fail!! 🔥 💥 😟
lint-report:
	python -m xonsh make.xsh lint-report
