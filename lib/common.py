import logging
import sys
from string import Template as _Template
from typing import Callable, Final

from dotenv import dotenv_values, find_dotenv


class Constants:
    _env_config: Final[dict] = dotenv_values(find_dotenv())
    BOT_TOKEN: Final[str] = _env_config.get("BOT_TOKEN")  # Must be defined in dotenv.
    DEV_MODE_ENABLED: Final[bool] = _env_config.get("DEV_MODE_ENABLED", False)
    LOG_THRESHOLD: Final[str] = _env_config.get("LOG_THRESHOLD", "info").upper()


class Log:
    _root_logger: Final[logging.Logger] = logging.getLogger()

    d: Final[Callable] = _root_logger.debug
    i: Final[Callable] = _root_logger.info
    w: Final[Callable] = _root_logger.warning
    e: Final[Callable] = _root_logger.error

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
    sub = _Template.substitute
    safe_sub = _Template.safe_substitute
