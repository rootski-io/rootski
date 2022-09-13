"""
This file is similar to the ``make.xsh`` script in the root of the
``rootski`` repository. See the header in that file for more details.
"""

import sys
from pathlib import Path
from textwrap import dedent
from glob import glob
from copy import deepcopy

# TODO: for some reason "pip install "
THIS_DIR = Path(__file__).parent
MAKE_UTILS_DIR = (THIS_DIR / "../make_utils/src").resolve().absolute()

from rich import print
sys.path.insert(0, str(MAKE_UTILS_DIR))

from make_utils.utils_without_dependencies import print_import_error_help_message

try:
    from rich import print
    from rich.panel import Panel
    import configparser
except ModuleNotFoundError as e:
    print_import_error_help_message(e)
    sys.exit(1)

from make_utils.makefile import Makefile
from make_utils.utils_with_dependencies import log, MakeXshError

from make_utils.utils_with_dependencies import log, MakeXshError
from make_utils.makefile import Makefile
from make_utils.xsh_utils import export_dot_env_vars

from rich import traceback
from rich import print
from rich.console import Console

# make tracebacks beautiful when errors occur 😃
traceback.install()

THIS_DIR = Path(__file__).parent


CUSTOM_MAKE_TEXT = dedent(f"""
# install dependencies for running other makefile targets;
# also install the rootski_api project
install:
\tpython -m pip install xonsh colorama pre-commit
\tpython -m pip install -e ../make_utils
\tpython -m pip install -e .[dev]
""")


# use this to turn python functions into makefile targets
makefile = Makefile(
    makefile_script_fname="make.xsh",
    makefile_fpath=THIS_DIR / "Makefile",
    makefile_header=CUSTOM_MAKE_TEXT
)


############################
# --- Makefile Targets --- #
############################


@makefile.target(tag="running rootski")
def run():
    """Run the rootski api using the config values in config/rootski-config.yml"""
    rootski_config_fpath = str((THIS_DIR / "config/rootski-config.yml").resolve().absolute())
    $ROOTSKI__CONFIG_FILE_PATH = rootski_config_fpath
    $AWS_PROFILE = "rootski"
    uvicorn "rootski.main.main:create_default_app" --factory --reload --port 3333


@makefile.target(tag="running rootski")
def run_local_db():
    """Run a local postgres database for REAL queries. Don't run tests against this!"""
    docker-compose run --publish 5432:5432 postgres


@makefile.target(tag="running rootski")
def run_test_db():
    """Run a local postgres instance for running tests (on port 8432). This one can be wiped."""
    docker-compose \
        -f @(str(THIS_DIR))/tests/resources/docker-compose.yml \
        run --rm --service-ports postgres


@makefile.target(tag="running rootski")
def run_compose():
    """Run the docker-compose file."""
    docker-compose up --remove-orphans


@makefile.target(tag="testing")
def build_test_image():
    """
    Helper target for building the special rootski docker image used in
    the functional tests.

    If you don't run this, 'full-test' and 'full-test-local' will build
    the image automatically anyway.
    """
    cd tests/resources \
		&& docker-compose build


@makefile.target(tag="utils")
def install_docker_compose():
    """Install the docker-compose CLI using pip."""
    pip install docker-compose


@makefile.target(tag="utils")
def export_aws_credentials_as_env_vars():
    """
    Read the [rootski] profile ~/.aws/credentials and export then as environment variables.
    """
    $AWS_ACCESS_KEY_ID=$(aws configure get rootski.aws_access_key_id).strip()
    $AWS_SECRET_ACCESS_KEY=$(aws configure get rootski.aws_secret_access_key).strip()
    $AWS_DEFAULT_REGION=$(aws configure get rootski.region).strip()

@makefile.target(tag="utils")
def clean():
    """Remove unnecessary artifacts created while running/developing/testing the rootski API."""
    find src tests -path '*.pyc*' -delete
    find src tests -path '*pycache*' -delete
    find src tests -path '*.py,cover*' -delete
    find src tests -path '.coverage' -delete
    find src -path '*.egg-info*' -delete
    rm -rf .pytest_cache
    rm -rf .eggs
    rm -rf .coverage test-reports coverage.xml
    rm -rf .ipynb_checkpoints
    rm -rf _docs docs-tmp
    rm -rf build dist

@makefile.target(tag="testing")
def unit_test():
    """
    Execute only the unit tests.

    You should run this often as you make changes. Running this command
    is easy and the unit tests execute very quickly. 🚀 🎉

    Regularly running these as you code will make it easy to see if you've
    accidentally broken the intended behavior of existing code. The sooner
    you catch errors that you have introduced, the easier it will be to
    fix them.
    """
    pytest tests/unit_tests/ --cov src/ \
        --cov-report term-missing \
        --cov-report html \
        --cov-report xml \
        --junitxml=./test-reports/junit.xml

@makefile.target(tag="testing")
def full_test_ci():
    """
    Execute ALL of the rootski API tests.

    NOTE: The "auth_service.py" tests require your [rootski] AWS profile
    credentials to have permissions to programattically create/delete
    a test user.

    This particular test may fail locally due to your credentials lacking
    sufficient permissions, but it may still pass in CI. This is because
    the CI pipeline has its own AWS credentials.

    NOTE: Even if you *do* have sufficient credentials, you should know
    that the functional tests require the AWS credentials to be
    present in environment variables. Run 'full-test-local' to
    have these credentials automatically added to your environment 😃
    """
    # execute tests
    log("Executing all tests with docker-compose (excluding smoke tests)")
    $RAISE_SUBPROC_ERROR = True
    try:
        cd tests/resources \
        && docker-compose run --rm \
            -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
            -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
            -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
            rootski \
                py.test tests \
                    --ignore "tests/smoke_tests" \
                    --cov src/ \
                    --cov-report term-missing \
                    --cov-report html \
                    --cov-report xml \
                    --junitxml=./test-reports/junit.xml
    except:
        # exit with status code 1
        MakeXshError("Tests failed!")
    finally:
        # this block executes even if 'except' calls sys.exit()
        log("Spinning down docker-compose stack")
        docker-compose down

@makefile.target(tag="testing")
def full_test():
    """
    Same as 'full-test' but tries to load your [rootski] credentials in ~/aws/credentials
    as environment variables before running the tests. 😃
    """
    export_aws_credentials_as_env_vars()
    full_test_ci()


@makefile.target(tag="testing")
def full_test_no_docker():
    """
    Execute the functional and unit tests without docker.

    The tests will read the values in 'tests/resources/test.env',
    but the ROOTSKI__POSTGRES_HOST variable will be set to localhost.

    Note that these tests require a PostgreSQL database to be available
    at localhost:<port> where port is the ROOTSKI__POSTGRES_PORT value
    found in 'tests/resources/test.env'.

    This can be achieved by running 'run_test_db' before running this
    target.

    Note that if you want to set breakpoints to debug your tests,
    you will need to need to launch the tests from your editor.
    Unfortunately, we can't write a target that stops on breakpoints
    for you :(

    If you are using VS Code and would like to set breakpoints for tests:

        1. create a .vscode/launch.json file
        2. create a new launch configuration
        3. set the ROOTSKI__POSTGRES_HOST variable to localhost
           in the launch configuration
        4. run the 'run_db' target to start up a PostgreSQL instance
        5. (Optional) use [Command/Ctrl] + [Shift] + P to open the command palette
           and use the "Testing: Focus on test explorer view" command to
           open up the test explorer AKA a menu to browse the python tests.
        6. Select the test you want to run in VS Code and run it
           in "debug mode".

    Happy testing!
    """
    $ROOTSKI__POSTGRES_HOST = "localhost"
    py.test tests \
        --ignore "tests/smoke_tests" \
        --cov src/ \
        --cov-report term-missing \
        --cov-report html \
        --cov-report xml \
        --junitxml=./test-reports/junit.xml

@makefile.target(tag="testing")
def serve_coverage_report():
    """
    Host a local webpage for exploring test coverage.

    The test coverage shown is in the ./test-reports/ folder. This folder
    is created/overwritten each time pytest is run with the '--cov' argument.

    The 'full-test' and 'unit-test' targets both include '--cov'.
    """
    coverage_report_port = 8080
    log(f"Serving test coverage at [yellow]http://localhost:{coverage_report_port}[/yellow]")
    python -m http.server @(coverage_report_port) --directory test-reports/htmlcov


@makefile.target("code quality")
def lint():
    """
    Run code quality checks against the codebase.
    Automatically fix code formatting and other things! 🚀 🎉
    The included code checks are:

        - black (code formatter)
        - pylint (code syntax and style checker)
        - isort (sorts imports)
        - radon (measures code complexity)

    Automatic fixes applied in this target are:

        - black will autoformat the codebase
        - isort will autosort import statements

    Any other issues must found by the tools must be fixed by hand
    or else the build (CI) will fail.
    """
    try:
        $RAISE_SUBPROC_ERROR = True
        black src/rootski/ tests/ --line-length 112
        isort src/rootski/ tests/ --profile black
        #    pylint src/rootski tests/
        radon cc raw mi ha
        # python -m doctest src/**/*.py
    except:
        MakeXshError("Errors were found while linting.")


@makefile.target("code quality")
def lint_report():
    """
    Exactly the same as 'lint' except no fixes will be applied.

    This is the target run in CI. If you didn't run 'lint' to format the
    code and also resolve any other code quality issues discovered by
    'lint' or 'lint-report' locally... the build will fail!! 🔥 💥 😟
    """
    try:
        $RAISE_SUBPROC_ERROR = True
        black src/rootski/ tests/ --check --line-length 112
        isort src/rootski/ tests/ --check-only --profile black
        #    pylint src/rootski/ tests/
        radon cc raw mi ha
        # python -m doctest src/**/*.py
    except:
        MakeXshError("Errors were found while linting.")

def main():
    try:
        makefile.run()
    except MakeXshError as e:
        log("make.xsh exited with the following MakeXshError:", mode="error")
        print(e)


if __name__ == "__main__":
    main()
