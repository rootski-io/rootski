import json
import logging
from enum import Enum
from pathlib import Path
from time import sleep
from typing import Dict, Generator, List

import requests
from pyclickup import ClickUp
from pyclickup.models import List as ClickupList
from pyclickup.models import Space, Team, User
from requests.models import Response

#####################
# --- Constants --- #
#####################


THIS_DIR = Path(__file__).parent
API_KEY_FPATH = THIS_DIR / "api-key.txt"
USERS_JSON_FPATH = THIS_DIR / "users.json"
ONBOARDING_TASKS_MARKDOWN_DIR = THIS_DIR / "onboarding-tasks"
CREATED_TASKS_JSON_FPATH = THIS_DIR / "created-tasks.json"


###################
# --- Logging --- #
###################


def enable_thorough_requests_logging():
    """Causes detailed logs to emit for all calls to the requests library."""
    # These two lines enable debugging at httplib level (requests->urllib3->http.client)
    # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # The only thing missing will be the response.body which is not logged.
    try:
        import http.client as http_client
    except ImportError:
        # Python 2
        import httplib as http_client
    http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


###################
# --- ClickUp --- #
###################
class RootskiTaskStatus(str, Enum):
    """Map status names to IDs"""

    to_do = "to do"
    in_progress = "in progress"
    blocked = "blocked"
    in_review = "in review"
    done = "done"


class RootskiTag(str, Enum):
    business = "business/legal"
    ci_cd = "ci/cd"
    devops = "devops"
    mlops = "mlops"
    onboarding = "onboarding"
    ui_ux = "ui/ux"


def read_api_key() -> str:
    return API_KEY_FPATH.read_text().strip()


def get_clickup() -> ClickUp:
    return ClickUp(read_api_key())


def update_users_json(clickup: ClickUp):
    """Query all of the users, jsonify them, and write them to ``users.json``."""
    main_team: Team = clickup.teams[0]
    main_space: Space = main_team.spaces[0]
    members: List[User] = main_space.members
    users = {user["user"]["username"]: user for user in members}
    with open(USERS_JSON_FPATH, "w") as file:
        json.dump(users, file, indent=4)


def get_rootski_list(clickup: ClickUp) -> ClickupList:
    lists = clickup.teams[0].spaces[0].projects[0].lists
    rootski_list: ClickupList = lists[0]
    return rootski_list


def create_task(
    list_id: int,
    name: str,
    description: str,
    status: RootskiTaskStatus,
    assignees: List[int],
    token: str,
    tag: RootskiTag,
):
    """Create a task on the given list and assign it to the given assignees

    Args:
        list_id: list to create the task under
        name: name of the task, can be any string
        description: markdown description
        status: status like "in progress" or "to do"
        assignees: list of user id's
        token: api key
    """

    values = {
        "name": name,
        "markdown_description": description,
        "tags": [str(tag.value)],
        "status": str(status.value),
        # "due_date": 1508369194377,
        # "due_date_time": False,
        # "time_estimate": 8640000,
        # "start_date": 1567780450202,
        "start_date_time": False,
        "notify_all": False,
        "parent": None,
        "links_to": None,
        "check_required_custom_fields": True,
        "assignees": assignees,
    }

    headers = {"Authorization": token, "Content-Type": "application/json"}
    url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
    response: Response = requests.post(url, json=values, headers=headers)
    return response


def create_onboarding_tasks_for_user(
    user_id: str, rootski_list_id: int, token: str, delay_seconds: float = 0.0
):
    markdown_tasks: List[Dict[str, str]] = read_markdown_files(ONBOARDING_TASKS_MARKDOWN_DIR)
    for task in markdown_tasks:
        title = task["title"]
        markdown = task["markdown"]
        if not task_already_created(user_id=user_id, title=title):
            sleep(delay_seconds)
            print(f"creating task '{title}' for user {user_id}")
            create_task(
                list_id=rootski_list_id,
                name=title,
                description=markdown,
                status=RootskiTaskStatus.to_do,
                tag=RootskiTag.onboarding,
                assignees=[user_id],
                token=token,
            )
            document_task_creation(user_id=user_id, title=title)
        else:
            print(f"Skipping task '{title}' for user {user_id} because it already exists.")


###############################
# --- Task Creation State --- #
###############################


def get_username_by_id(user_id: str):
    users_json = json.loads(USERS_JSON_FPATH.read_text())
    user_id_to_username = {user_obj["user"]["id"]: username for username, user_obj in users_json.items()}
    return user_id_to_username[user_id]


def document_task_creation(title: str, user_id: str):
    if not CREATED_TASKS_JSON_FPATH.exists():
        CREATED_TASKS_JSON_FPATH.write_text("[]")

    created_tasks = json.loads(CREATED_TASKS_JSON_FPATH.read_text())
    created_tasks.append({"title": title, "user_id": user_id, "username": get_username_by_id(user_id)})
    CREATED_TASKS_JSON_FPATH.write_text(json.dumps(created_tasks, indent=4))


def task_already_created(title: str, user_id: str) -> bool:
    if not CREATED_TASKS_JSON_FPATH.exists():
        return False

    created_tasks: List[Dict[str, str]] = json.loads(CREATED_TASKS_JSON_FPATH.read_text())
    return any(title == task["title"] and user_id == task["user_id"] for task in created_tasks)


####################
# --- Markdown --- #
####################


def parse_markdown_title(markdown: str):
    return markdown.strip().splitlines()[0].strip("#").strip()


def parse_markdown_to_dict(markdown_fpath: Path):
    markdown = markdown_fpath.read_text()
    return {"title": parse_markdown_title(markdown), "markdown": markdown}


def read_markdown_files(markdown_dir: Path) -> List[Dict[str, str]]:
    """Read in the markdown templates.

    Return a list of dictionaries of the following form:

    {
        "title": "Task Title",
        "markdown": "# Markdown Contents!",
    }

    Args:
        markdown_dir: directory of the markdown files
    """
    markdown_fpaths: Generator[Path, None, None] = markdown_dir.glob("*.md")
    return [parse_markdown_to_dict(path) for path in markdown_fpaths]


if __name__ == "__main__":

    clickup: ClickUp = get_clickup()
    # rootski_list: ClickupList = get_rootski_list(clickup) # this takes like 4 queries
    # rootski_list_id = rootski_list.id

    enable_thorough_requests_logging()

    rootski_list_id = 138236644
    token = read_api_key()

    update_users_json(clickup=clickup)

    users = json.loads(USERS_JSON_FPATH.read_text())
    for username, user_obj in users.items():
        user_id = user_obj["user"]["id"]
        create_onboarding_tasks_for_user(
            user_id=user_id, rootski_list_id=rootski_list_id, token=token, delay_seconds=0.2
        )
