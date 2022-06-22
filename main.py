from typing import Final

from discord import Activity, ActivityType, AllowedMentions, Cog, Intents, LoginFailure
from discord.ext.commands import Bot

from lib.characters import Character
from lib.common import Constants
from lib.logger import Log
from lib.registry import CogRegistry


class ReadyListener(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Final[Bot] = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        Log.i(f'Successfully logged in as "{self.bot.user}".')

        server_count = len(self.bot.guilds)
        if server_count != 1:
            Log.e(
                f"This bot account is in {server_count} servers (expected: 1). Exiting."
            )
            return await self.bot.close()

        home_server = self.bot.guilds[0]
        if home_server.id != Constants.HOME_SERVER_ID:
            Log.e(
                f'This bot is running in an unexpected server: "{home_server.name}"'
                f"{Log.NEWLINE}Make sure the HOME_SERVER_ID is configured properly."
            )
            return await self.bot.close()

        # Bot token and server are correctly configured. Finish the setup process.
        Log.i(f'Monitoring server: "{home_server.name}"')
        await self.bot.change_presence(
            activity=Activity(type=ActivityType.watching, name="everything.")
        )
        self.bot.remove_cog(self.__class__.__name__)


def setup(bot: Bot) -> None:
    # Load production-ready cogs, or all cogs if the bot is running in dev mode.
    for cog in CogRegistry:
        if cog.is_production_ready or Constants.DEV_MODE_ENABLED:
            Log.i(f'Loading extension "{cog.cog_class_name}".')
            bot.load_extension(cog.get_module_name())
    bot.add_cog(ReadyListener(bot))  # Prints a message when the bot has logged in.


if __name__ == "__main__":
    Character.initialize_all()

    mode_label = "developer" if Constants.DEV_MODE_ENABLED else "production"
    Log.i(f"Initializing bot in {mode_label} mode.")

    # These intents must be enabled in the Developer Portal on Discord's website.
    intents = Intents.default()
    intents.members = True
    intents.message_content = True

    qi_bot = Bot(
        allowed_mentions=AllowedMentions.none(),
        case_insensitive=True,
        command_prefix=Constants.COMMAND_PREFIX,
        debug_guilds=[Constants.HOME_SERVER_ID],
        help_command=None,
        intents=intents,
    )

    # This leads to calling the setup function defined above, which loads all the cogs.
    qi_bot.load_extension("main")

    try:
        Log.i("Attempting to log in to Discord...")
        qi_bot.run(Constants.BOT_TOKEN)
    except LoginFailure:
        Log.e("Failed to log in. Make sure the BOT_TOKEN is configured properly.")
