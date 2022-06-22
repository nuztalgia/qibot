import json
from string import Template as _Template
from typing import Any, Callable, Final, TypeAlias

from discord import TextChannel, Webhook
from dotenv import dotenv_values, find_dotenv

_TemplateMethod: TypeAlias = Callable[..., str]

_ENV_CONFIG: Final[dict[str, bool | int | str]] = dotenv_values(
    dotenv_path=find_dotenv(), verbose=True
)


class Constants:
    # Required environment config settings.
    BOT_TOKEN: Final[str] = _ENV_CONFIG.get("BOT_TOKEN")
    HOME_SERVER_ID: Final[int] = int(_ENV_CONFIG.get("HOME_SERVER_ID"))

    # Optional environment config settings.
    COMMAND_PREFIX: Final[str] = _ENV_CONFIG.get("COMMAND_PREFIX", ".")
    LOG_THRESHOLD: Final[str] = _ENV_CONFIG.get("LOG_THRESHOLD", "info").upper()
    DEV_MODE_ENABLED: Final[bool] = _ENV_CONFIG.get("DEV_MODE_ENABLED", False)
    SALUTATIONS_CHANNEL_ID: Final[int] = _ENV_CONFIG.get("SALUTATIONS_CHANNEL_ID", 0)


class Template(_Template):
    sub: Final[_TemplateMethod] = _Template.substitute
    safe_sub: Final[_TemplateMethod] = _Template.safe_substitute


class Json:
    _FILE_PATH_TEMPLATE: Final[Template] = Template("assets/$dir_name/$file_name.json")

    @staticmethod
    def load_from_file(dir_name: str, file_name: str) -> dict[str, Any] | list[Any]:
        path = Json._FILE_PATH_TEMPLATE.sub(dir_name=dir_name, file_name=file_name)
        with open(path, "r") as file:
            return json.load(file)


class Webhooks:
    _BOT_WEBHOOK_NAME: Final[str] = "QiBot Webhook"

    @staticmethod
    async def get_bot_webhook(channel: TextChannel) -> Webhook:
        for webhook in await channel.webhooks():
            if webhook.name == Webhooks._BOT_WEBHOOK_NAME:
                return webhook
        Log.i(f"Creating bot webhook in '{channel.name}' (Channel ID: {channel.id}).")
        return await channel.create_webhook(name=Webhooks._BOT_WEBHOOK_NAME)
