from discord import AllowedMentions, Intents, LoginFailure

from qibot.bot import QiBot
from qibot.utils import BOT_TOKEN, SERVER_ID, Log


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
    Log.i(f"Starting QiBot {QiBot.VERSION}.")
    bot = _create_bot(SERVER_ID)

    try:
        Log.i("Attempting to log in to Discord...")
        bot.run(BOT_TOKEN)
    except LoginFailure:
        Log.e("Failed to log in. Make sure the BOT_TOKEN is configured properly.")
