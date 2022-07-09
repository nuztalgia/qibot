from datetime import datetime
from typing import Final

from aiohttp import ClientSession
from discord import ClientUser, Member
from discord.utils import utcnow
from humanize import naturaltime

from lib.utils.templates import Template

_CLIENT_SESSION: Final[ClientSession] = ClientSession()

_MEMBER_NAMETAG: Final[Template] = Template("${name}#${tag}")
_TIME_STAMP_FORMAT: Final[Template] = Template("<t:${timestamp}>")


def format_time(
    time: datetime, show_timestamp: bool = True, show_elapsed: bool = True
) -> str:
    results = []
    if show_timestamp:
        results.append(_TIME_STAMP_FORMAT.sub(timestamp=int(time.timestamp())))
    if show_elapsed:
        elapsed_time = naturaltime(utcnow() - time)
        results.append(f"({elapsed_time})" if results else elapsed_time)
    return " ".join(results)


def get_member_nametag(member: Member | ClientUser) -> str:
    return _MEMBER_NAMETAG.sub(name=member.name, tag=member.discriminator)


async def load_content_from_url(url: str) -> bytes:
    async with _CLIENT_SESSION.get(url) as response:
        return await response.read()
