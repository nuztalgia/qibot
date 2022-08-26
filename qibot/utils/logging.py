import logging
import sys
from typing import Callable, Final, TypeAlias

_LogMethod: TypeAlias = Callable[[str], None]

_ROOT_LOGGER: Final[logging.Logger] = logging.getLogger()
_EXTERNAL_LOGGER_NAMES: Final[list[str]] = ["discord", "PIL"]

_LOG_LEVEL_ALIASES: Final[dict[str, int]] = {
    "d": logging.DEBUG,
    "i": logging.INFO,
    "w": logging.WARNING,
    "e": logging.ERROR,
}


class Log:
    NEWLINE: Final[str] = "\n                          "

    d: Final[_LogMethod] = _ROOT_LOGGER.debug
    i: Final[_LogMethod] = _ROOT_LOGGER.info
    w: Final[_LogMethod] = _ROOT_LOGGER.warning
    e: Final[_LogMethod] = _ROOT_LOGGER.error


def initialize_logging(
    log_level: str | int = logging.DEBUG,
    external_log_level: str | int = logging.WARNING,
) -> None:
    if isinstance(log_level, str):
        if log_level in _LOG_LEVEL_ALIASES:
            log_level = _LOG_LEVEL_ALIASES[log_level]
        else:
            log_level = log_level.upper()

    logging.basicConfig(
        level=log_level,
        style="{",
        format="{asctime} | {levelname[0]} | {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    for logger_name in _EXTERNAL_LOGGER_NAMES:
        logging.getLogger(logger_name).setLevel(external_log_level)
