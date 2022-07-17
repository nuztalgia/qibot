from getpass import getpass
from typing import Callable, Optional, TypeAlias

from qibot.version import VERSION

_FormatSecret: TypeAlias = Callable[[str], Optional[str]]


def confirm_or_exit(question: str) -> None:
    if not get_yes_or_no_answer(question):
        print("Received a non-affirmative response. Exiting.\n")
        raise SystemExit(0)  # Technically a success, since it's what the user wanted.


def get_secret(prompt: str, format_secret: Optional[_FormatSecret] = None) -> str:
    secret = getpass(f"{prompt}: ").strip()
    output = (format_secret and format_secret(secret)) or ("*" * len(secret))
    print(f"\033[F{prompt}: {output}\n")  # This overwrites the previously printed line.
    return secret


def get_yes_or_no_answer(question: str) -> bool:
    user_response = input(f'{question} If so, type "yes" or "y": ')
    print()  # Print an empty line to make subsequent output sections easier to read.
    return user_response.strip(" '\"").lower() in ("yes", "y")


def print_bot_version() -> None:
    print(
        "\n               o|         |    \n          ,---..|---.,---.|--- "
        "\n          |   |||   ||   ||    \n          `---|``---'`---'`---'"
        f"\n              |  VERSION {VERSION}\n"
    )
