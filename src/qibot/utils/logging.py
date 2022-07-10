import logging
import sys
from typing import Callable, Final, TypeAlias

_LogMethod: TypeAlias = Callable[[str], None]

_ROOT_LOGGER: Final[logging.Logger] = logging.getLogger()

_EXTERNAL_LOGGER_NAMES: Final[list[str]] = ["discord", "PIL"]
_EXTERNAL_LOGGER_LEVEL: Final[int] = logging.WARNING


class Log:
    NEWLINE: Final[str] = "\n                          "

    d: Final[_LogMethod] = _ROOT_LOGGER.debug
    i: Final[_LogMethod] = _ROOT_LOGGER.info
    w: Final[_LogMethod] = _ROOT_LOGGER.warning
    e: Final[_LogMethod] = _ROOT_LOGGER.error


def _initialize() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        style="{",
        format="{asctime} | {levelname[0]} | {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    for logger_name in _EXTERNAL_LOGGER_NAMES:
        logging.getLogger(logger_name).setLevel(_EXTERNAL_LOGGER_LEVEL)


# This will be executed only once (the first time this module is imported anywhere).
_initialize()
