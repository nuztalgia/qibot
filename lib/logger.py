import logging
import sys
from typing import Callable, Final, TypeAlias

from lib.common import Config

_LogMethod: TypeAlias = Callable[[str], None]

_ROOT_LOGGER: Final[logging.Logger] = logging.getLogger()


class Log:
    NEWLINE: Final[str] = "\n                          "

    d: Final[_LogMethod] = _ROOT_LOGGER.debug
    i: Final[_LogMethod] = _ROOT_LOGGER.info
    w: Final[_LogMethod] = _ROOT_LOGGER.warning
    e: Final[_LogMethod] = _ROOT_LOGGER.error


def _get_log_level() -> int | str:
    if Config.CUSTOM_LOG_THRESHOLD:
        return Config.CUSTOM_LOG_THRESHOLD.upper()
    elif Config.DEV_MODE_ENABLED:
        return logging.DEBUG
    else:
        return logging.INFO


def _initialize() -> None:
    logging.basicConfig(
        level=_get_log_level(),
        style="{",
        format="{asctime} | {levelname[0]} | {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging.WARNING)


# This will be executed only once (the first time this module is imported anywhere).
_initialize()
