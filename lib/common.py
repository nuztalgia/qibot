from datetime import datetime, timezone
from json import load as load_json
from string import Template as _Template
from typing import Any, Callable, Final

from discord import Asset, Member
from dotenv import dotenv_values, find_dotenv
from humanize import naturaltime

_ENV_CONFIG: Final[dict[str, Any]] = dotenv_values(
    dotenv_path=find_dotenv(), verbose=True
)


class Constants:
    BOT_VERSION: Final[str] = "0.1.0"
    BOT_TOKEN: Final[str] = _ENV_CONFIG["BOT_TOKEN"]
    HOME_SERVER_ID: Final[int] = int(_ENV_CONFIG["HOME_SERVER_ID"])
    COMMAND_PREFIX: Final[str] = _ENV_CONFIG.get("COMMAND_PREFIX", ".")
    DEV_MODE_ENABLED: Final[bool] = _ENV_CONFIG.get("DEV_MODE_ENABLED", False)


class Template(_Template):
    sub: Final[Callable[..., str]] = _Template.substitute
    safe_sub: Final[Callable[..., str]] = _Template.safe_substitute


class Utils:
    _MEMBER_NAMETAG: Final[Template] = Template("${name}#${tag}")
    _JSON_FILE_PATH: Final[Template] = Template("assets/data/${name}.json")

    @staticmethod
    def get_channel_id(channel_name: str) -> int:
        return _ENV_CONFIG.get(f"{channel_name}_CHANNEL_ID", 0)

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
