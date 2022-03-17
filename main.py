from discord import Activity, ActivityType, Bot, Cog, Intents

from lib.common import Constants, Log
from lib.registry import CogRegistry


class ReadyListener(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        Log.i(f"Successfully logged in as '{self.bot.user}'.")
        await self.bot.change_presence(
            activity=Activity(type=ActivityType.watching, name="everything.")
        )
        self.bot.remove_cog(self.__class__.__name__)


def setup(bot: Bot) -> None:
    # Load production-ready cogs, or all cogs if the bot is running in dev mode.
    for cog in CogRegistry:
        if cog.is_production_ready or Constants.DEV_MODE_ENABLED:
            Log.i(f"Loading extension '{cog.cog_class_name}'.")
            bot.load_extension(cog.get_module_name())
    bot.add_cog(ReadyListener(bot))  # Prints a message when the bot has logged in.


if __name__ == "__main__":
    Log.initialize()
    mode_label = "developer" if Constants.DEV_MODE_ENABLED else "production"
    Log.i(f"Initializing bot in {mode_label} mode.")

    # These intents must be enabled in the Developer Portal on Discord's website.
    intents = Intents.default()
    intents.members = True
    intents.message_content = True

    qi_bot = Bot(intents=intents)

    # This leads to calling the setup function defined above, which loads all the cogs.
    qi_bot.load_extension("main")

    Log.i("Attempting to log in to Discord...")
    qi_bot.run(Constants.BOT_TOKEN)
