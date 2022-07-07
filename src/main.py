from discord import AllowedMentions, Intents, LoginFailure

from lib.common import Config
from lib.logger import Log
from lib.registry import CogRegistry
from qibot import QiBot


def _create_bot(server_id: int) -> QiBot:
    return QiBot(
        allowed_mentions=AllowedMentions.none(),
        case_insensitive=True,
        debug_guilds=[server_id],
        help_command=None,
        intents=_get_required_intents(),
    )


# noinspection PyDunderSlots, PyUnresolvedReferences
def _get_required_intents() -> Intents:
    intents = Intents.default()
    # These intents must be enabled in the Developer Portal on Discord's website.
    intents.members = True
    intents.message_content = True
    return intents


if __name__ == "__main__":
    mode_label = "developer" if Config.DEV_MODE_ENABLED else "production"
    Log.i(f"Starting QiBot {QiBot.VERSION} in {mode_label} mode.")

    bot = _create_bot(Config.SERVER_ID)

    # Load production-ready cogs, or all cogs if the bot is running in dev mode.
    for cog in CogRegistry:
        if cog.is_production_ready or Config.DEV_MODE_ENABLED:
            Log.d(f'Loading extension "{cog.cog_class_name}"...')
            bot.load_extension(cog.get_module_name())

    try:
        Log.i("Attempting to log in to Discord...")
        bot.run(Config.BOT_TOKEN)
    except LoginFailure:
        Log.e("Failed to log in. Make sure the BOT_TOKEN is configured properly.")
