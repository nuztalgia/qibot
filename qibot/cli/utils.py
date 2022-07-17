from base64 import urlsafe_b64encode
from getpass import getpass
from os import urandom
from pathlib import Path
from typing import Callable, Final, Optional, TypeAlias

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from qibot.version import VERSION

_FormatSecret: TypeAlias = Callable[[str], Optional[str]]

_CLI_DIR: Final[Path] = Path(__file__).parent


def get_cli_key_file(filename: str) -> Path:
    return _CLI_DIR / f".{filename}.key"


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


def encrypt_string(password: str, data: str) -> bytes:
    return _get_fernet(password).encrypt(data.encode())


def decrypt_bytes(password: str, data: bytes) -> str:
    return _get_fernet(password or get_secret("PASSWORD")).decrypt(data).decode()


def _get_fernet(password: str) -> Fernet:
    salt_file = get_cli_key_file("prod.salt")
    if not salt_file.is_file():
        salt_file.write_bytes(urandom(16))
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_file.read_bytes(),
        iterations=480000,
    )
    return Fernet(urlsafe_b64encode(kdf.derive(password.encode())))
