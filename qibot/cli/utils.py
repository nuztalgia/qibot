from base64 import urlsafe_b64encode
from functools import partial
from os import urandom
from pathlib import Path
from typing import Callable, Final, Optional, TypeAlias

from colorama import Fore, Style
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

_ColorText: TypeAlias = Callable[[str], str]
_FormatText: TypeAlias = Callable[[str], Optional[str]]

_KEYS_DIR: Final[Path] = Path(__file__).parent / ".keys"
_YES_RESPONSES: Final[tuple[str, str]] = ("yes", "y")


def get_key_file(filename: str, qualifier: str = "") -> Path:
    if _KEYS_DIR.is_file():
        _KEYS_DIR.unlink()
    if not _KEYS_DIR.is_dir():
        _KEYS_DIR.mkdir()
    qualifier = f".{qualifier.strip().lower()}" if qualifier else ""
    return _KEYS_DIR / f".{filename.strip().lower()}{qualifier}.key"


def get_secret(prompt: str, format_text: Optional[_FormatText] = None) -> str:
    prompt = color_cyan(f"{prompt.strip().upper()}: ")
    result = getpass(prompt).strip()
    output = (format_text and format_text(result)) or color_grey("*" * len(result))
    print(f"\033[F\033[1A{prompt}{output}\n")  # This overwrites the previous line.
    return result


def get_yes_or_no_answer(question: str) -> bool:
    # The prompt must go through `print` (instead of `input`) to be formatted correctly.
    print(f"{question} If so, type {_FORMATTED_RESPONSES}: ", end="")
    user_response = input()
    print()  # Print an empty line to make subsequent output sections easier to read.
    return user_response.strip(" '\"").lower() in _YES_RESPONSES


def confirm_or_exit(question: str) -> None:
    if not get_yes_or_no_answer(question):
        print(color_grey("Received a non-affirmative response. Exiting process.\n"))
        raise SystemExit(0)  # Technically a success, since it's what the user wanted.


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


def _color(fore_color_code: str) -> _ColorText:
    def color_text(text: str) -> str:
        return f"{fore_color_code}{Style.BRIGHT}{text}{Style.NORMAL}{Fore.RESET}"

    return color_text


color_cyan: Final[_ColorText] = _color(Fore.CYAN)
color_green: Final[_ColorText] = _color(Fore.GREEN)
color_grey: Final[_ColorText] = _color(Fore.BLACK)  # "Bright black" shows up as grey.
color_magenta: Final[_ColorText] = _color(Fore.MAGENTA)
color_yellow: Final[_ColorText] = _color(Fore.YELLOW)

_FORMATTED_RESPONSES: Final[str] = " or ".join(
    f'"{color_cyan(response)}"' for response in _YES_RESPONSES
)

try:
    import msvcrt
except ImportError:
    # We're on an OS where things conveniently work out of the box.
    import getpass as _getpass

    # Just need to do a bit of type wrangling to satisfy the static type checkers.
    getpass: Final[Callable[[str], str]] = _getpass.getpass
else:
    # We're on Windows, so we need to do things differently. How fun!
    _WINDOWS_NEWLINES: Final[str] = "\r\n"

    def getpass(prompt: str) -> str:
        result = ""
        print(prompt, end="")

        while (input_char := msvcrt.getwch()) not in _WINDOWS_NEWLINES:
            if input_char == "\003":
                raise KeyboardInterrupt
            result = result[:-1] if input_char == "\b" else f"{result}{input_char}"

        for newline_char in _WINDOWS_NEWLINES:
            msvcrt.putwch(newline_char)

        return result
