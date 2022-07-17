from base64 import urlsafe_b64encode
from functools import partial
from getpass import getpass
from os import urandom
from pathlib import Path
from typing import Callable, Final, Optional, TypeAlias

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from qibot.version import VERSION

_FormatSecret: TypeAlias = Callable[[str], Optional[str]]

_KEYS_DIR: Final[Path] = Path(__file__).parent / ".keys"


def get_key_file(filename: str, qualifier: str = "") -> Path:
    if _KEYS_DIR.is_file():
        _KEYS_DIR.unlink()
    if not _KEYS_DIR.is_dir():
        _KEYS_DIR.mkdir()
    qualifier = f".{qualifier.strip().lower()}" if qualifier else ""
    return _KEYS_DIR / f".{filename.strip().lower()}{qualifier}.key"


def get_secret(prompt: str, format_secret: Optional[_FormatSecret] = None) -> str:
    secret = getpass(f"{prompt}: ").strip()
    output = (format_secret and format_secret(secret)) or ("*" * len(secret))
    print(f"\033[F{prompt}: {output}\n")  # This overwrites the previously printed line.
    return secret


def get_yes_or_no_answer(question: str) -> bool:
    user_response = input(f'{question} If so, type "yes" or "y": ')
    print()  # Print an empty line to make subsequent output sections easier to read.
    return user_response.strip(" '\"").lower() in ("yes", "y")


def confirm_or_exit(question: str) -> None:
    if not get_yes_or_no_answer(question):
        print("Received a non-affirmative response. Exiting the process.\n")
        raise SystemExit(0)  # Technically a success, since it's what the user wanted.


def print_bot_version() -> None:
    print(
        "\n               o|         |    \n          ,---..|---.,---.|--- "
        "\n          |   |||   ||   ||    \n          `---|``---'`---'`---'"
        f"\n              |  VERSION {VERSION}\n"
    )


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
