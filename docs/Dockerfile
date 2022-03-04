FROM python:3.9-slim-bullseye


RUN apt-get update && apt-get install -y \
    cmake

##############################################################
# --- Install draw.io CLI for rendering .drawio diagrams --- #
##############################################################

WORKDIR "/opt/drawio-desktop"

    # libappindicator3-1 \
ENV DRAWIO_VERSION "16.0.0"
RUN set -e; \
    apt-get install -y \
    xvfb \
    wget \
    libgbm1 \
    libasound2; \
    wget -q https://github.com/jgraph/drawio-desktop/releases/download/v${DRAWIO_VERSION}/drawio-amd64-${DRAWIO_VERSION}.deb \
    && apt-get install -y /opt/drawio-desktop/drawio-amd64-${DRAWIO_VERSION}.deb \
    && rm -rf /opt/drawio-desktop/drawio-amd64-${DRAWIO_VERSION}.deb; \
    rm -rf /var/lib/apt/lists/*;

ENV ELECTRON_DISABLE_SECURITY_WARNINGS "true"
ENV DRAWIO_DISABLE_UPDATE "true"
ENV DRAWIO_DESKTOP_COMMAND_TIMEOUT "10s"
ENV DRAWIO_DESKTOP_EXECUTABLE_PATH "/opt/drawio/drawio"
# Currently, no security warning in this version of drawio desktop
# ENV DRAWIO_DESKTOP_RUNNER_COMMAND_LINE "/opt/drawio-desktop/runner.sh"
ENV DRAWIO_DESKTOP_RUNNER_COMMAND_LINE "/opt/drawio-desktop/runner-no-security-warnings.sh"
ENV XVFB_DISPLAY ":42"
ENV XVFB_OPTIONS ""

#####################################################
# --- install NodeJS for the AWS CDK cli to use --- #
#####################################################

RUN apt-get update && apt-get install -y nodejs


#########################################################################
# --- install all python dependencies for each part of the codebase --- #
#########################################################################

# NOTE: for sphinx to be able to render docs for a portion of the codebase,
# the dependencies of that codebase must be installed
#
WORKDIR /rootski

# prepare to install backend dependencies
RUN mkdir -p ./rootski_api/src/
COPY ./rootski_api/setup.cfg ./rootski_api/setup.py ./rootski_api/

# prepare to install infrastructure dependencies (package: backend)
RUN mkdir -p ./infrastructure/iac/aws-cdk/backend/
COPY ./infrastructure/iac/aws-cdk/backend/setup.py ./infrastructure/iac/aws-cdk/backend/
COPY ./infrastructure/iac/aws-cdk/backend/README.md ./infrastructure/iac/aws-cdk/backend/

# prepare to install infrastructure dependencies (package: cognito)
RUN mkdir -p ./infrastructure/iac/aws-cdk/cognito/cognito/
COPY ./infrastructure/iac/aws-cdk/cognito/setup.py ./infrastructure/iac/aws-cdk/cognito/
COPY ./infrastructure/iac/aws-cdk/cognito/README.md ./infrastructure/iac/aws-cdk/cognito/


WORKDIR /rootski/docs

# install all local python packages and all of their dependencies;
# sadly, this means that for us to be able to generate docs for a
# portion of the codebase, that portion must have NO dependency
# conflicts with any other portion. This is a tradeoff for generating
# a unified docs site for the entire codebase using sphinx. In the
# future, we may explore ways of building subprojects independently.
COPY ./docs/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./docs/Makefile ./Makefile

ENTRYPOINT ["make"]
CMD ["html"]
