import argparse
import importlib
import operator
import sys
from typing import Final

import colorama

from qibot.cli.colors import cyan, green, magenta, yellow
from qibot.cli.tokens import get_token_info, matches_token_pattern
from qibot.cli.utils import decrypt_bytes, exit_cli
from qibot.version import VERSION

_PROGRAM_NAME: Final[str] = magenta("qibot")
_PROGRAM_PREFIX: Final[str] = f"{_PROGRAM_NAME}: "
_ERROR_PREFIX: Final[str] = f"{_PROGRAM_PREFIX}error: "


def main() -> int:
    colorama.init(autoreset=True)
    is_success = False
    try:
        is_success = _main()
    except KeyboardInterrupt:
        exit_cli(reason="\nReceived a keyboard interrupt.", is_error=False)
    finally:
        colorama.deinit()
        return 0 if is_success else 1


def _main() -> bool:
    args = _get_args()
    argv = sys.argv[1:]

    if operator.countOf(vars(args).values(), True) > 1:
        arg_info = ('", "'.join(argv[:-1])) + ('",' if len(argv) > 2 else '"')
        arg_info = f'("{arg_info} and "{argv[-1]}"). They are mutually exclusive.'
        print(f"{_ERROR_PREFIX}Cannot simultaneously use multiple options {arg_info}")
        return False

    if args.version:
        print_bot_version()
        return True

    mode_label = f"{green('production') if args.prod else yellow('development')} mode"
    token_file, password = get_token_info(args.prod, mode_label, _PROGRAM_PREFIX)

    if not token_file:
        # `get_token_file_info` takes care of printing an appropriate error message.
        return False

    bot_token = decrypt_bytes(data=token_file.read_bytes(), password=password)

    if not matches_token_pattern(bot_token):
        print(f"\n{_ERROR_PREFIX}Decrypted keyfile data doesn't look like a bot token.")
        if password:
            print("Please make sure you have the correct password, then try again.\n")
        print(
            "If this happens repeatedly and/or unexpectedly, try removing,\n"
            "regenerating, and then re-adding your bot token(s).\n"
        )
        return False

    print(f"\n{_PROGRAM_PREFIX}Starting bot in {mode_label}.\n")

    # We only import the bot module (and run its initialization code) when it's needed.
    bot_module = importlib.import_module("qibot.bot")
    return bot_module.QiBot().run(bot_token)


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=_PROGRAM_NAME,
        description=(
            "  QiBot is a Discord bot inspired by Stardew Valley.\n"
            '  Run "qibot" with no options to start the bot in development mode.'
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )

    def add_option(name: str, desc: str, action: str = "store_true") -> None:
        parser.add_argument(f"-{name[0]}", f"--{name}", action=action, help=desc)

    add_option("prod", "Run QiBot in production (i.e. password-protected) mode.")
    add_option("version", "Display the currently installed version of QiBot.")
    add_option("help", "Display this help message.", action="help")

    return parser.parse_args()


def print_bot_version() -> None:
    qibot_text = (
        "\n               o|         |    \n          ,---..|---.,---.|--- "
        "\n          |   |||   ||   ||    \n          `---|``---'`---'`---'"
        "\n              |  "
    )
    print(magenta(qibot_text) + cyan(f"VERSION {VERSION}\n"))
