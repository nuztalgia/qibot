import argparse
import importlib
from typing import Final

import colorama

from qibot.cli.tokens import get_token_info, matches_token_pattern
from qibot.cli.utils import cyan, exit_process, green, magenta, read_decrypted, yellow
from qibot.version import VERSION

_PROGRAM_NAME: Final[str] = magenta("qibot")
_PROGRAM_PREFIX: Final[str] = f"{_PROGRAM_NAME}: "
_ERROR_PREFIX: Final[str] = f"{_PROGRAM_PREFIX}error: "


def main() -> int:
    colorama.init(autoreset=True)
    try:
        _main()
    except KeyboardInterrupt:
        exit_process("\nReceived a keyboard interrupt.", is_error=False)
    finally:
        colorama.deinit()
    return 0


def _main() -> None:
    args = _get_args()

    if args.version:
        return print_bot_version()

    mode_label = f"{green('production') if args.prod else yellow('development')} mode"
    bot_token = read_decrypted(*get_token_info(args.prod, mode_label, _PROGRAM_PREFIX))

    if not matches_token_pattern(bot_token):
        print(f"\n{_ERROR_PREFIX}Decrypted keyfile data doesn't look like a bot token.")
        if args.prod:
            print("Please make sure you have the correct password, then try again.\n")
        return

    print(f"\n{_PROGRAM_PREFIX}Starting bot in {mode_label}.\n")

    # We only import the bot module (and run its initialization code) when it's needed.
    bot_module = importlib.import_module("qibot.bot")
    bot_module.QiBot().run(bot_token)


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

    add_option("prod", "Run the bot in production (i.e. password-protected) mode.")
    add_option("version", "Display the currently installed version.")
    add_option("help", "Display this help message.", action="help")

    return parser.parse_args()


def print_bot_version() -> None:
    qibot_text = (
        "\n               o|         |    \n          ,---..|---.,---.|--- "
        "\n          |   |||   ||   ||    \n          `---|``---'`---'`---'"
        "\n              |  "
    )
    print(magenta(qibot_text) + cyan(f"VERSION {VERSION}\n"))
