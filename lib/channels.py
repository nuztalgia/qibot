from enum import Enum, auto
from typing import Final

from discord import Bot, TextChannel, Webhook

from lib.common import get_channel_id
from lib.logger import Log

_BOT_WEBHOOK_NAME: Final[str] = "QiBot Webhook"


class Channel(Enum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, values: list) -> int:
        return get_channel_id(name)

    LOGGING = auto()
    WELCOME = auto()

    async def get_webhook(self, bot: Bot) -> Webhook:
        channel = await self._get_channel(bot)
        for webhook in await channel.webhooks():
            if webhook.name == _BOT_WEBHOOK_NAME:
                return webhook
        Log.i(f'Creating bot webhook in "{channel.name}" (Channel ID: {channel.id}).')
        return await channel.create_webhook(name=_BOT_WEBHOOK_NAME)

    async def _get_channel(self, bot: Bot) -> TextChannel:
        channel = bot.get_channel(self.value) or await bot.fetch_channel(self.value)
        if not isinstance(channel, TextChannel):
            raise ValueError(
                f'Invalid "{self.name.title()}" channel. (Specified ID: "{self.value}")'
            )
        return channel
