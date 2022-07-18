import sys
from base64 import urlsafe_b64encode
from functools import partial
from importlib import import_module
from os import urandom
from pathlib import Path
from types import ModuleType
from typing import Callable, Final, Optional, TypeAlias

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from qibot.cli.colors import cyan, grey, red

_FormatText: TypeAlias = Callable[[str], str]

_highlight: _FormatText = cyan
_lowlight: _FormatText = grey

_KEYS_DIR: Final[Path] = Path(__file__).parent / ".keys"
_YES_RESPONSES: Final[tuple[str, str]] = ("yes", "y")


def confirm_or_exit(question: str) -> None:
    if not get_bool_input(question):
        exit_cli("Received a non-affirmative response.", is_error=False)


def exit_cli(reason: str, is_error: bool = True) -> None:
    colored_reason = red(reason) if is_error else _lowlight(reason)
    print(f"\n{colored_reason} {_lowlight('Exiting process.')}\n")
    raise SystemExit(1 if is_error else 0)


def get_bool_input(question: str) -> bool:
    colored_prompt = '" or "'.join(_highlight(response) for response in _YES_RESPONSES)
    result = _get_input(f'{question} If so, type "{colored_prompt}":')
    return result.strip("'\"").lower() in _YES_RESPONSES


def get_hidden_input(prompt: str, format_text: Optional[_FormatText] = None) -> str:
    result = _get_input(colored_prompt := _highlight(f"{prompt}:"), hidden=True)
    output = _lowlight((format_text and format_text(result)) or "*" * len(result))
    print(f"\033[F\033[1A{colored_prompt} {output}")  # Overwrites the previous line.
    return result


def get_key_file(filename: str, qualifier: str = "") -> Path:
    if _KEYS_DIR.is_file():
        _KEYS_DIR.unlink()
    if not _KEYS_DIR.is_dir():
        _KEYS_DIR.mkdir()
    qualifier = f".{qualifier.strip().lower()}" if qualifier else ""
    return _KEYS_DIR / f".{filename.strip().lower()}{qualifier}.key"


def encrypt_string(data: str, password: Optional[str] = None) -> bytes:
    return _get_fernet(password).encrypt(data.encode())


def decrypt_bytes(data: bytes, password: Optional[str] = None) -> str:
    try:
        return _get_fernet(password).decrypt(data).decode()
    except InvalidToken:
        return ""


def _get_fernet(password: Optional[str]) -> Fernet:
    def get_extra_bytes(filename: str, get_initial_bytes: Callable[[], bytes]) -> bytes:
        extra_file = get_key_file(filename, qualifier="fernet")
        if not extra_file.is_file():
            extra_file.write_bytes(get_initial_bytes())
        return extra_file.read_bytes()

    if password:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=get_extra_bytes("prod", partial(urandom, 16)),
            iterations=480000,
        )
        key = urlsafe_b64encode(kdf.derive(password.encode()))
    else:
        key = get_extra_bytes("dev", Fernet.generate_key)

    return Fernet(key)


def _get_input(prompt: str, hidden: bool = False) -> str:
    # Use `print` for the prompt to ensure that any escape codes are formatted properly.
    # However, override the default `end` with " " to keep user input on the same line.
    print(prompt, end=" ")
    # Leading and trailing whitespace is stripped from the result before it's returned.
    return (_input_hidden() if hidden else input()).strip()


_WINDOWS_MODULE_NAME: Final[str] = "msvcrt"

if _WINDOWS_MODULE_NAME not in sys.builtin_module_names:
    # We're on an OS where things conveniently work out of the box.
    from getpass import getpass

    def _input_hidden() -> str:
        return getpass(prompt="")

else:
    # We're on Windows, so we need to do things differently. How fun!
    _MSVCRT: Final[ModuleType] = import_module(_WINDOWS_MODULE_NAME)
    _NEWLINE_CHARS: Final[str] = "\r\n"

    # Inspired by: https://github.com/python/cpython/blob/3.10/Lib/getpass.py#L97-L117
    def _input_hidden() -> str:
        result = ""

        while (input_char := _MSVCRT.getwch()) not in _NEWLINE_CHARS:
            if input_char == "\003":
                raise KeyboardInterrupt
            result = result[:-1] if input_char == "\b" else f"{result}{input_char}"

        for newline_char in _NEWLINE_CHARS:
            _MSVCRT.putwch(newline_char)

        return result
