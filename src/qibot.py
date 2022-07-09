from datetime import datetime
from typing import ClassVar, Final, Optional

from discord import Activity, ActivityType, ApplicationContext, Bot, Cog, slash_command
from discord.utils import utcnow

from lib.characters import Overseer
from lib.utils import BotChannel, Log


class QiBot(Bot):
    VERSION: Final[str] = "0.1.0"
    START_TIME: ClassVar[datetime]

    def __init__(self, *args, **options) -> None:
        super().__init__(*args, **options)
        self.add_cog(_MetaCommands(self))
        # TODO: Redesign loading mechanism when there are more extensions to deal with.
        self.load_extension("cogs.members")

    async def on_ready(self) -> None:
        Log.i(f'  Successfully logged in as "{self.user}".')

        server_name = self._get_server_name()
        if not server_name:
            return await self.close()

        Log.i(f'Monitoring server: "{server_name}"')
        type(self).START_TIME = utcnow()

        await BotChannel.initialize_all(self)

        await self.change_presence(
            activity=Activity(type=ActivityType.watching, name="everything.")
        )

    def _get_server_name(self) -> Optional[str]:
        if len(self.guilds) != 1:
            Log.e(
                f"This bot account is a member of {len(self.guilds)} servers."
                f"{Log.NEWLINE}It must be present in exactly 1 server. Exiting."
            )
            return None
        elif self.guilds[0].id != self.debug_guilds[0]:
            Log.e(
                f'This bot is running in an unexpected server: "{self.guilds[0].name}"'
                f"{Log.NEWLINE}Make sure the SERVER_ID is configured properly. Exiting."
            )
            return None
        else:
            return self.guilds[0].name


class _MetaCommands(Cog):
    @slash_command(description="Shows metadata about this bot.")
    async def about(self, ctx: ApplicationContext) -> None:
        if await BotChannel.BOT_SPAM.is_context(ctx):
            await Overseer.show_bot_metadata(ctx, QiBot.VERSION, QiBot.START_TIME)

    @slash_command(description="Shows a motivational quote. (Under construction!)")
    async def help(self, ctx: ApplicationContext) -> None:
        # TODO: Properly implement this when there's actual information to show.
        await Overseer.show_bot_help(ctx)
