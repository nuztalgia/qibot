from typing import Final, Optional

from discord import Activity, ActivityType, AllowedMentions, Cog, Intents, LoginFailure
from discord.ext.commands import Bot

from lib.channels import Channel
from lib.characters import Characters
from lib.common import Config, Constants
from lib.logger import Log
from lib.registry import CogRegistry


def run_bot() -> None:
    custom_prefix = Config.CUSTOM_COMMAND_PREFIX
    prefix = custom_prefix or Constants.DEFAULT_COMMAND_PREFIX

    prefix_label = f' with custom prefix "{custom_prefix}"' if custom_prefix else ""
    mode_label = "developer mode" if Config.DEV_MODE_ENABLED else "production mode"
    Log.i(f"Starting QiBot {Constants.QI_BOT_VERSION} in {mode_label}{prefix_label}.")

    bot = Bot(
        allowed_mentions=AllowedMentions.none(),
        case_insensitive=True,
        command_prefix=prefix,
        debug_guilds=[Config.SERVER_ID],
        help_command=None,
        intents=_get_required_intents(),
    )

    # Load production-ready cogs, or all cogs if the bot is running in dev mode.
    for cog in CogRegistry:
        if cog.is_production_ready or Config.DEV_MODE_ENABLED:
            Log.d(f'Loading extension "{cog.cog_class_name}"...')
            bot.load_extension(cog.get_module_name())

    # This cog is defined below. It finishes the setup process after the bot logs in.
    bot.add_cog(_ReadyListener(bot, Config.SERVER_ID))

    try:
        Log.i("Attempting to log in to Discord...")
        bot.run(Config.BOT_TOKEN)
    except LoginFailure:
        Log.e("Failed to log in. Make sure the BOT_TOKEN is configured properly.")


# noinspection PyDunderSlots, PyUnresolvedReferences
def _get_required_intents() -> Intents:
    intents = Intents.default()
    # These intents must be enabled in the Developer Portal on Discord's website.
    intents.members = True
    intents.message_content = True
    return intents


class _ReadyListener(Cog):
    def __init__(self, bot: Bot, server_id: int) -> None:
        self.bot: Final[Bot] = bot
        self._server_id: Final[int] = server_id

    @Cog.listener()
    async def on_ready(self) -> None:
        Log.i(f'  Successfully logged in as "{self.bot.user}".')

        server_name = self._get_server_name()
        if not server_name:
            return await self.bot.close()

        Log.i(f'Monitoring server: "{server_name}"')

        await Channel.initialize_all(self.bot)
        await Characters.initialize()  # Must be called after channels are initialized.

        await self.bot.change_presence(
            activity=Activity(type=ActivityType.watching, name="everything.")
        )
        self.bot.remove_cog(self.__class__.__name__)

    def _get_server_name(self) -> Optional[str]:
        server_count = len(self.bot.guilds)
        if server_count != 1:
            Log.e(
                f"This bot account is in {server_count} servers (expected: 1). Exiting."
            )
            return

        server = self.bot.guilds[0]
        if server.id != self._server_id:
            Log.e(
                f'This bot is running in an unexpected server: "{server.name}"'
                f"{Log.NEWLINE}Make sure the SERVER_ID is configured properly. Exiting."
            )
            return

        return server.name


if __name__ == "__main__":
    run_bot()
