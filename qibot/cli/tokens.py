import re
import shutil
import string
from enum import Enum, auto, unique
from pathlib import Path
from typing import Final, Optional

from qibot.cli.utils import (
    color_green,
    color_grey,
    color_magenta,
    color_yellow,
    confirm_or_exit,
    encrypt_string,
    get_key_file,
    get_secret,
    get_yes_or_no_answer,
)

_TOKEN_LENGTHS: Final[tuple[int, ...]] = (24, 6, 27)
_TOKEN_SEGMENT: Final[string.Template] = string.Template(r"[\w-]{$length}")
_TOKEN_REGEX: Final[re.Pattern] = re.compile(
    r"\.".join(_TOKEN_SEGMENT.substitute(length=length) for length in _TOKEN_LENGTHS)
)
_TOKEN_FORMAT: Final[str] = color_grey(
    ".".join("*" * length for length in _TOKEN_LENGTHS)
)


@unique
class _Token(Enum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, values: list) -> Path:
        return get_key_file(filename=name, qualifier="token")

    DEV = auto()
    PROD = auto()

    @property
    def file_path(self) -> Path:
        if self.value.is_dir():
            shutil.rmtree(self.value)
        return self.value

    @classmethod
    def get_existing_files(cls) -> tuple[Optional[Path], ...]:
        return tuple(
            member.file_path if member.file_path.is_file() else None for member in cls
        )


def matches_token_pattern(text: str) -> bool:
    return bool(_TOKEN_REGEX.fullmatch(text))


def get_token_file_info(prod: bool) -> tuple[Optional[Path], Optional[str]]:
    dev_file, prod_file = _Token.get_existing_files()

    if not (dev_file or prod_file):
        token_type = ""
    elif prod and (not prod_file):
        token_type = "production"
    elif (not prod) and (not dev_file):
        token_type = "development"
    else:
        # Use prod if -p was specified, otherwise try to use dev (with prod as backup).
        prod = prod or (dev_file is None)
        return (prod_file, get_secret("PASSWORD")) if prod else (dev_file, None)

    print(
        f"\nYou currently don't have a saved bot token for {token_type}."
        if token_type
        else "\nYou currently don't have any saved bot tokens."
    )
    confirm_or_exit(f"Would you like to {color_magenta('add a token')} now?")

    if not (bot_token := _get_new_bot_token()):
        # `_get_new_bot_token` takes care of printing an appropriate error message.
        return None, None

    if not token_type:
        print(
            "If this is a token that you plan to use in production (i.e. in a server\n"
            "that isn't just for bot testing), you should protect it with a password."
        )
        prod = get_yes_or_no_answer(
            f"Do you want to {color_magenta('set a password')} for this token?"
        )

    token_file = (_Token.PROD if prod else _Token.DEV).file_path
    password = _get_new_password() if prod else None

    token_file.write_bytes(encrypt_string(data=bot_token, password=password))

    print(color_green("Your token has been successfully encrypted and saved!"))
    confirm_or_exit(f"Do you want to {color_magenta('run QiBot')} with this token now?")

    return token_file, password


def _get_new_bot_token() -> Optional[str]:
    print(
        "Please enter your bot token now. It'll be invisible for security reasons,\n"
        "so don't worry about it not showing up! Just paste it in, then hit Enter."
    )

    def format_bot_token(token: str) -> Optional[str]:
        # Let the default formatter (all "*"s) handle the string if it isn't a token.
        return _TOKEN_FORMAT if matches_token_pattern(token) else None

    if matches_token_pattern(bot_token := get_secret("BOT TOKEN", format_bot_token)):
        return bot_token
    else:
        return print(
            f"That doesn't look like a valid Discord bot token. The expected format is:"
            f"\n    {_TOKEN_FORMAT}\nPlease check your bot token, then try again.\n"
        )


def _get_new_password() -> str:
    print(
        "Please enter a password for your token. It'll be invisible while you type it."
        "\nThis password won't be stored anywhere, and will only be used to decrypt"
        "\nyour bot token every time you start/restart QiBot in production mode."
    )
    while len(password := get_secret("PASSWORD")) < 8:
        print(color_yellow("Your password must be at least 8 characters long."))
        confirm_or_exit("Would you like to try again?")

    print("Please enter the same password again to confirm. Again, it'll be invisible.")
    while get_secret("CONFIRM PASSWORD") != password:
        print(color_yellow("That password doesn't match your original password."))
        confirm_or_exit("Would you like to try again?")

    return password
