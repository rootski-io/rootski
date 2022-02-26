import boto3
from botocore.client import BaseClient
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from textwrap import dedent
from typing import List, Optional, Union

#####################
# --- Constants --- #
#####################

# AWS credentials used to read/write to the database backup bucket
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
# Backup specific variables
BACKUP_BUCKET = os.environ["BACKUP_BUCKET"]
BACKUP_DIR = Path(os.environ["BACKUP_DIR"])
BACKUP_INTERVAL = os.environ["BACKUP_INTERVAL"]
# Postgres connection string
CONNECTION_STRING = "postgresql://{username}:{password}@{host}:{port}/{database}".format(
    username=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    database=os.environ["POSTGRES_DB"],
)
# Format for backup filenames
FILENAME_DATETIME_FORMAT = "rootski-db-%m-%d-%Y_%Hh-%Mm-%Ss.sql.gz"

############################
# --- Helper Functions --- #
############################


class DatabaseBackupNotFoundError(Exception):
    """Raised when when the specified backup object is not found in the S3 backups bucket."""


def parse_timedelta(time_str: str) -> timedelta:
    """Parse strings of the form "1d12h" or "1h30m" or "70s" into timedelta objects.

    :param time_str: the string to be parsed into a :class:timedelta object

    :return: returns a :class:'timedelta' object from the string representation
    """
    time_str_regex_pattern = re.compile(
        r"((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?"
    )

    parts = time_str_regex_pattern.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)


def run_shell_command(command: str, env_vars: dict):
    """Run a shell command and return the output.

    :param command: the command to be run
    :param env_vars: a dictionary of environment variables
    """

    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, env=env_vars)
    output, _ = process.communicate()
    print(output.decode("utf-8"))


###################
# --- Backup  --- #
###################


def make_backup_object_name_from_datetime() -> str:
    """Creates a string using the format specified by the FILENAME_DATETIME_FORMAT
    global variable for using as the filename of the backups.

    :return: the string to be used for the backup file name
    """
    return datetime.now().strftime(FILENAME_DATETIME_FORMAT)


def make_backup_fpath(object_name: str) -> Path:
    """Prepends the backup path to give a filepath for the object.

    :param object_name: the name of an object to which the BACKUP_DIR
        global variable should be prepended

    :return: returns a :class:'Path' object that gives a filepath
        for the 'object_name' file in the BACKUP_DIR directory
    """
    return BACKUP_DIR / object_name


def create_s3_session() -> boto3.session.Session:
    """Creates and returns an AWS session for listing and downloading backups in S3.

    :return: returns a :class:'boto3.session.Session' object using the AWS_ACCESS_KEY_ID
    and AWS_SECRET_ACCESS_KEY global variables that are set from the environment
    variables of the same name for interacting with AWS
    """
    sess = boto3.session.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    return sess


def create_s3_client() -> BaseClient:
    """Creates and returns an AWS S3 client for uploading backup to the cloud.

    :return: returns a :class:'BaseClient' object for uploading the backup
        file to AWS S3
    """
    sess = create_s3_session()
    return sess.client("s3")


def upload_backup_to_s3(
    s3_client: BaseClient,
    backup_fpath: Path,
    backup_bucket_name: str,
    backup_object_name: str,
):
    """Uploads the backup_fpath file to AWS S3.

    :param s3_client: an S3 client to use to upload the file
    :param backup_fpath: the filepath to the file that will be uploaded
    :param backup_bucket_name: the S3 bucket to upload the file to
    :param backup_object_name: the filename for the uploaded object in S3
    """
    with open(str(backup_fpath), "rb") as f:
        s3_client.upload_fileobj(Fileobj=f, Bucket=backup_bucket_name, Key=backup_object_name)


def delete_local_backup_file(backup_fpath: Path):
    """Deletes the local backup file once it has been uplaoded to S3.

    :param backup_fpath: the filepath to the file that will be deleted
    """
    os.remove(str(backup_fpath))


def backup_database(backup_object_name: str):
    """Creates a local backup of the database, uploades it to S3, and delets the local backup.

    :param backup_object_name: the name to be used for the backup file
    """
    # make sure the backup directory exists
    db_backup_gzip_fpath = make_backup_fpath(object_name=backup_object_name)
    db_backup_gzip_fpath.parent.mkdir(parents=True, exist_ok=True)

    # backup the database
    print("Creating the backup")

    # run the backup command
    backup_cmd = "pg_dumpall --dbname {conn_string} | gzip --stdout > {backup_fpath}".format(
        conn_string=CONNECTION_STRING, backup_fpath=db_backup_gzip_fpath
    )
    run_shell_command(command=backup_cmd, env_vars={"PGPASSWORD": os.environ["POSTGRES_PASSWORD"]})

    # upload the backup to S3
    print("Backing up the database as", backup_object_name, "to S3")
    s3_client = create_s3_client()  # s3_client: BaseClient = create_s3_client()
    upload_backup_to_s3(
        s3_client=s3_client,
        backup_fpath=db_backup_gzip_fpath,
        backup_bucket_name=BACKUP_BUCKET,
        backup_object_name=backup_object_name,
    )

    # delete local backup
    delete_local_backup_file(backup_fpath=db_backup_gzip_fpath)


def backup_database_on_interval(seconds: Union[int, float]):
    """Backs up the database to S3 repeatedly on an interval.

    :param seconds: the number of seconds to wait inbetween backups
    """
    print("Starting rootski backup daemon. Backups will run every {seconds}".format(seconds=seconds))
    print(
        "Backup interval in seconds is derived from {interval} found in BACKUP_INTERVAL".format(
            interval=BACKUP_INTERVAL
        )
    )
    while True:
        time.sleep(seconds)
        s3_backup_object_name = make_backup_object_name_from_datetime()
        backup_database(backup_object_name=s3_backup_object_name)


###################
# --- Restore --- #
###################


def download_backup_object(
    session: boto3.session.Session, backup_bucket_name: str, backup_object_name: str, backup_fpath: str
):
    """Downloads the object_name backup from the backup_bucket_name S3 bucket.

    :param session: the AWS session to be used for downloading the file
    :param backup_bucket_name: the name of the bucket to downlaod the file from
    :param backup_object_name: the name of the object to download
    :param backup_fpath: the filepath for the downloaded file
    """
    s3_client = session.client("s3")
    s3_client.download_file(Bucket=backup_bucket_name, Key=backup_object_name, Filename=backup_fpath)


def list_bucket_objects(session: boto3.session.Session, backup_bucket_name: str) -> List[str]:
    """Returns a list of all objects in the backup_bucket_name S3 bucket.

    :param session: the AWS session to be used for downloading the file
    :param backup_bucket_name: the name of the bucket to list the objects in

    :return: a list containing the names of all of the objects in the bucket
    """
    bucket = session.resource("s3").Bucket(name=backup_bucket_name)
    return [obj.key for obj in bucket.objects.all()]


def get_most_recent_backup_object_name(session: boto3.session.Session) -> str:
    """Returns the name of the most recent backup in S3.

    :param session: the AWS session to be used for listing all of the files in the
        AWS S3 bucket

    :return: the name of the most recent backup file in the S3 bucket
    """
    # get a list of all the backup files
    backup_files = list_bucket_objects(session=session, backup_bucket_name=BACKUP_BUCKET)

    # get the most recent backup file
    get_datetime_from_fpath = lambda fpath: datetime.strptime(fpath, FILENAME_DATETIME_FORMAT)
    most_recent_backup_fpath = max(backup_files, key=get_datetime_from_fpath)

    return most_recent_backup_fpath


def get_backup_object_name_to_restore_from(
    session: boto3.session.Session, backup_object_name__override: Optional[str]
) -> str:
    """Returns the name of the S3 backup to restore from. If an override is passed in,
    the function verifies that the backup exists in S3 or raises an error. Otherwise
    the function returns the name of the most recent backup in S3.

    :param session: the AWS session to be used to pulling a list of all of the objects
        in the S3 bucket
    :param backup_object_name__override: the name of a specific backup file in S3 to
        restore from

    :raises ClientError: if backup_object_name_to_restore_from__override is specified but
        is not in the database, this error will be thrown

    :return: the name of the S3 backup object to download and restore the database from
    """
    if backup_object_name__override is None:
        # get the name of the most recent backup object in S3
        backup_object_name_to_restore_from = get_most_recent_backup_object_name(session=session)
    else:
        # verify that the override backup exists
        s3_bucket_objects = list_bucket_objects(session=session, backup_bucket_name=BACKUP_BUCKET)
        if backup_object_name__override in s3_bucket_objects:
            backup_object_name_to_restore_from = backup_object_name__override
        else:
            raise DatabaseBackupNotFoundError(
                "No database backup was found in the {bucket_name} bucket with object name {backup_object_name}".format(
                    bucket_name=BACKUP_BUCKET, backup_object_name=backup_object_name__override
                )
            )
    return backup_object_name_to_restore_from


def restore_database(backup_object_name_to_restore_from__override: Optional[str] = None):
    """
    (1) drop the database
    (2) re-create it (but totally empty)
    (3) If `backup_object_name_to_restore_from__override` is `None`, restore from the most recent backup in S3. Otherwise, restore from specified backup stored in S3.

    :param backup_object_name_to_restore_from__override: the name of a specific backup
        the S3 bucket to restore from as an override for using the most recent backup
        , defaults to None
    """
    pg_env_vars = {"PGPASSWORD": os.environ["POSTGRES_PASSWORD"]}

    print("Dropping database {db_name}".format(db_name=os.environ["POSTGRES_DB"]))
    drop_db_cmd = "dropdb --host={host} --port={port} --username={user} {db_name}".format(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        user=os.environ["POSTGRES_USER"],
        db_name=os.environ["POSTGRES_DB"],
    )
    run_shell_command(command=drop_db_cmd, env_vars=pg_env_vars)

    print("Creating empty database {db_name}".format(db_name=os.environ["POSTGRES_DB"]))
    create_db_cmd = "createdb --host={host} --port={port} --username={user} {db_name}".format(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        user=os.environ["POSTGRES_USER"],
        db_name=os.environ["POSTGRES_DB"],
    )
    run_shell_command(command=create_db_cmd, env_vars=pg_env_vars)

    # find the most recent backup or verify the specify backup exists
    session = create_s3_session()
    backup_object_name_to_restore_from = get_backup_object_name_to_restore_from(
        session=session, backup_object_name__override=backup_object_name_to_restore_from__override
    )

    # download the backup
    print("Downloading backup file from S3")
    download_backup_object(
        session=session,
        backup_bucket_name=BACKUP_BUCKET,
        backup_object_name=backup_object_name_to_restore_from,
        backup_fpath=backup_object_name_to_restore_from,
    )

    # restore the database from a backup
    print("Restoring database from", backup_object_name_to_restore_from)
    restore_cmd = "gunzip --keep --stdout {backup_fpath} | psql --dbname {conn_string}".format(
        backup_fpath=backup_object_name_to_restore_from, conn_string=CONNECTION_STRING
    )
    run_shell_command(command=restore_cmd, env_vars=pg_env_vars)


######################
# --- Entrypoint --- #
######################


def main():
    print("System args:", sys.argv)
    print("Running database-backup process with subcommand", sys.argv[1])
    if sys.argv[1] == "backup":
        s3_backup_object_name = make_backup_object_name_from_datetime()
        backup_database(backup_object_name=s3_backup_object_name)
    elif sys.argv[1] == "backup-on-interval":
        backup_interval_seconds = parse_timedelta(time_str=BACKUP_INTERVAL).seconds
        backup_database_on_interval(seconds=backup_interval_seconds)
    elif sys.argv[1] == "restore-from-most-recent":
        restore_database()
    elif sys.argv[1] == "restore-from-backup":
        s3_backup_object_name_to_restore_from__override = sys.argv[2]
        restore_database(
            backup_object_name_to_restore_from__override=s3_backup_object_name_to_restore_from__override
        )

    else:
        print(
            dedent(
                """
        USAGE:

            python backup_or_restore.py <COMMAND> [ARGS...]

        ENVIRONMENT VARIABLES:

            BACKUP_DIR: the directory to store backups in

            BACKUP_INTERVAL: the interval to backup the database; can be numbered in
                any combination of hours, minutes, and seconds as long as
                they appear in that order (e.g. "1h30m", "70s", "2h15m")

            # connection details
            POSTGRES_USER
            POSTGRES_PASSWORD
            POSTGRES_HOST
            POSTGRES_PORT
            POSTGRES_DB

        COMMANDS:

            backup                    -- Backup the database to the BACKUP_DIR environment
                                         variable directory

            backup-on-interval        -- Run an immortal process that backs up the database
                                         every BACKUP_INTERVAL (backup behaviour is equivalent to
                                         the "backup" subcommand)

            restore-from-most-recent  -- Restore the database from the most recent backup in the
                                         BACKUP_DIR environment variable directory

            restore-from-backup <backup filename> -- Restore the database from the specified backup file
                                     <backup filename> should be one of the filenames in the BACKUP_DIR
        """
            )
        )


if __name__ == "__main__":
    main()
