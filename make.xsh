"""
Utility script exposing a CLI interface for working with the Rootski codebase.

Run "python -m xonsh make.sh help" to see a list of available commands exposed.
"""

import sys
import os
from pathlib import Path
import json
from textwrap import dedent
from glob import glob

# manually add ./make_utils/ to PYTHONPATH so we can import from the make_utils module
THIS_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(THIS_DIR))

from make_utils.utils_without_dependencies import print_import_error_help_message, get_localhost

try:
    import bcrypt
    from rich import print
    from rich.panel import Panel
    from rich import traceback
    import configparser
except ModuleNotFoundError as e:
    print_import_error_help_message(e)
    sys.exit(1)

# make tracebacks beautiful when errors occur 😃
traceback.install()

from make_utils.makefile import Makefile
from make_utils.utils_with_dependencies import log, MakeXshError
from make_utils.xsh_utils import export_dot_env_vars
from make_utils.docker import (
    container_is_healthy,
    container_is_running,
    await_docker_container_status,
    get_container_id_by_image
)

#####################
# --- Constants --- #
#####################

# names of env files containing secrets for database, traefik, API, etc.
DEV_ENV_FILE = "dev.env"
PROD_ENV_FILE = "prod.env"

# volumes
POSTGRES_LOCAL_DATA_VOLUME = THIS_DIR / "infrastructure/containers/postgres/data"
POSTGRES_BACKUPS_VOLUME = THIS_DIR / "infrastructure/containers/postgres/backups"
PORTAINER_VOLUME = THIS_DIR / "infrastructure/containers/portainer-volume"
PGADMIN_VOLUME = THIS_DIR / "infrastructure/containers/pgadmin-volume"

CUSTOM_MAKE_TEXT = dedent("""
# run this script to install MANY dependencies needed
# to run rootski. Please read through the "onboard.sh" script in
# this directory to comment any install commands you don't want
#
# WARNING!!! read 'onboard.sh' to see which dependencies are needed to run all
# of the Makefile targets. 'onboard.sh' is experimental and may
# mess up programs installed on your system. Run it at your own risk
# or take select lines from it to install the dependencies you need.
onboard:
\t/bin/bash onboard.sh\n

# install python dependencies to run the makefile; I recommend creating and
# activating a virtual environment first. For instructions on how to do that,
# read the header comment in the "make.xsh" file or the LONG comment in the
# "onboard.sh" file.
install:
\t# install python dependencies needed to execute various makefile targets
\tpython -m pip install xonsh==0.10.1 rich pre-commit==2.15.0 bcrypt==3.2.0 dvc[s3]==2.9.4
\t# install pre-commit hooks to protect the quality of code committed by contributors
\tpre-commit install
\t# install git lfs for downloading rootski CSVs and other large files in the repo
\tgit lfs install
""")

EXTRA_HELP_MESSAGE = (
    "The [magenta]rootski_api/[/magenta] subfolder has its own [magenta]makefile[/magenta]"
    + " If you [magenta]cd[/magenta] into [magenta]rootski_api/[/magenta] and run [magenta]make help[/magenta],"
    + " you will see sub-commands that are only relevent to the backend API codebase."
)

# use this to turn python functions into makefile targets
makefile = Makefile(
    makefile_script_fname="make.xsh",
    makefile_fpath=THIS_DIR / "Makefile",
    help_message_extra=EXTRA_HELP_MESSAGE,
    makefile_header=CUSTOM_MAKE_TEXT
)


#######################
# --- Subcommands --- #
#######################

@makefile.target(tag="run services locally")
def build_images():
    """Build images needed for the backend."""
    export_dot_env_vars(env_file=DEV_ENV_FILE)
    export_rootski_profile_aws_creds()
    $POSTGRES_HOST = get_localhost()

    docker-compose build

    cd rootski_api
    docker-compose build


@makefile.target(tag="run services locally")
def start_backend():
    """Start up the backend with development settings. (see dev.env)"""
    __start_backend(env_file=DEV_ENV_FILE)
    print_dev_backend_startup_message()

@makefile.target(tag="run services locally")
def start_backend_prod():
    """
    Start up the backend with production settings.

    NOTE: you can only do this 5 times per day before
    LetsEncrypt refuses to verify certs for your IP address. (see prod.env)
    """

    # set up the acme.json file volume mount
    acme_json_cert_file = Path(THIS_DIR / "infrastructure/containers/traefik/volume/acme.json")
    not acme_json_cert_file.exists() || sudo touch @(str(acme_json_cert_file)) # create acme.json if not exists
    log("[yellow]sudo[/yellow] is required to create [yellow]acme.json[/yellow] with permission 600")
    sudo chmod 600 @(acme_json_cert_file) # the acme.json file must have this permission level
    log(f"Set [yellow]acme.json[/yellow] permissions to 600 ([dim yellow]{acme_json_cert_file}[/dim yellow])")

    # set up postgres/ folder volume mount
    POSTGRES_DATA_DIR = Path(THIS_DIR / "infrastructure/containers/postgres/data")
    POSTGRES_DATA_DIR.mkdir(exist_ok=True, parents=True)

    __start_backend(env_file=PROD_ENV_FILE)

@makefile.target(tag="run services locally")
def restore_database():
    """
    Use the "database-backup" service in the "docker-compose.yml" file drop, recreate,
    and restore all of the tables from S3.
    """
    database_backup_container_id = $(docker ps --quiet --filter name=database-backup)
    database_backup_container_id = database_backup_container_id.strip()
    docker exec @(database_backup_container_id) python3 backup_or_restore.py restore-from-most-recent || \
        echo "There is not a Postgres container currently running. Run `make start-database-stack` to start the database."

@makefile.target(tag="run services locally")
def backup_database():
    """
    Use the "database-backup" service in the "docker-compose.yml" file to backup
    the database to S3.
    """
    database_backup_container_id = $(docker ps --quiet --filter name=database-backup)
    database_backup_container_id = database_backup_container_id.strip()
    docker exec @(database_backup_container_id) python3 backup_or_restore.py backup || \
        echo "There is not a Postgres container currently running. Run `make start-database-stack` to start the database."

@makefile.target(tag="run services locally")
def start_database_stack():
    """
    Use the "database-backup" service in the "docker-compose.yml" file to backup on a
    regular inteval specified in the "docker-compose.yml" all of the tables in the
    databse.
    """
    export_dot_env_vars(env_file=DEV_ENV_FILE)
    export_rootski_profile_aws_creds()
    $POSTGRES_HOST = get_localhost()
    # Deletes any existing pgdata folder and reinitiates it.
    rm -rf infrastructure/containers/postgres/data/pgdata/
    docker swarm init || echo "docker swarm is already initialized :D"
    docker stack deploy --compose-file docker-compose.yml rootski-database

@makefile.target(tag="run services locally")
def stop_database_stack():
    """
    Tears down the `rootski-database` docker-swarm stack and removes
    ALL currently running docker containers.

    Use if you ran `run-database`.
    """
    log("Removing the `rootski-database` docker swarm stack and ALL running docker containers")
    docker stack rm rootski-database
    docker container rm --force $(docker ps -aq)
    log(
        "Done! If you want to run rootski-database again, note that it takes docker "
        + "\n\tseveral seconds to finish removing networks."
    )

@makefile.target(tag="deploy")
def deploy_backend():
    """Run "terraform apply -auto-approve" to deploy the backend"""
    log("Deploying new backend instance. Make sure the latest user-data.sh script is committed and pushed.")
    os.chdir(THIS_DIR / "./infrastructure/iac/terraform/rootski-backend")
    log("Running [magenta]terraform apply -auto-approve[/magenta]")
    terraform apply -auto-approve

@makefile.target(tag="actions on remote infrastructure")
def ssh_backend():
    """Create an SSH connection with the rootski backend instance."""
    ip = get_spot_instance_ip()
    log(f"Executing [magenta]ssh -i ~/.ssh/personal/rootski.id_rsa ec2-user@{ip}[/magenta]")
    ssh -i ~/.ssh/personal/rootski.id_rsa ec2-user@@(ip)

@makefile.target(tag="actions on remote infrastructure")
def tail_user_data_log():
    """
    Tail the progress of the [magenta]user-data.sh[/magenta] on the spot instance to
    follow the deployment progress.
    """
    # great SO answer on how to do this:
    # https://stackoverflow.com/questions/566110/how-can-i-tail-a-remote-file
    ip = get_spot_instance_ip()
    log(f"Executing [magenta]ssh -t -i ~/.ssh/personal/rootski.id_rsa ec2-user@{ip} 'tail -f /var/log/user-data.log'[/magenta]")
    ssh -t -i ~/.ssh/personal/rootski.id_rsa ec2-user@@(ip) 'tail -f /var/log/user-data.log'

@makefile.target(tag="deploy")
def deploy_frontend():
    """
    Use docker and prod.env to
    (1) build an optimized version of the frontend
    (2) reset the cloudfront cache so that users will get the new version
    (3) upload the new version to s3 (where the frontend is hosted)
    """
    frontend_dir = (THIS_DIR / "rootski_frontend").absolute()
    build_dir = frontend_dir / "build"

    # clean up the build dir
    rm -rf @(build_dir)

    docker-compose -f @(str(THIS_DIR / "rootski_frontend/docker-compose.yml")) build
    docker-compose -f @(str(THIS_DIR / "rootski_frontend/docker-compose.yml")) run build-rootski-frontend

    # get the cloudfront distribution; note that "CloudfrontID" is an Output name in the front end stack template
    FRONT_END_STACK_NAME = "Rootski-Front-End-CF"
    front_end_stack_json = $(aws cloudformation describe-stacks --stack-name @(FRONT_END_STACK_NAME) --profile rootski)
    front_end_stack_json = json.loads(front_end_stack_json)
    front_end_stack_outputs = front_end_stack_json["Stacks"][0]["Outputs"]
    cloudfront_id_output = [output for output in front_end_stack_outputs if output["OutputKey"] == "CloudfrontID"][0]
    CLOUDFRONT_DISTRIBUTION_ID = cloudfront_id_output["OutputValue"]

    # invalidate all of the cached files in the cloudfront distribution so that people's browsers will have
    # to pull the latest rootski web files when they visit www.rootski.io
    log("Invalidating rootski.io CloudFront distribution cache...")
    print($(aws cloudfront create-invalidation \
        --distribution-id @(CLOUDFRONT_DISTRIBUTION_ID) \
        --paths "/*" \
        --profile rootski))

    # now upload the built files to s3
    log("Uploading new website files to S3...")
    aws s3 sync @(build_dir) s3://www.rootski.io --acl public-read --profile rootski



@makefile.target(tag="utils")
def clean():
    """
    Delete artifacts left behind from running targets, executing tests, etc. For example:

        "**/.DS_Store"
        "**/.mypy_cache"
        "**/.pytest_cache"
        "**/test"
        "**/.coverage"
        "**/.ipynb_checkpoints"
        "**/*.pyc"

        "rootski_frontend/build"

        "infrastructure/containers/traefik/traefik.log"
        "infrastructure/containers/traefik/volume/traefik.log"
        "infrastructure/containers/traefik/volume/traefik-ui-users.htpasswd"
        "infrastructure/containers/traefik/volume/rootski-docs-users.htpasswd"
        "infrastructure/containers/traefik/volume/dynamic-config.yml"

    It isn't dangerous to delete any of these. They are all git-ignored anyway. They
    are created whenever various parts of the rootski codebase are executed.
    """
    def remove_glob(pattern):
        matches = set(glob(str(THIS_DIR / pattern), recursive=True))
        matches_in_venv = set(glob(str(THIS_DIR / "**/venv/*"), recursive=True))
        for file in (matches - matches_in_venv):
            rm -rf @(file)

    # frontend
    remove_glob("rootski_frontend/build")

    # traefik
    remove_glob("infrastructure/containers/traefik/traefik.log")
    remove_glob("infrastructure/containers/traefik/volume/traefik.log")
    remove_glob("infrastructure/containers/traefik/volume/access.log")
    remove_glob("infrastructure/containers/traefik/volume/traefik-ui-users.htpasswd")
    remove_glob("infrastructure/containers/traefik/volume/rootski-docs-users.htpasswd")
    remove_glob("infrastructure/containers/traefik/volume/dynamic-config.yml")

    # python artifacts
    remove_glob("**/.DS_Store")
    remove_glob("**/.mypy_cache")
    remove_glob("**/.pytest_cache")
    remove_glob("**/test-reports")
    remove_glob("**/.coverage")
    remove_glob("**/.ipynb_checkpoints")
    remove_glob("**/*.pyc")
    remove_glob("**/__pycache__")

@makefile.target(tag="actions on remote infrastructure")
def show_user_data_log():
    """If run on the EC2 instance, this command prints the logs."""
    cat /var/log/user-data.log

@makefile.target(tag="utils")
def await_db_healthy():
    """
    Block until the backend database is healthy or it times out.

    This is helpful in conjunction with the other subcommands like
    "make start-backend", "make run", etc.
    """
    log(f"Waiting for the PostgreSQL container ID")
    postgres_container_id = get_container_id_by_image(image_substr="postgres", wait=True, wait_timout_seconds=45)
    log(f"Postgres container id: {postgres_container_id}")
    if postgres_container_id is None: MakeXshError("Failed to find container id for postgres")
    log("Waiting for PostgreSQL container to be healthy")
    await_docker_container_status(container_id=postgres_container_id, status="healthy", timeout=45)

@makefile.target(tag="run services locally")
def run():
    """
    runs the entire rootski app (backend and frontend)
    and does all of the setup required such as building docker
    images, seeding the database (providing you've installed git-lfs
    have the data files downloaded).

    See the bottom of the "Onboarding" page in
    the knowledge base if you don't know what git-lfs
    is and you haven't set it up in your copy of this
    git repository.
    """

    export_dot_env_vars(env_file=DEV_ENV_FILE)

    # 1. make sure the data files are cloned with git-lfs
    log("(1/7) Pulling large data files ")
    which git-lfs || @(MakeXshError("git-lfs command not found; you can install it with 'make onboard'"))
    git lfs install || @(MakeXshError("'git lfs install' command failed! Do you have git-lfs installed?"))
    git lfs pull || @(MakeXshError("git lfs pull failed"))

    # 2. build the backend images
    log("(2/7) Building the backend docker images")
    build_images()

    # 3. build the frontend image
    log("(3/7) Building the frontend docker image")
    docker build \
        -f @(str(THIS_DIR / "rootski_frontend/Dockerfile")) \
        -t rootski/rootski-frontend @(str(THIS_DIR / "rootski_frontend")) \
       || @(MakeXshError("Failed to build the frontend docker image"))

    # 4. start the frontend (because it takes a while for it to be ready after the container starts)
    log("(4/7) Starting the frontend")
    docker rm --force rootski-frontend || echo "rootski frontend not running"
    __start_frontend(env_file=DEV_ENV_FILE)

    # 5. start the dev backend
    log("(5/7) Starting backend with docker swarm")
    __start_backend(env_file=DEV_ENV_FILE)


    log("(5/7) Waiting for the database to be up and healthy")
    await_db_healthy()

    log(
        "(6/7) Checking if database is already seeded... (up to 30 seconds)"
        + "\n\n\tThis process (and seeding the database) is pretty tempermental. "
        + "\n\tIf it fails, try running `make run` again a time or two. "
        + "\n\tYou can also check the `postgres` docker container logs (the VS Code "
        + "\n\t`docker` extension is great for that). You can ALSO try just running "
        + "\n\t`make start-backend`, checking that postgres is up, and then running "
        + "\n\t`make seed-dev-db`."
    )
    if not is_db_seeded(env_file=DEV_ENV_FILE):
        log("(7/7) The database has not been seeded. Seeding now (this may take a few minutes)")
        wipe_and_seed_db(env_file=DEV_ENV_FILE)
    else:
        log("(7/7) Turns out... it is! 😃")

    # 7. display all of the links of interest to the user
    print_dev_backend_startup_message()

@makefile.target(tag="run services locally")
def seed_dev_db():
    """Wipe and seed the dev database running locally."""
    wipe_and_seed_db(env_file=DEV_ENV_FILE),

@makefile.target(tag="run services locally")
def seed_prod_db():
    """Wipe and seed prod database running locally."""
    wipe_and_seed_db(env_file=PROD_ENV_FILE),

@makefile.target(tag="run services locally")
def stop():
    """
    Tears down the `rootski` docker-swarm stack and removes
    ALL currently running docker containers.

    Use if you ran `run`.
    """
    log("Removing the `rootski` docker swarm stack and ALL running docker containers")
    docker stack rm rootski
    docker container rm --force $(docker ps -aq)
    log(
        "Done! If you want to run rootski again, note that it takes docker "
        + "\n\tseveral seconds to finish removing networks."
    )

@makefile.target(tag="utils")
def install_aws_cli():
    """Helper target for installing the AWS CLI v2."""
    # set some paths for the install
    temp_dir = THIS_DIR / "aws_cli_artifacts"
    temp_dir.mkdir(exist_ok=True, parents=True)
    awscli_install_binaries_zip_fpath = str(temp_dir / "aws-cli-v2.zip")

    # install the aws cli
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o @(awscli_install_binaries_zip_fpath)
    unzip @(awscli_install_binaries_zip_fpath) -d @(str(temp_dir))
    /bin/bash  @(str(temp_dir / "aws/install"))

    # clean up
    rm -rf @(str(temp_dir))

@makefile.target(tag="continuous integration")
def check_code_quality():
    """
    Runs all of the pre-commit hooks in "rootski/.pre-commit-config.yaml"
    against the entire codebase.

    Some issues such as autoformatting the code and removing unused import statements
    will be fixed automatically.

    Other errors such as linting problems or files that are too large will need
    to be fixed manually. See the "rootski/.pre-commit-config.yaml" for
    details on ALL of the checks being run.

    NOTE: if auto-fixes are applied to any of the files in the codebase by
    running this target, you will need to "git add ..." those files again
    to commit the changes.
    """
    # ensure no pre-commit hooks are skipped by env vars
    # https://pre-commit.com/#temporarily-disabling-hooks
    $SKIP = ""
    # run the pre-commit hooks in .pre-commit-config.yaml against the entire codebase
    pre-commit run --all-files || @(MakeXshError("At least one pre-commit hook failed."))

@makefile.target(tag="continuous integration")
def check_code_quality_ci():
    """Same as above, but only runs in CI whereas above is meant to run locally."""
     # prepare to skip certain pre-commit hooks when we run them:
    # https://pre-commit.com/#temporarily-disabling-hooks
    $SKIP = "no-commit-to-branch"
    # run the pre-commit hooks in .pre-commit-config.yaml against the entire codebase
    pre-commit run --all-files || @(MakeXshError("At least one pre-commit hook failed."))


############################
# --- Helper Functions --- #
############################

def encrypt_password(username, password):
    """
    Return the equivalent string that "htpasswd -nB <username> <password>" would.

    This can be used to generate usernames and hashed passwords that traefik
    can use for protecting certain routes with basic auth.

    Note that to be used in YAML files, all occurrences of '$' must be escaped.
    Basically, just replace all occurrences of '$' with '$$' and it'll work :)
    """
    bcrypted = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
    return f"{username}:{bcrypted}"

def export_bcrypt_user_password_env_var(username, password, env_var_name):
    """Export an encrypted 'user:<encrypted passwd>' string to the "env_var_name" environment variable."""
    log(
        f"Setting [yellow]{env_var_name}[/yellow] environment variable to "
        + f"[yellow]{username}[/yellow]:[yellow]<bcrypt-hashed {username} password>[/yellow]"
    )
    bcrypted_user_pass = encrypt_password(
        username=username,
        password=password,
    )
    ${env_var_name} = bcrypted_user_pass


def export_rootski_profile_aws_creds():
    log(
        "Exporting [magenta]rootski[/magenta] profile AWS credentials to"
        + " [yellow]AWS_SECRET_ACCESS_KEY[/yellow] and [yellow]AWS_ACCESS_KEY_ID[/yellow]")
    aws_creds_rel_path = ".aws/credentials"
    aws_credentials_file = Path.home() / aws_creds_rel_path
    if not aws_credentials_file.exists():
        log(
            f"No credentials file found at \"{aws_creds_rel_path}\". Credentials not exported."
            + " This is okay if you don't need valid HTTPS certs for Traefik or if you are using IAM"
            + "Role-based Authentication.",
            mode="error"
        )

    try:
        config = configparser.RawConfigParser()
        config.read(str(aws_credentials_file))
        $AWS_ACCESS_KEY_ID = config.get("rootski", "aws_access_key_id")
        $AWS_SECRET_ACCESS_KEY = config.get("rootski", "aws_secret_access_key")
    except configparser.NoSectionError:
        log(
            f"No credentials file found at \"{aws_creds_rel_path}\". Credentials not exported."
            + " This is okay if you don't need valid HTTPS certs for Traefik or if you are using IAM"
            + "Role-based Authentication.",
            mode="error"
        )


def get_spot_instance_ip():
    """Get the IP address of currently deployed spot instance."""
    tfstate_fpath = str(THIS_DIR / "./infrastructure/iac/terraform/rootski-backend/terraform.tfstate")
    rootski_backend_terraform_outputs = $(terraform output -json -state=@(tfstate_fpath))
    data = json.loads(rootski_backend_terraform_outputs)
    ip = data["rootski_public_ip"]["value"]
    return ip


def __start_backend(env_file):
    # make sure the traefik.log mount won't break

    def wipe_and_create_traefik_file(fname):
        fpath = THIS_DIR / Path(f"./infrastructure/containers/traefik/volume/{fname}")
        log(f"wiping/creating the mounted [yellow]{fname}[/yellow] file at [dim yellow]{fpath}[/dim yellow]")
        fpath.exists() && rm -rf @(fpath) # delete the log file if it exists
        touch @(fpath) # then re-create it

    wipe_and_create_traefik_file(fname="traefik.log")
    wipe_and_create_traefik_file(fname="access.log")

    # ensure volume mount folders exist; NOTE, postgres seems to get angry
    # if we create the postgres db volume here... so we won't. Instead,
    # the postgres/volume/ folder has a .gitkeep inside of it
    POSTGRES_BACKUPS_VOLUME.mkdir(exist_ok=True, parents=True)
    POSTGRES_LOCAL_DATA_VOLUME.mkdir(exist_ok=True, parents=True)
    PORTAINER_VOLUME.mkdir(exist_ok=True, parents=True)
    PGADMIN_VOLUME.mkdir(exist_ok=True, parents=True)

    # init the docker swarm
    docker swarm init || echo "docker swarm is already initialized :D"

    export_dot_env_vars(env_file)
    export_rootski_profile_aws_creds()

    # derive the <user>:<bcrypted password> strings for basic-auth-protected
    # traefik routes and export them as environment variables for docker swarm
    export_bcrypt_user_password_env_var(
        username=$TRAEFIK__ROOTSKI_DOCS_USER,
        password=$TRAEFIK__ROOTSKI_DOCS_PASSWORD,
        env_var_name="TRAEFIK__ROOTSKI_BCRYPT_USER_PASSWORD"
    )
    export_bcrypt_user_password_env_var(
        username=$TRAEFIK__TRAEFIK_UI_USER,
        password=$TRAEFIK__TRAEFIK_UI_PASSWORD,
        env_var_name="TRAEFIK__TRAEFIK_UI_BCRYPT_USER_PASSWORD"
    )

    error_msg = "'docker stack deploy' command failed; this may work if you try again--do check the error message, though"
    docker stack deploy \
        --compose-file docker-compose.yml \
        rootski \
    || @(MakeXshError(error_msg))
    # docker stack deploy \
    #     --compose-file docker-compose.yml \
    #     --compose-file docker-compose.traefik-labels.yml \
    # rootski \
    # || @(MakeXshError(error_msg))

def __start_frontend(env_file=DEV_ENV_FILE):
    frontend_dir = THIS_DIR / "rootski_frontend"
    node_modules_dir = frontend_dir / "node_modules"

    error_msg = "'docker run' command failed for rootski/rootski-frontend. You could try:" \
        + "\n\t(1) running 'make stop' to remove all docker containers" \
        + "\n\t(2) running 'make run' to try again" \
        + "\n\t(-) You can also restart docker desktop if you *really* can't" \
        + "\n\t    get rid of your running containers 🤷‍♂️."

    # use a local volume mount if the user has node installed
    # and has run "npm install" in "rootski_frontend"
    if node_modules_dir.exists():
        docker run -d \
            --name rootski-frontend \
            -e REACT_APP__BACKEND_URL=http://localhost:3333 \
            -e CHOKIDAR_USEPOLLING=true \
            -e PORT=3000 \
            -e HOST=0.0.0.0 \
            -v @(str(frontend_dir)):/app \
            -p 3000:3000 \
            -ti \
            rootski/rootski-frontend \
        || @(MakeXshError(error_msg))

    # if they haven't, it's easier for users to just use the
    # set of node_modules in the frontend image; sadly, this means
    # it won't watch for their local changes and react if they
    # are developing on it
    else:
        docker run -d \
            --name rootski-frontend \
            -e REACT_APP__BACKEND_URL=http://localhost:3333 \
            -e CHOKIDAR_USEPOLLING=true \
            -e PORT=3000 \
            -e HOST=0.0.0.0 \
            -p 3000:3000 \
            -ti \
            rootski/rootski-frontend \
        || @(MakeXshError(error_msg))


def print_dev_backend_startup_message():
    export_dot_env_vars(env_file=DEV_ENV_FILE)
    message = dedent(f"""
    [green]Started Rootski in development mode![/green] 🎉 🎉 🎉

    [cyan]Note:[/cyan] it may take a few seconds for the frontend to become available.
    Run [magenta]docker ps[/magenta] to see how all the containers are doing (if
    you ran [magenta]make run[/magenta] to get here). You should expect to see a [magenta]rootski/rootski-frontend[/magenta]
    container running.

    Below, you'll find various helpful links to help you access
    all the services you just started 😃

    [cyan]
    Frontend
    --------[/cyan]

    The frontend is written in [magenta]React[/magenta]. You can start it manually with
    [magenta]cd rootski_frontend; npm install; npm run start[/magenta]
    If you ran [magenta]make run[/magenta] to get here, this should be unnecessary.

    url  [yellow]http://localhost:3000[/yellow]

    Some cyrillic words to use in the search bar:

    - [magenta]принимать[/magenta] (verb)
    - [magenta]снисходительный[/magenta] (adjective)
    - [magenta]быстро[/magenta] (adverb)
    - [magenta]ли[/magenta] (particle)
    - [magenta]любовь[/magenta] (noun)

    [cyan]
    Backend API UIs
    ---------------[/cyan]

    The backend API uses [magenta]REST[/magenta] for requests that modify data.
    It uses [magenta]GraphQL[/magenta] for requests that read data. We have a
    ✨ fancy UI ✨ for each of these. Check them out!

    REST API Docs  [yellow]https://localhost[magenta]/docs[/magenta][/yellow]
    GraphQL        [yellow]https://{ $TRAEFIK__ROOTSKI_API_SUBDOMAIN }.{ $TRAEFIK__ROOTSKI_DOMAIN }[magenta]/graphql[/magenta][/yellow]
    username       [dim bold green]{ $TRAEFIK__ROOTSKI_DOCS_USER }[/dim bold green]
    password       [dim bold green]{ $TRAEFIK__ROOTSKI_DOCS_PASSWORD }[/dim bold green]

    [cyan]
    PostgreSQL Connection Information
    ---------------------------------[/cyan]

    host      [dim bold green]localhost[/dim bold green]
    user      [dim bold green]{ $POSTGRES_USER }[/dim bold green]
    password  [dim bold green]{ $POSTGRES_PASSWORD }[/dim bold green]
    database  [dim bold green]{ $POSTGRES_DB }[/dim bold green]
    port      [dim bold green]{ $POSTGRES_PORT }[/dim bold green]

    You can use these credentials to connect to our PostgreSQL
    database and browse the data using any PostgreSQL "client program".
    I recommend downloading and installing [magenta]DBeaver[/magenta].

    [cyan]
    Notes
    -----[/cyan]

    [cyan]*[/cyan] The docker extension for VS Code makes
        it really easy to view the logs to all of the rootski containers,
        or get a bash shell inside of them to explore and debug.
    """)

    panel = Panel(
        message,
        title="Welcome to the Rootski Dev Team!",
        border_style="cyan",
        expand=False,
    )
    print(panel)


def wipe_and_seed_db(env_file):
    """Drop and create all rootski db tables, then load seed data into them."""
    export_dot_env_vars(env_file)

    localhost = get_localhost()

    data_dir = THIS_DIR / "rootski_api/migrations/initial_data/data"

    # use the rootski container to seed the database
    docker run \
        -v @(data_dir):/data \
        -v @(data_dir / "../gather_data.py"):/gather_data.py \
        --network host \
        -e DATA_DIR=/data \
        -e POSTGRES_HOST=@(localhost) \
        -e POSTGRES_PORT=$POSTGRES_PORT \
        -e POSTGRES_USER=$POSTGRES_USER \
        -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
        -e POSTGRES_DB=$POSTGRES_DB \
        --entrypoint python \
        rootski/rootski-api /gather_data.py "seed-db" \
    || @(MakeXshError(  \
        "Failed to seed the database. You could try: " \
        + f"\n\t(1) deleting the '{POSTGRES_LOCAL_DATA_VOLUME}' folder"  \
        + "\n\t(2) running 'make stop'" \
        + "\n\t(3) waiting a few seconds for the docker networks to delete" \
        + "\n\t(4) running 'make run' again" \
    ))

def is_db_seeded(env_file) -> bool:
    """Return True if the database has been seeded."""
    export_dot_env_vars(env_file)

    localhost = get_localhost()

    data_dir = THIS_DIR / "rootski_api/migrations/initial_data/data"

    # use the rootski container to seed the database
    db_is_seeded_response = $(docker run \
        -v @(data_dir):/data \
        -v @(data_dir / "../gather_data.py"):/gather_data.py \
        --network host \
        -e DATA_DIR=/data \
        -e POSTGRES_HOST=@(localhost) \
        -e POSTGRES_PORT=$POSTGRES_PORT \
        -e POSTGRES_USER=$POSTGRES_USER \
        -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
        -e POSTGRES_DB=$POSTGRES_DB \
        --entrypoint python \
        rootski/rootski-api /gather_data.py "is-db-seeded")
    print(db_is_seeded_response)
    return "success" in db_is_seeded_response


################
# --- Main --- #
################

def main():
    "Get the command from the arguments and execute it; if invalid command, show the usage"
    try:
        makefile.run()
    except MakeXshError as e:
        log("make.xsh exited with the following MakeXshError:")
        print(e)
        print(makefile.__generate_help_message())

if __name__ == "__main__":
    main()
