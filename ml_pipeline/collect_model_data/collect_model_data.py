"""
Collect the word breakdowns data and put it in a csv file that can be ingested by the model.

This file uses the following global variables:
AWS_ACCESS_KEY_ID - Access key for uploading csv file to S3
AWS_SECRET_ACCESS_KEY - Secret Access key for uploading csv file to S3
BACKUP BUCKET - The name of the S3 bucket to upload the csv to
FILENAME_DATETIME_FORMAT - The formatting string for the name of the csv files
"""

import os

from rootski_models.models import Breakdown, BreakdownItem
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# AWS credentials used to read/write to the database backup bucket
# AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
# AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
# Backup specific variables
# BACKUP_BUCKET = os.environ["BACKUP_BUCKET"]
# Format for backup filenames
FILENAME_DATETIME_FORMAT = "training-data-%m-%d-%Y_%Hh-%Mm-%Ss.csv"


# def create_s3_client() -> BaseClient:
#     """Create and returns an AWS S3 client for uploading backup to the cloud.

#     :return: returns a :class:'BaseClient' object for uploading the backup
#         file to AWS S3
#     """
#     sess = create_s3_session()
#     return sess.client("s3")


# def upload_data_to_s3(
#     s3_client: BaseClient,
#     data_fpath: str,
#     data_bucket_name: str,
#     data_object_name: str,
# ):
#     """Upload the backup_fpath file to AWS S3.

#     :param s3_client: an S3 client to use to upload the file
#     :param backup_fpath: the filepath to the file that will be uploaded
#     :param backup_bucket_name: the S3 bucket to upload the file to
#     :param backup_object_name: the filename for the uploaded object in S3
#     """
#     with open(backup_fpath, "rb") as file:
#         s3_client.upload_fileobj(Fileobj=file, Bucket=backup_bucket_name, Key=backup_object_name)


def get_db_connection_string_from_env_vars() -> str:
    """Create the database connection string using the environment variables in the docker container."""
    db_connection_str = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        database=os.environ["POSTGRES_DB"],
    )
    return db_connection_str


def get_breakdowns_data_from_db():
    """Retrieve the breakdowns data from the database."""
    connection_string = get_db_connection_string_from_env_vars()
    engine = create_engine(connection_string, echo=True)

    with open("breakdowns_data_for_model.csv", "w", encoding="utf-8") as data_file:
        with Session(engine) as session:
            prev_word = ""
            breakdown_str = ""
            word_from_breakdown = ""
            for row in (
                session.query(Breakdown, BreakdownItem)
                .join(BreakdownItem, Breakdown.breakdown_id == BreakdownItem.breakdown_id)
                .filter(Breakdown.breakdown_id is not None)
                .filter(Breakdown.word is not None)
                .order_by(Breakdown.breakdown_id, BreakdownItem.position)
                .all()
            ):
                if row.Breakdown.word == prev_word:
                    if row.BreakdownItem.type is not None:
                        breakdown_str += f"{row.BreakdownItem.morpheme}:{row.BreakdownItem.type}/"
                    else:
                        breakdown_str += f"{row.BreakdownItem.morpheme}:null/"
                    word_from_breakdown += row.BreakdownItem.morpheme
                    if word_from_breakdown == row.Breakdown.word.replace("-", ""):
                        breakdown_str = breakdown_str[:-1] + "\n"
                        data_file.write(breakdown_str)
                else:
                    prev_word = row.Breakdown.word
                    breakdown_str = ""
                    word_from_breakdown = ""
                    if row.BreakdownItem.type is not None:
                        breakdown_str += f"{row.BreakdownItem.morpheme}:{row.BreakdownItem.type}/"
                    else:
                        breakdown_str += f"{row.BreakdownItem.morpheme}:null/"
                    word_from_breakdown += row.BreakdownItem.morpheme


if __name__ == "__main__":
    get_breakdowns_data_from_db()
