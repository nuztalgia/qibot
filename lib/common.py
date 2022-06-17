import logging
import sys
from string import Template as _Template
from typing import Callable, Final, TypeAlias

from dotenv import dotenv_values, find_dotenv

_LogMethod: TypeAlias = Callable[[str], None]
_TemplateMethod: TypeAlias = Callable[..., str]


class Constants:
    _env_config: Final[dict[str, str | bool]] = dotenv_values(find_dotenv())
    BOT_TOKEN: Final[str] = _env_config.get("BOT_TOKEN")  # Must be defined in dotenv.
    COMMAND_PREFIX: Final[str] = _env_config.get("COMMAND_PREFIX", ".")
    DEV_MODE_ENABLED: Final[bool] = _env_config.get("DEV_MODE_ENABLED", False)
    LOG_THRESHOLD: Final[str] = _env_config.get("LOG_THRESHOLD", "info").upper()


class Log:
    _root_logger: Final[logging.Logger] = logging.getLogger()

    d: Final[_LogMethod] = _root_logger.debug
    i: Final[_LogMethod] = _root_logger.info
    w: Final[_LogMethod] = _root_logger.warning
    e: Final[_LogMethod] = _root_logger.error

    @staticmethod
    def initialize() -> None:
        logging.basicConfig(
            level=Constants.LOG_THRESHOLD,
            style="{",
            format="{asctime} | {levelname[0]} | {message}",
            datefmt="%Y-%m-%d %H:%M:%S",
            stream=sys.stdout,
        )
        discord_logger = logging.getLogger("discord")
        discord_logger.setLevel(logging.WARNING)


class Template(_Template):
    sub: Final[_TemplateMethod] = _Template.substitute
    safe_sub: Final[_TemplateMethod] = _Template.safe_substitute
