import os
import tempfile

import mlflow

print("mlflow version:", mlflow.__version__)

mlflow.set_experiment("test")

with tempfile.TemporaryDirectory() as tmp_dir, mlflow.start_run() as run:
    # Added this line
    print("tracking uri:", mlflow.get_tracking_uri())
    print("artifact uri:", mlflow.get_artifact_uri())

    fname = "sample.txt"
    tmp_path = os.path.join(tmp_dir, fname)

    # create a text file to log
    with open(tmp_path, "w") as f:
        f.write("sample")

    # logging
    mlflow.log_param("p", 0)
    mlflow.log_metric("m", 1)
    mlflow.log_artifact(tmp_path, "files")
