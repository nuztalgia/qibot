from base64 import urlsafe_b64encode
from functools import partial
from getpass import getpass
from os import urandom
from pathlib import Path
from typing import Callable, Final, Optional, TypeAlias

from colorama import Fore, Style
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

_FormatText: TypeAlias = Callable[[str], str]

_KEYS_DIR: Final[Path] = Path(__file__).parent / ".keys"
_YES_RESPONSES: Final[tuple[str, str]] = ("yes", "y")


def confirm_or_exit(question: str) -> None:
    if not get_bool_input(question):
        exit_cli("Received a non-affirmative response.", is_error=False)


def exit_cli(reason: str, is_error: bool = True) -> None:
    colored_reason = red(reason) if is_error else grey(reason)
    print(f"\n{colored_reason} {grey('Exiting process.')}\n")
    raise SystemExit(1 if is_error else 0)


def get_bool_input(question: str) -> bool:
    colored_prompt = '" or "'.join(cyan(response) for response in _YES_RESPONSES)
    result = _get_input(f'{question} If so, type "{colored_prompt}":')
    return result.strip("'\"").lower() in _YES_RESPONSES


def get_hidden_input(prompt: str, format_text: Optional[_FormatText] = None) -> str:
    result = _get_input(colored_prompt := cyan(f"{prompt}:"), hidden=True)
    output = grey((format_text and format_text(result)) or "*" * len(result))
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
    return (getpass(prompt="") if hidden else input()).strip()


def _color(fore_color_code: str) -> _FormatText:
    def color_text(text: str) -> str:
        return f"{fore_color_code}{Style.BRIGHT}{text}{Style.NORMAL}{Fore.RESET}"

    return color_text


cyan: Final[_FormatText] = _color(Fore.CYAN)
green: Final[_FormatText] = _color(Fore.GREEN)
grey: Final[_FormatText] = _color(Fore.BLACK)  # "Bright black" is displayed as grey.
magenta: Final[_FormatText] = _color(Fore.MAGENTA)
red: Final[_FormatText] = _color(Fore.RED)
yellow: Final[_FormatText] = _color(Fore.YELLOW)
