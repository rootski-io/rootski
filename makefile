# WARNING! DO NOT MODIFY THIS FILE! It was generated automatically
# from the make.xsh file.



# run this script to install MANY dependencies needed
# to run rootski. Please read through the "onboard.sh" script in
# this directory to comment any install commands you don't want
#
# WARNING!!! read 'onboard.sh' to see which dependencies are needed to run all
# of the Makefile targets. 'onboard.sh' is experimental and may
# mess up programs installed on your system. Run it at your own risk
# or take select lines from it to install the dependencies you need.
onboard:
	/bin/bash onboard.sh


# install python dependencies to run the makefile; I recommend creating and
# activating a virtual environment first. For instructions on how to do that,
# read the header comment in the "make.xsh" file or the LONG comment in the
# "onboard.sh" file.
install:
	# install python dependencies needed to execute various makefile targets
	python -m pip install xonsh==0.10.1 rich pre-commit==2.15.0 bcrypt==3.2.0 dvc[s3]==2.9.4
	# install pre-commit hooks to protect the quality of code committed by contributors
	pre-commit install
	# install git lfs for downloading rootski CSVs and other large files in the repo
	git lfs install




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


############################
# --- ALL CONTRIBUTORS --- #
############################

# Use "npm" to install the all-contributors-cli and initialize
# the rootski/ folder as a node project.
install-all-contributors-cli:
	python -m xonsh make.xsh install-all-contributors-cli


# Use the "all-contributors-cli" to generate the tables
# that credit developers for contributions registered in
# the "rootski/.all-contributorsrc" file.
generate-all-contributors-table:
	python -m xonsh make.xsh generate-all-contributors-table


################################
# --- RUN SERVICES LOCALLY --- #
################################

# Build images needed for the backend.
build-images:
	python -m xonsh make.xsh build-images


# Start up the backend with development settings. (see dev.env)
start-backend:
	python -m xonsh make.xsh start-backend


# Start up the backend with production settings.
#
# NOTE: you can only do this 5 times per day before
# LetsEncrypt refuses to verify certs for your IP address. (see prod.env)
start-backend-prod:
	python -m xonsh make.xsh start-backend-prod


# Use the "database-backup" service in the "docker-compose.yml" file drop, recreate,
# and restore all of the tables from S3.
restore-database:
	python -m xonsh make.xsh restore-database


# Use the "database-backup" service in the "docker-compose.yml" file to backup
# the database to S3.
backup-database:
	python -m xonsh make.xsh backup-database


# Use the "database-backup" service in the "docker-compose.yml" file to backup on a
# regular inteval specified in the "docker-compose.yml" all of the tables in the
# databse.
start-database-stack:
	python -m xonsh make.xsh start-database-stack


# Tears down the `rootski-database` docker-swarm stack and removes
# ALL currently running docker containers.
#
# Use if you ran `run-database`.
stop-database-stack:
	python -m xonsh make.xsh stop-database-stack


# runs the entire rootski app (backend and frontend)
# and does all of the setup required such as building docker
# images, seeding the database (providing you've installed git-lfs
# have the data files downloaded).
#
# See the bottom of the "Onboarding" page in
# the knowledge base if you don't know what git-lfs
# is and you haven't set it up in your copy of this
# git repository.
run:
	python -m xonsh make.xsh run


# Wipe and seed the dev database running locally.
seed-dev-db:
	python -m xonsh make.xsh seed-dev-db


# Wipe and seed prod database running locally.
seed-prod-db:
	python -m xonsh make.xsh seed-prod-db


# Tears down the `rootski` docker-swarm stack and removes
# ALL currently running docker containers.
#
# Use if you ran `run`.
stop:
	python -m xonsh make.xsh stop


##################
# --- DEPLOY --- #
##################

# Run "terraform apply -auto-approve" to deploy the backend
deploy-backend:
	python -m xonsh make.xsh deploy-backend


# Use docker and prod.env to
# (1) build an optimized version of the frontend
# (2) reset the cloudfront cache so that users will get the new version
# (3) upload the new version to s3 (where the frontend is hosted)
deploy-frontend:
	python -m xonsh make.xsh deploy-frontend


############################################
# --- ACTIONS ON REMOTE INFRASTRUCTURE --- #
############################################

# Create an SSH connection with the rootski backend instance.
ssh-backend:
	python -m xonsh make.xsh ssh-backend


# Tail the progress of the [magenta]user-data.sh[/magenta] on the spot instance to
# follow the deployment progress.
tail-user-data-log:
	python -m xonsh make.xsh tail-user-data-log


# If run on the EC2 instance, this command prints the logs.
show-user-data-log:
	python -m xonsh make.xsh show-user-data-log


#################
# --- UTILS --- #
#################

# Delete artifacts left behind from running targets, executing tests, etc. For example:
#
# "**/.DS_Store"
# "**/.mypy_cache"
# "**/.pytest_cache"
# "**/test"
# "**/.coverage"
# "**/.ipynb_checkpoints"
# "**/*.pyc"
#
# "rootski_frontend/build"
#
# "infrastructure/containers/traefik/traefik.log"
# "infrastructure/containers/traefik/volume/traefik.log"
# "infrastructure/containers/traefik/volume/traefik-ui-users.htpasswd"
# "infrastructure/containers/traefik/volume/rootski-docs-users.htpasswd"
# "infrastructure/containers/traefik/volume/dynamic-config.yml"
#
# It isn't dangerous to delete any of these. They are all git-ignored anyway. They
# are created whenever various parts of the rootski codebase are executed.
clean:
	python -m xonsh make.xsh clean


# Block until the backend database is healthy or it times out.
#
# This is helpful in conjunction with the other subcommands like
# "make start-backend", "make run", etc.
await-db-healthy:
	python -m xonsh make.xsh await-db-healthy


# Helper target for installing the AWS CLI v2.
install-aws-cli:
	python -m xonsh make.xsh install-aws-cli


##################################
# --- CONTINUOUS INTEGRATION --- #
##################################

# Runs all of the pre-commit hooks in "rootski/.pre-commit-config.yaml"
# against the entire codebase.
#
# Some issues such as autoformatting the code and removing unused import statements
# will be fixed automatically.
#
# Other errors such as linting problems or files that are too large will need
# to be fixed manually. See the "rootski/.pre-commit-config.yaml" for
# details on ALL of the checks being run.
#
# NOTE: if auto-fixes are applied to any of the files in the codebase by
# running this target, you will need to "git add ..." those files again
# to commit the changes.
check-code-quality:
	python -m xonsh make.xsh check-code-quality


# Same as above, but only runs in CI whereas above is meant to run locally.
check-code-quality-ci:
	python -m xonsh make.xsh check-code-quality-ci
