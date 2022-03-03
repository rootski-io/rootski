# The context for this file needs to be path/to/rootski_api
FROM python:3.9.6-slim-buster

RUN apt-get update && apt-get -y install git make
# RUN apt-get -y install git
WORKDIR /usr/src/rootski_api
COPY . .
# needs to be a git repository in order for "pip install ." type commands to work
RUN git init \
    && git config --global user.email "banana-man@rootski.io" \
    && git config --global user.name "Banana man" \
    && git add version.txt \
    && git commit -m "initial commit"
RUN make install
