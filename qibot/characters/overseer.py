from datetime import datetime
from typing import Final

from discord import ApplicationContext

from qibot.characters.core import Action, Character
from qibot.embeds import create_inline_fields
from qibot.meta import VERSION
from qibot.utils import format_time, get_member_nametag

_DEVELOPER_DISCORD_TAG: Final[str] = "<@318178318488698891>"
_GITHUB_LINK: Final[str] = "[Available on GitHub!](https://github.com/nuztalgia/qibot)"


class Overseer(Character):
    async def show_bot_help(self, ctx: ApplicationContext) -> None:
        # TODO: Properly implement this when there's actual information to show.
        await self._send_message(action=Action.BOT_HELP, destination=ctx)

    async def show_bot_metadata(
        self, ctx: ApplicationContext, start_time: datetime
    ) -> None:
        await self._send_message(
            action=Action.BOT_METADATA,
            destination=ctx,
            fields=create_inline_fields(
                ("🏷️", "Bot Tag", get_member_nametag(ctx.bot.user)),
                ("🧭", "Home Server", ctx.guild.name),
                ("⌛", "Last Restarted", format_time(start_time, show_timestamp=False)),
                ("🤖", "Bot Version", VERSION),
                ("🤓", "Developer", _DEVELOPER_DISCORD_TAG),
                ("💻", "Source Code", _GITHUB_LINK),
            ),
        )
