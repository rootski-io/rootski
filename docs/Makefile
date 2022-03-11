# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build

#
SOURCEDIR     = ./source/

# location to write the generated HTML files and other assets
BUILDDIR      = ./build/

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

invalidate-s3-cache:
	python aws_invalidate_stack.py \
		--s3-static-site-stack-name docs-s3-static-site--stack--cdk \
		--region us-east-1 \
		--profile rootski

# after running 'make html' or 'make docs-docker', run this to
# upload the docs to S3 and incalidate the CloudFront cache so that
# users can access the new in the browser
publish-to-s3: invalidate-s3-cache
	aws s3 sync ./build/html/ s3://docs.rootski.io/ --acl public-read --profile rootski
	@echo "docs published to https://docs.rootski.io/"

# publish docs to S3 to docs.rootski.io/review/<current-branch-name>/
# this is an easy way to share the docs you're working on with other collaborators
# before they are ready to deploy to the public-facing docs site.
publish-to-s3-for-review: invalidate-s3-cache
	aws s3 \
		sync ./build/html/ "s3://docs.rootski.io/review/$$(git branch --show-current)/" \
		--acl public-read \
		--profile rootski
	echo "[rootski] published docs to https://docs.rootski.io/review/$$(git branch --show-current)"

# build a docker image with python dependencies for the entire project
build-image:
	docker-compose build

# use the docker image to build the docs
docs-docker:
	mkdir -p $(BUILDDIR)/html
	mkdir -p $(BUILDDIR)/doctrees
	docker-compose run --rm sphinx

# use the docker image to build the docs; use special configurations
# for building the docs in CI such as failing on any warnings
docs-docker-ci:
	mkdir -p $(BUILDDIR)/html
	mkdir -p $(BUILDDIR)/doctrees
	docker-compose run --rm sphinx docs-ci

# build docs, but fail with warnings
docs-ci:
	@$(SPHINXBUILD) -W "$(SOURCEDIR)" "$(BUILDDIR)"

# use the docker image to
serve-docker:
	docker-compose run -p 4444:4444 sphinx serve

# start a local server that rebuilds the docs whenever one
# of the .rst files in rootski/docs/source changes; note that
# the build can take a long time or get stuck in a loop of
# perpetual building
serve-watch:
	sphinx-autobuild $(SOURCEDIR) $(BUILDDIR)/html ../README.rst

# install python dependencies needed to build the docs; note that
# you must also have nodejs and draw.io-desktop install on your
# system for the docs to build successfully
install:
	@echo "install python requirements"
	pip install -r requirements.txt

# serve the docs over s static http server
serve:
	@echo "[rootski] hosting the docs at ✨ http://localhost:4444 ✨"
	@echo "          refresh your browser each time you run 'make html' or make 'docs-docker'"
	@echo "          to see the changes reflected in your browser"
	@echo ""
	@echo ""
	python -m http.server 4444 --directory $(BUILDDIR)/html

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
