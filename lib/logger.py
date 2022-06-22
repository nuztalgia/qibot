import logging
import sys
from typing import Callable, Final, TypeAlias

from lib.common import Constants

_LogMethod: TypeAlias = Callable[[str], None]

_ROOT_LOGGER: Final[logging.Logger] = logging.getLogger()


class Log:
    NEWLINE: Final[str] = "\n                          "

    d: Final[_LogMethod] = _ROOT_LOGGER.debug
    i: Final[_LogMethod] = _ROOT_LOGGER.info
    w: Final[_LogMethod] = _ROOT_LOGGER.warning
    e: Final[_LogMethod] = _ROOT_LOGGER.error


logging.basicConfig(
    level=logging.DEBUG if Constants.DEV_MODE_ENABLED else logging.INFO,
    style="{",
    format="{asctime} | {levelname[0]} | {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)

discord_logger = logging.getLogger("discord")
discord_logger.setLevel(logging.WARNING)
