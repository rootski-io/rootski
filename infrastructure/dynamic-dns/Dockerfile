# This docker image is meant to be used for DynamicDNS on
#
# (1) The VPN server
# (2) The on-prem server
# (3) The EC2 spot instance

FROM python:3.9-slim-buster

RUN pip install xonsh

ENV TEMP_DIR="aws_cli_artifacts"
ENV AWSCLI_INSTALL_BINARIES_ZIP_FPATH="${TEMP_DIR}/aws-cli-v2.zip"

RUN apt-get update \
    && apt-get install -y curl zip

RUN mkdir -p ${TEMP_DIR} \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" \
        -o ${AWSCLI_INSTALL_BINARIES_ZIP_FPATH} \
    && unzip ${AWSCLI_INSTALL_BINARIES_ZIP_FPATH} -d ${TEMP_DIR} \
    && /bin/bash "${TEMP_DIR}/aws/install" \
    && rm -rf ${TEMP_DIR}

RUN aws
