from json import load as load_json
from string import Template as _Template
from typing import Any, Callable, Final

from dotenv import dotenv_values, find_dotenv

_ENV_CONFIG: Final[dict[str, Any]] = dotenv_values(
    dotenv_path=find_dotenv(), verbose=True
)


class Constants:
    BOT_VERSION: Final[str] = "0.1.0"
    BOT_TOKEN: Final[str] = _ENV_CONFIG["BOT_TOKEN"]
    HOME_SERVER_ID: Final[int] = int(_ENV_CONFIG["HOME_SERVER_ID"])
    COMMAND_PREFIX: Final[str] = _ENV_CONFIG.get("COMMAND_PREFIX", ".")
    DEV_MODE_ENABLED: Final[bool] = _ENV_CONFIG.get("DEV_MODE_ENABLED", False)


class Template(_Template):
    sub: Final[Callable[..., str]] = _Template.substitute
    safe_sub: Final[Callable[..., str]] = _Template.safe_substitute


def get_channel_id(channel_name: str) -> int:
    return _ENV_CONFIG.get(f"{channel_name}_CHANNEL_ID", 0)


def load_json_file(file_name: str) -> dict[str, Any] | list[Any]:
    with open(f"assets/data/{file_name}.json", "r") as file:
        return load_json(file)
