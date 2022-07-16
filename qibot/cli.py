import argparse
import importlib

from qibot.version import VERSION


def main() -> None:
    args = _get_args()

    if args.version:
        _print_version()
        return

    # The bot module is only imported (and initialization code is only run) if needed.
    bot_module = importlib.import_module("qibot.bot")
    bot_module.QiBot().run()


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

    add_option("help", "Display this help message.", action="help")
    add_option("version", "Display the currently installed version of QiBot.")

    return parser.parse_args()


def _print_version() -> None:
    print(
        "\n               o|         |    \n          ,---..|---.,---.|--- "
        "\n          |   |||   ||   ||    \n          `---|``---'`---'`---'"
        f"\n              |  VERSION {VERSION}\n"
    )
