import argparse
import importlib
import operator
import sys
from typing import Final

from qibot.cli.tokens import get_token_file
from qibot.version import VERSION

_ERROR_PREFIX: Final[str] = "qibot: error: "


def main() -> None:
    args = _get_args()
    argv = sys.argv[1:]

    if operator.countOf(vars(args).values(), True) > 1:
        arg_info = ('", "'.join(argv[:-1])) + ('",' if len(argv) > 2 else '"')
        arg_info = f'("{arg_info} and "{argv[-1]}"). They are mutually exclusive.'
        print(f"{_ERROR_PREFIX}Cannot simultaneously use multiple options {arg_info}")
        return

    if args.version:
        _print_version()
        return

    if not (token_file := get_token_file(args.prod, _ERROR_PREFIX)):
        return

    # The bot module is only imported (and initialization code is only run) if needed.
    bot_module = importlib.import_module("qibot.bot")
    bot_module.QiBot().run(token_file.read_text())


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


def _print_version() -> None:
    print(
        "\n               o|         |    \n          ,---..|---.,---.|--- "
        "\n          |   |||   ||   ||    \n          `---|``---'`---'`---'"
        f"\n              |  VERSION {VERSION}\n"
    )
