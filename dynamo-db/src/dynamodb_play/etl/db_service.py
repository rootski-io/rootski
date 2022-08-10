import os
from pathlib import Path

import dotenv
from rootski.config import Config
from rootski.services.database.database import DBService

THIS_DIR = Path(__file__).parent
DEV_DOT_ENV_FPATH = THIS_DIR / "../../../../dev.env"


def get_dbservice() -> DBService:
    dotenv.load_dotenv(dotenv_path=DEV_DOT_ENV_FPATH)
    os.environ["ROOTSKI__POSTGRES_HOST"] = "localhost"
    config = Config(
        # postgres_host="database.Rootski.io"
        postgres_host="192.168.12.175",
        cognito_aws_region="doesn't matter",
        cognito_user_pool_id="doesn't matter",
        cognito_web_client_id="doesn't matter",
    )
    db_service = DBService.from_config(config)
    db_service.init()

    return db_service


if __name__ == "__main__":
    get_dbservice()
