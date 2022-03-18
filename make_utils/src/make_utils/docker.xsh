"""Utility functions for working with the docker CLI."""

import time
from pathlib import Path
import sys

# manually add ../make_utils/ to PYTHONPATH so we can import resources from make_utils
THIS_DIR = Path(__file__).parent.absolute()
MAKE_UTILS_DIR = (THIS_DIR / "..").resolve().absolute()
sys.path.insert(0, str(MAKE_UTILS_DIR))

from make_utils.utils_with_dependencies import MakeXshError, log

def container_is_healthy(container_id):
    """Return True if the container is healthy; False otherwise."""
    status = $(docker inspect -f '{{.State.Health.Status}}' @(container_id)).lower().strip()
    return status == "healthy"

def container_is_running(container_id):
    """Return True if the container is running; False otherwise."""
    return $(docker inspect -f '{{.State.Running}}' @(container_id)) == "true"

def await_docker_container_status(container_id, status="running", timeout=15):
    """
    a timeout error if the given container has not started running within the timeout limit.

    :param container_id: the container id to check
    :param status: the status to wait for. One of {"healthy", "running"}
    :raises TimeoutError: if the container has not met the desired status within the timeout limit
    """
    # validate parameters
    if status not in {"healthy", "running"}:
        ValueError(f"Invalid status: {status}. Must be one of ['healthy', 'running']")

    # determine which type of status to wait for
    status_check = {
        "healthy": container_is_healthy,
        "running": container_is_running,
    }[status]

    # wait for the status to be met or timeout
    for i in range(timeout):
        if status_check(container_id):
            return
        log(f"Waiting {i + 1}/{timeout}")
        time.sleep(1)
    MakeXshError(
        f"Timed out waiting for {container_id} to start up."
        + "\n\tBut docker can legitimately be slow sometimes. Try running this again OR "
        + "\n\ttry running 'docker ps' to check if the container is up manually AND/OR "
        + "\n\tuse the VS Code 'Docker' extension to browse your running/stopped containers"
        + "\n\tto check their logs for issues."
    )

def get_container_id_by_image(image_substr, wait=False, wait_timout_seconds=5):
    """Return the id of a container id whose image name matches :image_substr:"""
    start_time = time.time()
    for i in range(wait_timout_seconds):
        container_id = $(docker ps | grep @(image_substr) | awk '{ print $1 }').strip()
        if container_id != "":
            return container_id
        if not wait:
            MakeXshError(f"Failed to find container id for image substring '{image_substr}'")
        log(f"Waiting {i + 1}/{wait_timout_seconds}")
        time.sleep(1)
    MakeXshError(
        f"Timed out waiting for container id with image substring '{image_substr}'. "
        + "\n\tBut docker can legitimately be slow sometimes. Try running this again OR "
        + "\n\ttry running 'docker ps' to check if the container is up manually AND/OR "
        + "\n\tuse the VS Code 'Docker' extension to browse your running/stopped containers"
        + "\n\tto check their logs for issues."
    )
