import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from textwrap import dedent

#####################
# --- Constants --- #
#####################

BACKUP_DIR = Path(os.environ["BACKUP_DIR"])
BACKUP_INTERVAL = os.environ["BACKUP_INTERVAL"]
CONNECTION_STRING = "postgresql://{username}:{password}@{host}:{port}/{database}".format(
    username=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    database=os.environ["POSTGRES_DB"],
)
FILENAME_DATETIME_FORMAT = "rootski-db-%m-%d-%Y_%Hh-%Mm-%Ss.sql.gz"

############################
# --- Helper Functions --- #
############################


def parse_timedelta(time_str):
    """Parse strings of the form "1d12h" or "1h30m" or "70s" into timedelta objects."""
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


def run_shell_command(command, env_vars):
    """Run a shell command and return the output."""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, env=env_vars)
    output, _ = process.communicate()
    print(output.decode("utf-8"))


###################
# --- Backup  --- #
###################


def make_backup_fpath():
    return BACKUP_DIR / datetime.now().strftime(FILENAME_DATETIME_FORMAT)


def backup_database(db_backup_gzip_fpath):
    # make sure the backup directory exists
    db_backup_gzip_fpath.parent.mkdir(parents=True, exist_ok=True)

    # backup the database
    print("Backing up database to", db_backup_gzip_fpath)

    # run the backup command
    backup_cmd = (
        "pg_dumpall --dbname {conn_string} --clean --if-exists | gzip --stdout > {backup_fpath}".format(
            conn_string=CONNECTION_STRING, backup_fpath=db_backup_gzip_fpath
        )
    )
    run_shell_command(backup_cmd, env_vars={"PGPASSWORD": os.environ["POSTGRES_PASSWORD"]})


def backup_database_on_interval(seconds):
    print("Starting rootski backup daemon. Backups will run every {seconds}".format(seconds=seconds))
    print(
        "Backup interval in seconds is derived from {interval} found in BACKUP_INTERVAL".format(
            interval=BACKUP_INTERVAL
        )
    )
    while True:
        time.sleep(seconds)
        backup_database(make_backup_fpath())


###################
# --- Restore --- #
###################


def get_most_recent_backup_fpath():
    # get a list of all the backup files
    backup_files = BACKUP_DIR.glob("*.sql.gz")

    # get the most recent backup file
    get_datetime_from_fpath = lambda fpath: datetime.strptime(str(fpath.name), FILENAME_DATETIME_FORMAT)
    most_recent_backup_fpath = max(backup_files, key=get_datetime_from_fpath)

    return most_recent_backup_fpath


def restore_database(backup_fpath):
    """
    (1) drop the database
    (2) re-create it (but totally empty)
    (3) restore from the backup at backup_fpath
    """

    pg_env_vars = {"PGPASSWORD": os.environ["POSTGRES_PASSWORD"]}

    print("Dropping database {db_name}".format(db_name=os.environ["POSTGRES_DB"]))
    drop_db_cmd = "dropdb --host={host} --port={port} --username={user} {db_name}".format(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        user=os.environ["POSTGRES_USER"],
        db_name=os.environ["POSTGRES_DB"],
    )
    run_shell_command(drop_db_cmd, env_vars=pg_env_vars)

    print("Creating empty database {db_name}".format(db_name=os.environ["POSTGRES_DB"]))
    create_db_cmd = "createdb --host={host} --port={port} --username={user} {db_name}".format(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        user=os.environ["POSTGRES_USER"],
        db_name=os.environ["POSTGRES_DB"],
    )
    run_shell_command(create_db_cmd, env_vars=pg_env_vars)

    # restore the database from a backup
    print("Restoring database from", backup_fpath)
    restore_cmd = "gunzip --keep --stdout {backup_fpath} | psql --dbname {conn_string}".format(
        backup_fpath=backup_fpath, conn_string=CONNECTION_STRING
    )
    run_shell_command(restore_cmd, env_vars=pg_env_vars)


######################
# --- Entrypoint --- #
######################


def main():
    print("Running database-backup process with subcommand", sys.argv[1])
    if sys.argv[1] == "backup":
        backup_database(make_backup_fpath())
    elif sys.argv[1] == "backup-on-interval":
        backup_interval_seconds = parse_timedelta(BACKUP_INTERVAL).seconds
        backup_database_on_interval(seconds=backup_interval_seconds)
    elif sys.argv[1] == "restore-from-most-recent":
        restore_database(get_most_recent_backup_fpath())
    elif sys.argv[1] == "restore-from-backup":
        backup_fpath = BACKUP_DIR / sys.argv[2]
        restore_database(backup_fpath)
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
