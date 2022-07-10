from datetime import datetime
from typing import ClassVar, Final, Optional

from discord import (
    Activity,
    ActivityType,
    AllowedMentions,
    ApplicationContext,
    Bot,
    Cog,
    Intents,
    LoginFailure,
    slash_command,
)
from discord.utils import utcnow

from qibot.characters import Overseer
from qibot.cogs import MemberListeners
from qibot.utils import BOT_TOKEN, SERVER_ID, BotChannel, Log


def main() -> None:
    bot = _QiBot(SERVER_ID)
    bot.run(BOT_TOKEN)


class _QiBot(Bot):
    VERSION: Final[str] = "0.1.0"
    START_TIME: ClassVar[datetime]

    def __init__(self, server_id: int) -> None:
        Log.i(f"Starting QiBot {type(self).VERSION}.")
        super().__init__(
            allowed_mentions=AllowedMentions.none(),
            debug_guilds=[server_id],
            help_command=None,
            intents=_get_required_intents(),
        )
        # TODO: Redesign cog-adding mechanism when there are more cogs to deal with.
        self.add_cog(_MetaCommands(self))
        self.add_cog(MemberListeners(self))

    def run(self, bot_token: str) -> None:
        try:
            Log.i("Attempting to log in to Discord...")
            super().run(bot_token)
        except LoginFailure:
            Log.e("Failed to log in. Make sure the BOT_TOKEN is configured properly.")

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


# noinspection PyDunderSlots, PyUnresolvedReferences
def _get_required_intents() -> Intents:
    intents = Intents.default()
    # These intents must be enabled in the Developer Portal on Discord's website.
    intents.members = True
    intents.message_content = True
    return intents


class _MetaCommands(Cog):
    @slash_command(description="Shows metadata about this bot.")
    async def about(self, ctx: ApplicationContext) -> None:
        if await BotChannel.BOT_SPAM.is_context(ctx):
            await Overseer.show_bot_metadata(ctx, _QiBot.VERSION, _QiBot.START_TIME)

    @slash_command(description="Shows a motivational quote. (Under construction!)")
    async def help(self, ctx: ApplicationContext) -> None:
        # TODO: Properly implement this when there's actual information to show.
        await Overseer.show_bot_help(ctx)
