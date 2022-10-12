from typing import Final

from botstrap import Botstrap, CliColors, Color, Option
from discord import AllowedMentions

from qibot.utils import initialize_logging

VERSION: Final[str] = "0.2.0"


def main() -> int:
    botstrap = (
        Botstrap(
            desc="QiBot is a modern Discord bot inspired by Stardew Valley.",
            colors=(colors := CliColors(Color.pink)),
            version=_get_display_version(colors),
        )
        .register_token(
            uid="dev",
            display_name=Color.yellow("development"),
        )
        .register_token(
            uid="prod",
            requires_password=True,
            display_name=Color.green("production"),
        )
    )

    args = botstrap.parse_args(
        loglevel=Option(
            default="i",
            choices=("d", "debug", "i", "info", "w", "warning", "e", "error"),
            help="The lowest message level to log.",
        ),
        allow_pings=Option(flag=True, help="Allow the bot to ping people/roles."),
    )

    initialize_logging(log_level=args.loglevel)
    pings = AllowedMentions.everyone() if args.allow_pings else AllowedMentions.none()
    botstrap.run_bot(bot_class="qibot.bot.QiBot", allowed_mentions=pings)

    return 0


def _get_display_version(colors: CliColors) -> str:
    return colors.primary(
        "\n               o|         |      "
        "\n          ,---..|---.,---.|---   "
        "\n          |   |||   ||   ||      "
        "\n          `---|``---'`---'`---'  "
        "\n              |  "
    ) + colors.highlight(f"VERSION {VERSION}\n")
