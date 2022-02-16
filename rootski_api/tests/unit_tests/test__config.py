"""Test proper functionality of the configuration manager."""

import json
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict

import yaml

from rootski.config.config import DEFAULT_S3_STATIC_SITE_DOMAIN, Config, get_environ_name
from tests.constants import DUMMY_CONFIG_VALUES
from tests.utils import scoped_env_vars


def get_sample_settings(as_env_vars: bool = False) -> Dict[str, Any]:
    if as_env_vars:
        return {get_environ_name(k): json.dumps(v) for k, v in DUMMY_CONFIG_VALUES.items()}
    else:
        return deepcopy(DUMMY_CONFIG_VALUES)


@contextmanager
def temp_yaml_file(contents: Dict[str, Any]) -> Path:
    """Create a temporary YAML file containing the ``contents``."""
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        yml_fpath = tmp_dir / "test-settings.yml"
        Path.touch(yml_fpath)
        with open(yml_fpath, "w") as tmp_file:
            yaml.safe_dump(deepcopy(contents), tmp_file)
        yield Path(yml_fpath)


def test__heirarchy_of_settings_sources():
    """Test that all setting sources follow the right priority."""

    # first priority - init/constructor arguments
    init_settings = get_sample_settings()
    init_settings["port"] = 1
    del init_settings["host"]
    del init_settings["domain"]
    del init_settings["s3_static_site_origin"]

    # second priority - environment variables
    env_settings = get_sample_settings(as_env_vars=True)
    env_settings[get_environ_name("port")] = "2"
    env_settings[get_environ_name("host")] = "env-host"
    del env_settings[get_environ_name("s3_static_site_origin")]
    del env_settings[get_environ_name("domain")]

    # third priority - yaml config file
    yaml_settings = get_sample_settings()
    yaml_settings["port"] = 2
    yaml_settings["host"] = "yaml-host"
    yaml_settings["domain"] = "yaml-domain"
    del yaml_settings["s3_static_site_origin"]

    # ... defaults are the last priority

    # write the yaml to a config file
    with temp_yaml_file(yaml_settings) as tmp_config_file:
        config_file_fpath = str(tmp_config_file.absolute())
        # set the Config() environment variables; set path to config file as environment variable
        env_vars = {
            **env_settings,
            get_environ_name("config_file_path"): config_file_fpath,
        }
        with scoped_env_vars(env_vars):
            settings = Config(**init_settings)
            assert settings.port == 1
            assert settings.host == "env-host"
            assert settings.domain == "yaml-domain"
            assert settings.s3_static_site_origin == DEFAULT_S3_STATIC_SITE_DOMAIN
