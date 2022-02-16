#
# Dockerfile created by following official FastAPI tutorial:
# https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker
#
# Usage:
#     Build Args:
#         ROOTSKI_API_BUILD:
#             Should be one of two things:
#             (1) "" (default) an empty string. Only installs production dependencies.
#             (2) "[all]" installs testing/linting/database dependencies in addition
#                 to produciton dependencies.
#
#     Volumes:
#          /usr/src/app - the contents of the rootski_api/ folder
#
#     Manually Build, Run, and Attach:
#          # from rootski_api/
#          docker build -t rootski_api --build-arg="[all]" .
#          docker run --rm -v "$PWD":/usr/src/app/rootski_api \
#              -it --entrypoint /bin/bash rootski_api

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ARG ROOTSKI_EXTRAS=""

WORKDIR /usr/src/rootski

# install rootski dependencies
COPY setup.cfg setup.py ./
RUN mkdir -p src
RUN pip install -U pip
RUN python3 -m pip install -e .${ROOTSKI_EXTRAS}

# copy in the code base
COPY . .

ENV ROOTSKI__NUM_WORKERS=1
ENV ROOTSKI__HOST="0.0.0.0"
ENV ROOTSKI__PORT="80"

# CMD uvicorn "rootski.main.main:create_default_app" --factory --workers ${NUM_WORKERS} --host ${ROOTSKI__HOST} --port ${ROOTSKI__PORT}

# fastapi recommends using gunicorn if you can:
# https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#gunicorn
CMD gunicorn "rootski.main.main:create_default_app()" \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers ${ROOTSKI__NUM_WORKERS} \
    --bind ${ROOTSKI__HOST}:${ROOTSKI__PORT} \
    --reload
