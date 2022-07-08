from datetime import datetime
from typing import Final

from discord import ApplicationContext

from lib.characters.internal import Action, Character
from lib.common import Utils
from lib.embeds import FieldData

_DEVELOPER_DISCORD_TAG: Final[str] = "<@318178318488698891>"
_GITHUB_LINK: Final[str] = "[Available on GitHub!](https://github.com/nuztalgia/qibot)"


class Overseer(Character):
    async def show_bot_help(self, ctx: ApplicationContext) -> None:
        # TODO: Properly implement this when there's actual information to show.
        await self._send_message(action=Action.BOT_HELP, destination=ctx)

    async def show_bot_metadata(
        self, ctx: ApplicationContext, bot_version: str, bot_start_time: datetime
    ) -> None:
        formatted_bot_tag = Utils.get_member_nametag(ctx.bot.user)
        formatted_start_time = Utils.format_time(bot_start_time, show_timestamp=False)
        await self._send_message(
            action=Action.BOT_METADATA,
            destination=ctx,
            fields=[
                FieldData("🏷️", "Bot Tag", formatted_bot_tag, True),
                FieldData("🧭", "Home Server", ctx.guild.name, True),
                FieldData("⌛", "Last Restarted", formatted_start_time, True),
                FieldData("🤖", "Bot Version", bot_version, True),
                FieldData("🤓", "Developer", _DEVELOPER_DISCORD_TAG, True),
                FieldData("💻", "Source Code", _GITHUB_LINK, True),
            ],
        )
