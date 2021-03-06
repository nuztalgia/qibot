import re
import shutil
from enum import Enum, auto, unique
from pathlib import Path
from typing import Final, Optional, TypeAlias

from qibot.cli.utils import (
    confirm_or_exit,
    exit_process,
    get_hidden_input,
    get_key_file,
    green,
    grey,
    write_encrypted,
    yellow,
)

_TokenInfo: TypeAlias = tuple[Path, Optional[str]]

_PROMPT_BOT_TOKEN: Final[str] = "BOT TOKEN"
_PROMPT_PASSWORD: Final[str] = "PASSWORD"

_TOKEN_SEGMENT_LENGTHS: Final[tuple[int, ...]] = (24, 6, 27)
_TOKEN_REGEX: Final[re.Pattern] = re.compile(
    r"\.".join(r"[\w-]{%i}" % i for i in _TOKEN_SEGMENT_LENGTHS)
)
_TOKEN_FORMAT: Final[str] = ".".join("*" * i for i in _TOKEN_SEGMENT_LENGTHS)


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


def matches_token_pattern(text: str) -> bool:
    return bool(_TOKEN_REGEX.fullmatch(text))


def get_token_info(prod: bool, mode_label: str, prefix: str) -> _TokenInfo:
    if (not prod) and (dev_file := _Token.DEV.file_path).is_file():
        return dev_file, None
    elif prod and (prod_file := _Token.PROD.file_path).is_file():
        print(f"\n{prefix}prod: Please enter the password to decrypt your bot token.")
        return prod_file, get_hidden_input(_PROMPT_PASSWORD)
    else:
        print(f"\n{prefix}You currently don't have a saved bot token for {mode_label}.")
        confirm_or_exit("\nWould you like to add one now?")
        return _create_token_info(prod)


def _create_token_info(prod: bool) -> _TokenInfo:
    token_file = (_Token.PROD if prod else _Token.DEV).file_path
    bot_token = _get_new_bot_token()
    password = _get_new_password() if prod else None

    write_encrypted(file_path=token_file, data=bot_token, password=password)

    print(green("\nYour token has been successfully encrypted and saved."))
    confirm_or_exit("\nDo you want to use this token to run your bot now?")

    return token_file, password


def _get_new_bot_token() -> str:
    def format_token(token: str) -> str:
        # Let the default formatter handle the string if it doesn't look like a token.
        return _TOKEN_FORMAT if matches_token_pattern(token) else ""

    print("\nPlease enter your bot token now. It'll be invisible for security reasons.")
    bot_token = get_hidden_input(_PROMPT_BOT_TOKEN, format_token)

    if not matches_token_pattern(bot_token):
        message = "That doesn't seem like a valid bot token. It should look like this:"
        print(f'\n{message}\n{grey(f"{_PROMPT_BOT_TOKEN}: {_TOKEN_FORMAT}")}')
        exit_process("Please make sure you have the correct token, then try again.")

    return bot_token


def _get_new_password() -> str:
    print(
        "\nTo keep your bot token extra safe, it must be encrypted with a password.\n"
        "This password won't be stored anywhere. It will only be used as a key to\n"
        f"decrypt your token every time you run the bot in {green('production')} mode."
    )

    print("\nPlease enter a password for your production token.")
    while len(password := get_hidden_input(_PROMPT_PASSWORD)) < (min_length := 8):
        print(yellow(f"\nYour password must be at least {min_length} characters long."))
        confirm_or_exit("Would you like to try a different one?")

    print("\nPlease re-enter the same password again to confirm.")
    while get_hidden_input(_PROMPT_PASSWORD) != password:
        print(yellow("\nThat password doesn't match your original password."))
        confirm_or_exit("Would you like to try again?")

    return password
