from enum import Enum, auto
from typing import Any, Final

from discord import ApplicationContext, Bot, TextChannel, Webhook

from qibot.utils.json import load_dict_from_file
from qibot.utils.logging import Log
from qibot.utils.templates import Template

_BOT_WEBHOOK_NAME: Final[str] = "QiBot Webhook"

_CTX_MISMATCH: Final[Template] = Template("That command is only available in <#$id>.")

_CHANNEL_CACHE: Final[dict[str, TextChannel]] = {}
_WEBHOOK_CACHE: Final[dict[str, Webhook]] = {}

_CONFIG: Final[dict[str, Any]] = load_dict_from_file(filename="config")

BOT_TOKEN: Final[str] = _CONFIG["bot_token"]
SERVER_ID: Final[int] = _CONFIG["server_id"]


class BotChannel(Enum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, values: list) -> int:
        return _CONFIG["channel_ids"].get(name.lower(), 0)

    @classmethod
    async def initialize_all(cls, bot: Bot) -> None:
        for enum_member in cls:
            name, uid = enum_member.name, enum_member.value
            channel = bot.get_channel(uid) or await bot.fetch_channel(uid)
            if not isinstance(channel, TextChannel):
                raise ValueError(f'Invalid "{name}" channel. (Specified ID: "{uid}")')
            _CHANNEL_CACHE[name] = channel

    ADMIN_LOG = auto()
    BOT_SPAM = auto()
    RULES = auto()
    WELCOME = auto()

    @property
    def url(self) -> str:
        return self._get_from_cache().jump_url

    async def is_context(self, ctx: ApplicationContext, respond: bool = True) -> bool:
        if ctx.channel_id == self.value:
            return True
        elif respond:
            await ctx.respond(_CTX_MISMATCH.sub(id=self.value), ephemeral=True)
        return False

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
