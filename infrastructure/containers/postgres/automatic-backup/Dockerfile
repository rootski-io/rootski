# Note: be sure the postgres image tag matches
# the one used to run the database
FROM postgres:9.6

# install python and pip
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:fkrull/deadsnakes
RUN apt-get install -y python3 python3-pip curl
RUN apt-get install -y zip

# install script dependencies
RUN python3 -m pip install boto3 xonsh

WORKDIR /app

COPY backup_or_restore.py ./backup_or_restore.py

ENTRYPOINT ["python3", "-m", "xonsh", "backup_or_restore.py"]
CMD ["backup-on-interval"]
