import os
import subprocess
import sys
import time
from datetime import datetime
from textwrap import dedent
from typing import List, Union

import boto3
from botocore.client import BaseClient

#####################
# --- Constants --- #
#####################

# AWS credentials used to read/write to the database backup bucket
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
# Backup specific variables
BACKUP_BUCKET = os.environ["BACKUP_BUCKET"]
BACKUP_DIR = os.environ["BACKUP_DIR"]
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
    """Raised when the specified backup object is not found in the S3 backups bucket."""


class InvalidBackupIntervalError(Exception):
    """Raised when the specified backup interval cannot be parsed onto a timedelta object."""


def parse_time_str(time_str: str) -> int:
    """Parse strings of the form "1d 12h" or "1h 30m" or "70s" into seconds.

    :param time_str: the string to be parsed into seconds

    :return: returns the time as the number of seconds
    """
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400}

    try:
        # Iterates over each part of the time_str and converts it to seconds
        seconds = 0
        for time_part in time_str.split():
            seconds += int(time_part[:-1]) * seconds_per_unit[time_part[-1]]
        return seconds
    except Exception:
        raise InvalidBackupIntervalError("The specified backup interval cannot be parsed.") from Exception


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
    """Return a string using the format specified by the FILENAME_DATETIME_FORMAT.

    This FILENAME_DATE_FORMAT is a global variable and the returned string will
    be used as the filename of the backups.

    :return: the string to be used for the backup file name
    """
    return datetime.now().strftime(FILENAME_DATETIME_FORMAT)


def make_backup_fpath(object_name: str) -> str:
    """Prepend the backup path to give a filepath for the object.

    :param object_name: the name of an object to which the BACKUP_DIR
        global variable should be prepended

    :return: returns a filepath for the 'object_name' file in the
        BACKUP_DIR directory
    """
    return "{backup_dir}/{object_name}".format(backup_dir=BACKUP_DIR, object_name=object_name)


def create_s3_session() -> boto3.session.Session:
    """Create and returns an AWS session for listing and downloading backups in S3.

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
    """Create and returns an AWS S3 client for uploading backup to the cloud.

    :return: returns a :class:'BaseClient' object for uploading the backup
        file to AWS S3
    """
    sess = create_s3_session()
    return sess.client("s3")


def upload_backup_to_s3(
    s3_client: BaseClient,
    backup_fpath: str,
    backup_bucket_name: str,
    backup_object_name: str,
):
    """Upload the backup_fpath file to AWS S3.

    :param s3_client: an S3 client to use to upload the file
    :param backup_fpath: the filepath to the file that will be uploaded
    :param backup_bucket_name: the S3 bucket to upload the file to
    :param backup_object_name: the filename for the uploaded object in S3
    """
    with open(backup_fpath, "rb") as file:
        s3_client.upload_fileobj(Fileobj=file, Bucket=backup_bucket_name, Key=backup_object_name)


def delete_local_backup_file(backup_fpath: str):
    """Delete the local backup file once it has been uplaoded to S3.

    :param backup_fpath: the filepath to the backup that will be deleted
    """
    os.remove(backup_fpath)


def backup_database(backup_object_fpath: str):
    """Create a local backup of the database that can be uploaded to S3 or kept locally.

    :param backup_object_fpath: the filepath to backup the database to
    """
    print("Creating the backup")

    # run the backup command
    backup_cmd = "pg_dumpall --dbname {conn_string} | gzip --stdout > {backup_fpath}".format(
        conn_string=CONNECTION_STRING, backup_fpath=backup_object_fpath
    )
    run_shell_command(command=backup_cmd, env_vars={"PGPASSWORD": os.environ["POSTGRES_PASSWORD"]})


def upload_backup_to_s3_and_delete(backup_object_fpath: str, backup_object_name: str):
    """Upload the local backup file to S3 and delete it.

    :param backup_object_fpath: the filepath to the local copy of the backup to upload to S3
    :param backup_object_name: the name to be used for the backup file in S3
    """
    # upload the backup to S3
    print("Backing up the database as", backup_object_name, "to S3")
    s3_client = create_s3_client()  # s3_client: BaseClient = create_s3_client()
    upload_backup_to_s3(
        s3_client=s3_client,
        backup_fpath=backup_object_fpath,
        backup_bucket_name=BACKUP_BUCKET,
        backup_object_name=backup_object_name,
    )

    # delete local backup
    print("Backup uploaded to S3. Deleting local copy")
    delete_local_backup_file(backup_fpath=backup_object_fpath)


def backup_database_to_s3():
    """Back up the database to S3 repeatedly on an interval."""
    s3_backup_object_name = make_backup_object_name_from_datetime()
    backup_object_to_upload_fpath = make_backup_fpath(object_name=s3_backup_object_name)
    backup_database(backup_object_fpath=backup_object_to_upload_fpath)
    upload_backup_to_s3_and_delete(
        backup_object_fpath=backup_object_to_upload_fpath, backup_object_name=s3_backup_object_name
    )


def backup_database_on_interval(seconds: Union[int, float]):
    """Back up the database to S3 repeatedly on an interval.

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
        backup_database_to_s3()


###################
# --- Restore --- #
###################


def download_backup_object(
    session: boto3.session.Session, backup_bucket_name: str, backup_object_name: str, backup_fpath: str
):
    """Download the object_name backup from the backup_bucket_name S3 bucket.

    :param session: the AWS session to be used for downloading the file
    :param backup_bucket_name: the name of the bucket to downlaod the file from
    :param backup_object_name: the name of the object to download
    :param backup_fpath: the filepath for the downloaded file
    """
    s3_client = session.client("s3")
    s3_client.download_file(Bucket=backup_bucket_name, Key=backup_object_name, Filename=backup_fpath)


def list_bucket_objects(session: boto3.session.Session, backup_bucket_name: str) -> List[str]:
    """Return a list of all objects in the backup_bucket_name S3 bucket.

    :param session: the AWS session to be used for downloading the file
    :param backup_bucket_name: the name of the bucket to list the objects in

    :return: a list containing the names of all of the objects in the bucket
    """
    bucket = session.resource("s3").Bucket(name=backup_bucket_name)
    return [obj.key for obj in bucket.objects.all()]


def get_datetime_from_fpath(
    backup_object_name: str, datetime_format: str = FILENAME_DATETIME_FORMAT
) -> datetime:
    """Return a datetime object from a string of the FILENAME_DATETIME_FORMAT.

    :param fpath: the backup_object_name to extract the datetime from
    :param datetime_format: the datetime formatting string used to create and in this case
        decode the backup file names, defaults to the FILENAME_DATETIME_FORMAT global variable

    :return: a datetime object for when the backup was created
    """
    return datetime.strptime(backup_object_name, datetime_format)


def get_most_recent_backup_object_name(session: boto3.session.Session) -> str:
    """Return the name of the most recent backup in S3.

    :param session: the AWS session to be used for listing all of the files in the
        AWS S3 bucket

    :return: the name of the most recent backup file in the S3 bucket
    """
    # get a list of all the backup files
    backup_files = list_bucket_objects(session=session, backup_bucket_name=BACKUP_BUCKET)

    # get the most recent backup file
    most_recent_backup_fpath = max(backup_files, key=get_datetime_from_fpath)

    return most_recent_backup_fpath


def restore_database_from_most_recent_s3_backup():
    """Download the most recent S3 backup and restore the database from it.

    (1) find the most recent backup object in the S3 BACKUP_BUCKET bucket
    (2) download the most recent backup object
    (3) call restore_database_from_backup() func to restore the database from the backup
    """
    # find the most recent backup
    session = create_s3_session()
    backup_object_name_to_restore_from = get_most_recent_backup_object_name(session=session)

    # download the backup
    print("Downloading backup object from S3")
    download_backup_object(
        session=session,
        backup_bucket_name=BACKUP_BUCKET,
        backup_object_name=backup_object_name_to_restore_from,
        backup_fpath=backup_object_name_to_restore_from,
    )

    # restore the database from the backup
    restore_database_from_backup(backup_to_restore_from_fpath=backup_object_name_to_restore_from)


def restore_database_from_backup(backup_to_restore_from_fpath: str):
    """Restore the database from a specified backup file.

    (1) drop the database
    (2) re-create it (but totally empty)
    (3) restore the database from the `backup_to_restore_from_fpath` backup

    :param backup_to_restore_from_fpath: the filepath to the .gz filtype backup to
        restore from
    """
    # this allows running cli commands against the database without manually entering the password
    pg_env_vars = {"PGPASSWORD": os.environ["POSTGRES_PASSWORD"]}

    # Drop any existing $POSTGRES_DB databse
    print("Dropping database {db_name}".format(db_name=os.environ["POSTGRES_DB"]))
    drop_db_cmd = "dropdb --host={host} --port={port} --username={user} {db_name}".format(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        user=os.environ["POSTGRES_USER"],
        db_name=os.environ["POSTGRES_DB"],
    )
    run_shell_command(command=drop_db_cmd, env_vars=pg_env_vars)

    # Create a new and empty $POSTGRES_DB database to be restored
    print("Creating empty database {db_name}".format(db_name=os.environ["POSTGRES_DB"]))
    create_db_cmd = "createdb --host={host} --port={port} --username={user} {db_name}".format(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        user=os.environ["POSTGRES_USER"],
        db_name=os.environ["POSTGRES_DB"],
    )
    run_shell_command(command=create_db_cmd, env_vars=pg_env_vars)

    # Restore the $POSTGRES_DB from the specified backup file
    print("Restoring database from", backup_to_restore_from_fpath)
    restore_cmd = "gunzip --keep --stdout {backup_fpath} | psql --dbname {conn_string}".format(
        backup_fpath=backup_to_restore_from_fpath, conn_string=CONNECTION_STRING
    )
    print(restore_cmd)
    run_shell_command(command=restore_cmd, env_vars=pg_env_vars)

    print("Successfully restored database")

######################
# --- Entrypoint --- #
######################


def main():
    print("System args:", sys.argv)
    print("Running database-backup process with subcommand", sys.argv[1])
    if sys.argv[1] == "backup-database-to-s3":
        backup_database_to_s3()
    elif sys.argv[1] == "backup-database-to-s3-on-interval":
        backup_interval_seconds = parse_time_str(time_str=BACKUP_INTERVAL)
        backup_database_on_interval(seconds=backup_interval_seconds)
    elif sys.argv[1] == "restore-database-from-most-recent-s3-backup":
        restore_database_from_most_recent_s3_backup()
    elif sys.argv[1] == "backup-database-locally":
        backup_fpath = BACKUP_DIR + "/rootski-db-dev-backup.sql.gz"
        backup_database(backup_object_fpath=backup_fpath)
    elif sys.argv[1] == "restore-database-from-local-backup":
        local_backup_to_restore_from_fpath = BACKUP_DIR + "/rootski-db-dev-backup.sql.gz"
        restore_database_from_backup(backup_to_restore_from_fpath=local_backup_to_restore_from_fpath)
    else:
        print(
            dedent(
                """
                USAGE:

                    python backup_or_restore.py <COMMAND> [ARGS...]

                ENVIRONMENT VARIABLES:

                    BACKUP_BUCKET: the S3 bucket that contains the database backups
                    BACKUP_DIR: the directory to store backups in
                    BACKUP_INTERVAL: the interval to backup the database; can be numbered in
                        any combination of hours, minutes, and seconds as long as
                        they appear in that order (e.g. "1h30m", "70s", "2h15m")

                    # connection details
                    POSTGRES_USER: {postgres_user}
                    POSTGRES_PASSWORD: {postgres_password}
                    POSTGRES_HOST: {postgres_host}
                    POSTGRES_PORT: {postgres_port}
                    POSTGRES_DB: {postgres_db}

                COMMANDS:

                    backup-database-to-s3
                        -- Backup the database to the BACKUP_BUCKET S3 bucket

                    backup-database-to-s3-on-interval
                        -- Run an immortal process that backs up the database to S3
                        every BACKUP_INTERVAL (backup behaviour is equivalent to
                        the "backup-database-to-s3" subcommand)

                    restore-database-from-most-recent-s3-backup
                        -- Restore the database from the most recent
                        backup in the BACKUP_BUCKET S3 bucket

                    backup-database-locally
                        -- Backup the database to a local file

                    restore-database-from-local-backup
                        -- Restore the database from the backup located at
                        infrastructure/containers/postgres/backups/rootski-db-dev-backup.sql.gz.

                """.format(
                    postgres_user=os.environ["POSTGRES_USER"],
                    postgres_password=os.environ["POSTGRES_PASSWORD"],
                    postgres_host=os.environ["POSTGRES_HOST"],
                    postgres_port=os.environ["POSTGRES_PORT"],
                    postgres_db=os.environ["POSTGRES_DB"],
                )
            )
        )


if __name__ == "__main__":
    main()
