from datetime import datetime, timezone
from json import load as load_json
from string import Template as StandardTemplate
from typing import Any, Callable, Final, Optional

from discord import Asset, Member
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


class Template(StandardTemplate):
    sub: Final[Callable[..., str]] = StandardTemplate.substitute
    safe_sub: Final[Callable[..., str]] = StandardTemplate.safe_substitute


class Utils:
    _MEMBER_NAMETAG: Final[Template] = Template("${name}#${tag}")
    _JSON_FILE_PATH: Final[Template] = Template("assets/data/${name}.json")

    @staticmethod
    def get_member_avatar(member: Member, size: int = 64) -> Asset:
        # Note: Discord will complain if "size" is not a power of 2.
        return member.display_avatar.with_size(size).with_format("png")

    @staticmethod
    def get_member_nametag(member: Member) -> str:
        return Utils._MEMBER_NAMETAG.sub(name=member.name, tag=member.discriminator)

    @staticmethod
    def load_json_file(name: str) -> dict[str, Any] | list[Any]:
        with open(Utils._JSON_FILE_PATH.sub(name=name), "r", encoding="utf-8") as file:
            return load_json(file)

    @staticmethod
    def format_time(time: datetime, include_elapsed: bool = True) -> str:
        result = f"<t:{int(time.timestamp())}>"
        if include_elapsed:
            # noinspection PyTypeChecker
            result += f" ({naturaltime(datetime.now(timezone.utc) - time)})"
        return result
