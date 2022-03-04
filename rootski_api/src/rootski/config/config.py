"""
Configuration handler for the API. The philosophies for how
Rootski handles configuration come from the "12-Factor App".

All configuration values can come from the following sources, and will
be prioritized in the following order:

1. CLI arguments (unused in this app)
2. Environment variables
3. Config file
4. Default values

.. note::
    If the name of a config value in the YAML file is "name", then
    the environment variable equivalent will be ROOTSKI__NAME.
"""

import json
import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import yaml
from pydantic import AnyHttpUrl, BaseSettings, validator
from pydantic.dataclasses import dataclass
from pydantic.env_settings import SettingsSourceCallable
from rootski.config.ssm import get_ssm_parameters_by_prefix

ANON_USER = "anon@rootski.io"
ENVIRON_PREFIX: str = "ROOTSKI__"

# default config values

#: default port for the FastAPI server to listen on
DEFAULT_PORT: int = 3333
#: default host for the FastAPI server to listen on
DEFAULT_HOST: str = "0.0.0.0"
#: default domain for the API (used for CORS and may be for other things)
DEFAULT_DOMAIN: str = "www.rootski.io"
#: default http:// URL of the S3 bucket containing the static frontend files
DEFAULT_S3_STATIC_SITE_DOMAIN = "http://io.rootski.www.s3-website-us-west-2.amazonaws.com"
#: environment variable where the rootski API config file should be found
YAML_CONFIG_PATH_ENV_VAR: str = f"{ENVIRON_PREFIX}CONFIG_FILE_PATH"

# we expect this to be one of "dev" or "prod"
DEPLOYMENT_ENVIRONMENT_ENV_VAR = f"{ENVIRON_PREFIX}ENVIRONMENT"
DEFAULT_DEPLOYMENT_ENVIRONMENT = "dev"

# maps to a string boolean
FETCH_VALUES_FROM_SSM_ENV_VAR = f"{ENVIRON_PREFIX}FETCH_VALUES_FROM_AWS_SSM"


#########################################################
# --- Helper functions to set Rootski config values --- #
#########################################################


def get_environ_name(name: str) -> str:
    """Get the environment variable name for a given config value."""
    return f"{ENVIRON_PREFIX}{name.upper()}"


def load_config_from_yaml(config_fpath: str) -> Dict[str, str]:
    """Read config from a YAML file."""
    with Path(config_fpath).open("r") as f:
        config = yaml.safe_load(f)
    return config


##########################
# --- Rootski Config --- #
##########################


def yaml_config_settings_source(settings: "Config") -> Dict[str, Any]:
    """App settings from the yaml config file."""
    yaml_config_path = os.environ.get(YAML_CONFIG_PATH_ENV_VAR)
    if not yaml_config_path:
        return {}
    return load_config_from_yaml(config_fpath=yaml_config_path) if yaml_config_path else {}


def aws_parameter_store_settings_source(settings: "Config") -> Dict[str, Any]:
    """
    Fetch app settings from AWS SSM Parameter Store.

    If a previous settings provider has set the ``fetch_values_from_ssm`` value to ``False``,
    this function will not attempt to fetch values from SSM.
    """
    fetch_values_from_aws_ssm: bool = os.environ.get(FETCH_VALUES_FROM_SSM_ENV_VAR, "false").lower() == "true"
    if not fetch_values_from_aws_ssm:
        return {}

    deployment_environment = os.environ.get(DEPLOYMENT_ENVIRONMENT_ENV_VAR, DEFAULT_DEPLOYMENT_ENVIRONMENT)
    rootski_params: Dict[str, str] = get_ssm_parameters_by_prefix(prefix=f"/rootski/{deployment_environment}/")

    to_return: Dict[str, str] = {}
    if "database_config" in rootski_params.keys():
        database_config = json.loads(rootski_params["database_config"])
        to_return.update(
            {
                "postgres_user": database_config["postgres_user"],
                "postgres_password": database_config["postgres_password"],
                "postgres_host": database_config["postgres_host"],
                "postgres_port": database_config["postgres_port"],
                "postgres_db": database_config["postgres_db"],
            }
        )

    def update__to_return__if_key_present_in__rootski_params(key: str):
        if key in rootski_params.keys():
            to_return[key] = rootski_params[key]

    for key in ["cognito_aws_region", "cognito_user_pool_id", "cognito_web_client_id"]:
        update__to_return__if_key_present_in__rootski_params(key)

    return to_return


def default_settings(settings: "Config") -> Dict[str, Any]:
    """Default values for certain app settings."""
    # these keys must be named the same as the attributes in the
    # Config class below
    return {
        # "s3_static_site_origin": DEFAULT_S3_STATIC_SITE_DOMAIN,
        "host": DEFAULT_HOST,
        "port": DEFAULT_PORT,
        "domain": DEFAULT_DOMAIN,
        "extra_allowed_cors_origins": [],
    }


class LogLevel(str, Enum):
    """Logging levels."""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"


@dataclass(frozen=True)
class Config(BaseSettings):
    """A configuration manager for the app.

    Configuration values are discovered and kept in the following order of priority:

    1. Init arguments (could be used to give CLI arguments highest priority)
    2. Environment variables of the form ``<ENVIRON_PREFIX>UPPER_CASE_ATTRIBUTE``
    3. Config yaml file, whose location is at ``<ENVIRON_PREFIX>CONFIG_FILE_PATH``
    4. Default values set in this ``dataclass``

    .. note::

        When using environment variables, values should be JSON formatted strings.
        For example, ``"link1,link2,link3"`` would fail for ``extra_allowed_cors_origins``,
        but ``'["link1", "link2", "link3"]'`` would work.

    .. note::

        This ``__init__()`` method only exists so that there is a class-level
        docstring in the sphinx documentation.
    """

    log_level: LogLevel = LogLevel.INFO.value

    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    domain: str = DEFAULT_DOMAIN
    s3_static_site_origin: str = DEFAULT_S3_STATIC_SITE_DOMAIN
    cognito_aws_region: str
    cognito_user_pool_id: str
    cognito_web_client_id: str

    static_assets_dir: str = str((Path(__file__).parent / "../../../static").resolve())

    extra_allowed_cors_origins: List[AnyHttpUrl] = []

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_db: str

    @property
    def sync_sqlalchemy_database_uri(self) -> str:
        return f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def async_sqlalchemy_database_uri(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def static_morphemes_json_fpath(self) -> Path:
        return Path(self.static_assets_dir) / "morphemes.json"

    # TODO - uncomment these; unfortunately, as of Nov 1, 2021, pydantic does not support
    # "postgressql+psycopg2" or "postgresql+asyncpg" as schemas for the PostgresDsn. This
    # is coming in the next release, but when I installed the latest release from GitHub
    # many other portions of the app broke, so for now, these will be constructed using
    # properties

    # @validator("sync_sqlalchemy_database_uri", pre=True)
    # def assemble_sync_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
    #     """Simultaneously validate db connection params and build the connection string."""
    #     if isinstance(v, str):
    #         return v
    #     return PostgresDsn.build(
    #         scheme="postgresql+psycopg2",
    #         user=values.get("postgres_user"),
    #         password=values.get("postgres_password"),
    #         host=values.get("postgres_host"),
    #         port=values.get("postgres_port"),
    #         path=f"/{values.get('postgres_db') or ''}",
    #     )

    # @validator("async_sqlalchemy_database_uri", pre=True)
    # def assemble_async_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
    #     """Simultaneously validate db connection params and build the connection string."""
    #     if isinstance(v, str):
    #         return v
    #     return PostgresDsn.build(
    #         scheme="postgresql+asyncpg",
    #         user=values.get("postgres_user"),
    #         password=values.get("postgres_password"),
    #         host=values.get("postgres_host"),
    #         port=values.get("postgres_port"),
    #         path=f"/{values.get('postgres_db') or ''}",
    #     )

    @property
    def allowed_cors_origins(self) -> List[AnyHttpUrl]:
        return self.extra_allowed_cors_origins + [
            self.s3_static_site_origin,
            f"http://localhost:{self.port}",
            f"https://localhost:{self.port}",
            f"https://{self.domain}",
        ]

    @property
    def cognito_public_keys_url(self) -> str:
        """URL of Cognito public keys used to validate cognito issued JWT tokens for the Rootski user pool."""
        return f"https://cognito-idp.{self.cognito_aws_region}.amazonaws.com/{self.cognito_user_pool_id}/.well-known/jwks.json"

    @validator("extra_allowed_cors_origins", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Ensure ``extra_allowed_cors_origins`` is a valid list of strings.
        Parse it from a str to a List[str] if needed."""
        # parse comma separated strings to List[str]
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_prefix = ENVIRON_PREFIX
        case_sensitive = False
        use_enum_values = True

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            """Register settings providers.

            Config providers will be prioritized in the order they are returned here."""
            return (
                init_settings,  # kwargs to Config() constructor
                env_settings,  # environment variable versions of config values
                yaml_config_settings_source,  # values from yaml file
                aws_parameter_store_settings_source,  # values from ssm parameter store
                file_secret_settings,  # ???
            )

    def __init__(self, **kwargs):
        # The tests seem to fail without this empty __init__
        # pylint: disable=useless-super-delegation
        super().__init__(**kwargs)


if __name__ == "__main__":
    os.environ[FETCH_VALUES_FROM_SSM_ENV_VAR] = "true"
    os.environ[DEPLOYMENT_ENVIRONMENT_ENV_VAR] = "prod"
    os.environ["AWS_PROFILE"] = "rootski"
    from rich import print

    config = Config()
    print(config.dict())
