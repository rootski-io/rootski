import logging
import os
import shutil
import tempfile

import mlflow

# removed from local disk after the run
ARTIFACTS_DIR = tempfile.mkdtemp(dir=".")

# configure logging both to file and stdout
LOGS_FPATH = os.path.join(ARTIFACTS_DIR, "run.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    filename=LOGS_FPATH,
    filemode="w",
)
stdout = logging.StreamHandler()
stdout.setLevel(logging.INFO)
LOGGER = logging.getLogger()
LOGGER.addHandler(stdout)


def main():
    with mlflow.start_run() as run:
        try:
            do_run(run)
        finally:
            # write logs to tracking server
            mlflow.log_artifact(LOGS_FPATH)

    # clean up all local artifacts
    shutil.rmtree(ARTIFACTS_DIR)


def do_run(run: mlflow.ActiveRun):

    mlflow.set_tag("implementation", "mine")

    LOGGER.info("Logging hyperparameters")
    mlflow.log_param("Batch Size", 2048)
    mlflow.log_param("Heads", 6)
    mlflow.log_param("Encoder Layers", 3)

    LOGGER.info("Beginning training")
    for loss in range(100):
        mlflow.log_metric("Training Loss", loss ** 2, step=loss)
        mlflow.log_metric("Validation Loss", 1.1 * loss ** 2, step=loss)

    LOGGER.info("Logging an artifact")
    sequence_artifact_path = os.path.join(ARTIFACTS_DIR, "sequence.txt")
    with open(sequence_artifact_path, "w") as file:
        file.write("приказать -> <bp> <mp> ...\n")
        file.write("TEXT!!!!")
    mlflow.log_artifact(sequence_artifact_path, "folder")

    mlflow.log_artifact("./setup.py")
    mlflow.log_artifact(local_path="/usr/src/app/requirements.txt", artifact_path="files")

    LOGGER.error("Logging an error")
    LOGGER.warning("Logging a warning")
    LOGGER.debug("LOgging a debug")


if __name__ == "__main__":
    main()
