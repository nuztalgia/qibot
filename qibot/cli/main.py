import argparse
import importlib
import operator
import sys
from typing import Final

from qibot.cli.tokens import get_token_file
from qibot.cli.utils import decrypt_bytes, print_bot_version

_SUCCESS: Final[int] = 0
_ERROR: Final[int] = 1


def main() -> int:
    args = _get_args()
    argv = sys.argv[1:]

    if operator.countOf(vars(args).values(), True) > 1:
        arg_info = ('", "'.join(argv[:-1])) + ('",' if len(argv) > 2 else '"')
        arg_info = f'("{arg_info} and "{argv[-1]}"). They are mutually exclusive.'
        print(f"qibot: error: Cannot simultaneously use multiple options {arg_info}")
        return _ERROR

    if args.version:
        print_bot_version()
        return _SUCCESS

    token_file, token_file_password = get_token_file(args.prod)

    if not token_file:
        # `get_token_file` takes care of printing an appropriate error message.
        return _ERROR

    if isinstance(token_file_password, str):
        bot_token = decrypt_bytes(token_file_password, data=token_file.read_bytes())
    else:
        bot_token = token_file.read_text()

    # We only import the bot module (and run its initialization code) when it's needed.
    bot_module = importlib.import_module("qibot.bot")

    bot_is_running = bot_module.QiBot().run(bot_token)
    return _SUCCESS if bot_is_running else _ERROR


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="qibot",
        description=(
            "  QiBot is a Discord bot inspired by Stardew Valley.\n"
            '  Run "qibot" with no options to start the bot in the default mode.'
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )

    def add_option(name: str, desc: str, action: str = "store_true") -> None:
        parser.add_argument(f"-{name[0]}", f"--{name}", action=action, help=desc)

    add_option("prod", "Run QiBot in production (i.e. password-protected) mode.")
    add_option("help", "Display this help message.", action="help")
    add_option("version", "Display the currently installed version of QiBot.")

    return parser.parse_args()
