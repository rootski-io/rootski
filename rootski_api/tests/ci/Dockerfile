# The context for this file needs to be path/to/rootski_api
FROM python:3.9.6-slim-buster

RUN apt-get update && apt-get -y install git make
# RUN apt-get -y install git
WORKDIR /usr/src/rootski_api
COPY . .
RUN make install