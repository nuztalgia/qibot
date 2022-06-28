from enum import Enum, auto
from typing import Final

from discord import Bot, TextChannel, Webhook

from lib.common import Config
from lib.logger import Log

_BOT_WEBHOOK_NAME: Final[str] = "QiBot Webhook"

_CHANNEL_CACHE: Final[dict[str, TextChannel]] = {}
_WEBHOOK_CACHE: Final[dict[str, Webhook]] = {}


class Channel(Enum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, values: list) -> int:
        return Config.get_channel_id(name)

    LOGGING = auto()
    RULES = auto()
    WELCOME = auto()

    async def get_channel(self, bot: Bot) -> TextChannel:
        if self.name not in _CHANNEL_CACHE:
            channel = bot.get_channel(self.value) or await bot.fetch_channel(self.value)
            if not isinstance(channel, TextChannel):
                raise ValueError(
                    f'Invalid "{self.name}" channel. (Specified ID: "{self.value}")'
                )
            _CHANNEL_CACHE[self.name] = channel
        return _CHANNEL_CACHE[self.name]

    async def get_webhook(self, bot: Bot) -> Webhook:
        if self.name not in _WEBHOOK_CACHE:
            _WEBHOOK_CACHE[self.name] = await self._find_or_create_webhook(bot)
        return _WEBHOOK_CACHE[self.name]

    async def _find_or_create_webhook(self, bot: Bot) -> Webhook:
        channel = await self.get_channel(bot)
        for webhook in await channel.webhooks():
            if webhook.name == _BOT_WEBHOOK_NAME:
                return webhook
        Log.i(f'Creating bot webhook in "{channel.name}" (Channel ID: {channel.id}).')
        return await channel.create_webhook(name=_BOT_WEBHOOK_NAME)
