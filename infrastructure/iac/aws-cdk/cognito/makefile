# first 7 characters of the current git commit hash
SHORT_GIT_COMMIT_HASH=$$(git rev-parse --short HEAD)

# current project version
PROJECT_VERSION=$$(cat version.txt)

# Do a symbolic install of the project into the current environment.
# Ensure that a virtual or condas environment is active before executing this command, otherwise the
# install will be into system Python.
# -e Tells the tool to install symbolically. Site-packages in the environment will be symlinks to code.
# The [dev] spec tells setup to install extra dependencies needed for development work.
install:
	pip install -U pip
	pip install -r requirements.txt

diff:
	cdk diff --profile rootski

deploy:
	cdk deploy --profile rootski

# Execute ben-py-lint against the source and test folders.
# This will update code in place for applicable tools (black, isort, etc.)
# Ben-py-lint behaves differently in test folders, consult it's documentation for more information.
lint:
	black src/rootski/ tests/ -l 112
	isort src/rootski/ tests/
	radon cc raw mi hal

# execute unit tests and generate coverage reports.
# Note: Generating html outputs are optional, this line can be removed if build time is an issue.
unit-test:
	pytest tests/unit_tests/ --cov src/ \
		--cov-report term-missing \
		--cov-report html \
		--cov-report xml \
		--junitxml=./test-reports/junit.xml

# execute doctests on docstrings and files in the docs/ folder
doctest:
	# equivalent of 'python -m doctest src/**/*.py docs/**/*.rst'
	python -m doctest $$(find src -name "*.py")
	python -m doctest $$(find docs -name "*.rst")

# Execute unit tests, full tests, and doctests; generating coverage reports.
# Note: Generating html outputs are optional, this line can be removed if build time is an issue.
full-test:
	pytest tests/ --cov src/ \
		--cov-report term-missing \
		--cov-report html \
		--cov-report xml \
		--junitxml=./test-reports/junit.xml
	# equivalent of 'python -m doctest src/**/*.py docs/**/*.rst'
	python -m doctest $$(find src -name "*.py")
	python -m doctest $$(find docs -name "*.rst")

# Host a local http server to view the test coverage report locally.
# Note, the coverage report should first be generated using `make unit-test` or `make full-test`.
serve-coverage-report:
	@echo "serving test coverage site at http://localhost:3333"
	python -m http.server 3333 --directory test-reports/htmlcov

validate-project: build-docs lint-report full-test

# Safely tag repository with the latest version.
tag-with-latest-version:
	git tag $$(cat version.txt) || echo "repository already tagged"

# Push local git tags to remote origin; will fail if any local tags
# are already on remote. WARNING: Only call this if you know what you are
# doing since the state of the git tags in remote impacts whether builds pass or fail.
push-tags-to-remote:
	git push origin --tags

# Delete unnecessary artifacts from the project directory
clean:
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
