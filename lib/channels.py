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

    @classmethod
    async def initialize_all(cls, bot: Bot):
        for enum_member in cls:
            name, uid = enum_member.name, enum_member.value
            channel = bot.get_channel(uid) or await bot.fetch_channel(uid)
            if not isinstance(channel, TextChannel):
                raise ValueError(f'Invalid "{name}" channel. (Specified ID: "{uid}")')
            _CHANNEL_CACHE[name] = channel

    LOGGING = auto()
    RULES = auto()
    WELCOME = auto()

    @property
    def url(self) -> str:
        return self._get_from_cache().jump_url

    async def get_webhook(self) -> Webhook:
        if self.name not in _WEBHOOK_CACHE:
            _WEBHOOK_CACHE[self.name] = await self._find_or_create_webhook()
        return _WEBHOOK_CACHE[self.name]

    async def _find_or_create_webhook(self) -> Webhook:
        channel = self._get_from_cache()
        for webhook in await channel.webhooks():
            if webhook.name == _BOT_WEBHOOK_NAME:
                return webhook
        Log.i(f'Creating bot webhook in "{channel.name}" (Channel ID: {channel.id}).')
        return await channel.create_webhook(name=_BOT_WEBHOOK_NAME)

    def _get_from_cache(self) -> TextChannel:
        return _CHANNEL_CACHE[self.name]
