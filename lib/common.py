import json
import re
import string
from datetime import datetime, timezone
from typing import Any, Callable, Final, Optional

from aiofiles import open as open_file
from aiohttp import ClientSession
from discord import Member
from dotenv import dotenv_values, find_dotenv
from humanize import naturaltime


class Constants:
    QI_BOT_VERSION: Final[str] = "0.1.0"
    DEFAULT_COMMAND_PREFIX: Final[str] = "."


class Config:
    _ENV: Final[dict[str, Any]] = dotenv_values(dotenv_path=find_dotenv(), verbose=True)

    BOT_TOKEN: Final[str] = _ENV["BOT_TOKEN"]
    SERVER_ID: Final[int] = int(_ENV["SERVER_ID"])
    DEV_MODE_ENABLED: Final[bool] = _ENV.get("DEV_MODE_ENABLED", False)
    CUSTOM_COMMAND_PREFIX: Final[Optional[str]] = _ENV.get("CUSTOM_COMMAND_PREFIX")
    CUSTOM_LOG_THRESHOLD: Final[Optional[str]] = _ENV.get("CUSTOM_LOG_THRESHOLD")

    @classmethod
    def get_channel_id(cls, channel_name: str) -> int:
        return cls._ENV.get(f"{channel_name.upper()}_CHANNEL_ID", 0)


class Template(string.Template):
    sub: Final[Callable[..., str]] = string.Template.substitute
    safe_sub: Final[Callable[..., str]] = string.Template.safe_substitute


class Utils:
    _CLIENT_SESSION: Final[ClientSession] = ClientSession()

    _JSON_FILE_PATH: Final[Template] = Template("assets/data/${name}.json")
    _MEMBER_NAMETAG: Final[Template] = Template("${name}#${tag}")
    _TIME_FORMAT: Final[Template] = Template("<t:${timestamp}> (${elapsed})")

    _TEMPLATE_KEY_PATTERN: Final[re.Pattern] = re.compile(r"\${?(\w*)", re.ASCII)

    @classmethod
    def format_time(cls, time: datetime) -> str:
        # noinspection PyTypeChecker
        elapsed = naturaltime(datetime.now(timezone.utc) - time)
        return cls._TIME_FORMAT.sub(timestamp=int(time.timestamp()), elapsed=elapsed)

    @classmethod
    def get_member_nametag(cls, member: Member) -> str:
        return cls._MEMBER_NAMETAG.sub(name=member.name, tag=member.discriminator)

    @classmethod
    def get_template_keys(cls, template_string: str) -> set[str]:
        return set(cls._TEMPLATE_KEY_PATTERN.findall(template_string))

    @classmethod
    async def load_content_from_url(cls, url: str) -> bytes:
        async with cls._CLIENT_SESSION.get(url) as response:
            return await response.read()

    @classmethod
    async def load_json_from_file(
        cls, name: str, lowercase_keys: bool = False
    ) -> dict[str, Any] | list[Any]:
        filename = cls._JSON_FILE_PATH.sub(name=name)
        async with open_file(filename, mode="r", encoding="utf-8") as file:
            result = json.loads(await file.read())
        return cls._lowercase_keys(result) if lowercase_keys else result

    @classmethod
    def _lowercase_keys(cls, original: dict[str, Any]) -> dict[str, Any]:
        result = {}
        for key, value in original.items():
            new_value = cls._lowercase_keys(value) if isinstance(value, dict) else value
            result[key.lower()] = new_value
        return result
