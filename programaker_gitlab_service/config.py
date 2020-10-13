import getpass
import json
import os
from xdg import XDG_CONFIG_HOME

PROGRAMAKER_BRIDGE_ENDPOINT_ENV = 'PLAZA_BRIDGE_ENDPOINT'
PROGRAMAKER_AUTH_TOKEN_ENV = 'PLAZA_BRIDGE_AUTH_TOKEN'

PROGRAMAKER_BRIDGE_ENDPOINT_INDEX = "plaza_bridge_endpoint"
PROGRAMAKER_AUTH_TOKEN_INDEX = 'plaza_authentication_token'


global directory, config_file
directory = os.path.join(XDG_CONFIG_HOME, "plaza", "bridges", "gitlab")
config_file = os.path.join(directory, "config.json")


def _get_config():
    if not os.path.exists(config_file):
        return {}
    with open(config_file, "rt") as f:
        return json.load(f)


def _save_config(config):
    os.makedirs(directory, exist_ok=True)
    with open(config_file, "wt") as f:
        return json.dump(config, f)


def get_bridge_endpoint():
    # Check if the bridge endpoint is defined in an environment variable
    programaker_bridge_endpoint_env = os.getenv(PROGRAMAKER_BRIDGE_ENDPOINT_ENV, None)
    if programaker_bridge_endpoint_env is not None:
        return programaker_bridge_endpoint_env

    # If not, request it and save it to a file
    config = _get_config()
    if config.get(PROGRAMAKER_BRIDGE_ENDPOINT_INDEX, None) is None:
        config[PROGRAMAKER_BRIDGE_ENDPOINT_INDEX] = input("Programaker bridge endpoint: ")
        if not config[PROGRAMAKER_BRIDGE_ENDPOINT_INDEX]:
            raise Exception("No bridge endpoint introduced")
        _save_config(config)
    return config[PROGRAMAKER_BRIDGE_ENDPOINT_INDEX]


def get_auth_token():
    env_val = os.getenv(PROGRAMAKER_AUTH_TOKEN_ENV, None)
    if env_val is not None:
        return env_val

    config = _get_config()
    if config.get(PROGRAMAKER_AUTH_TOKEN_INDEX, None) is None:
        config[PROGRAMAKER_AUTH_TOKEN_INDEX] = input('Programaker authentication TOKEN: ')
        if not config[PROGRAMAKER_AUTH_TOKEN_INDEX]:
            raise Exception('No authentication token introduced')
        _save_config(config)
    return config[PROGRAMAKER_AUTH_TOKEN_INDEX]
