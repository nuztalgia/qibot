from __future__ import annotations

from enum import Enum, auto, unique
from random import choice as choose_random
from typing import Any, Final, Iterable, Optional, TypeAlias

from discord import Bot, File, Member

from lib.channels import Channel
from lib.common import Template, Utils
from lib.embeds import EmbedData, FieldData
from lib.logger import Log

_ActionDict: TypeAlias = dict[str, str | list[str]]


@unique
class _Action(Enum):
    MEMBER_JOINED = auto()
    MEMBER_LEFT = auto()
    MENTION_RULES = auto()

    @property
    def key(self) -> str:
        return self.name.lower()

    @classmethod
    def _is_defined(cls, key: str) -> bool:
        return any(member for member in cls if key.lower() == member.key)

    @classmethod
    def sanitize(cls, action_dict: _ActionDict) -> _ActionDict:
        sanitized_dict = {}
        for key in list(action_dict):
            if cls._is_defined(key):
                sanitized_dict[key] = action_dict[key]
            else:
                Log.w(f'    "{key}" is not a recognized action. Ignoring.')
        return sanitized_dict

    def get_response(self, action_dict: _ActionDict) -> str:
        response = ""
        if self.key in action_dict:
            # Use the single defined string, or a random choice from the defined list.
            response = action_dict[self.key]
            if isinstance(response, list):
                response = choose_random(response)
        return response


class _Character:
    _DATA: Final[dict[str, Any]] = Utils.load_json_file(name="characters")

    def __init__(self) -> None:
        self._name: Final[str] = self.__class__.__name__.strip("_").title()

        Log.d(f"  Initializing character: {self._name.upper()}")
        data: dict[str, Any] = _Character._DATA[self._name.upper()]

        self._avatar_url: Final[str] = data["avatar_url"]
        self._color: Final[int] = int(data["color"], base=16)
        self._dialogue: Final[_ActionDict] = _Action.sanitize(data["dialogue"])
        self._emoji: Final[_ActionDict] = _Action.sanitize(data["emoji"])

    def _get_dialogue(self, action: _Action, **kwargs) -> str:
        dialogue = action.get_response(self._dialogue)
        if not dialogue:
            Log.e(f'Dialogue for "{action.key}" is not defined for {self._name}.')
        return Template(dialogue).safe_sub(kwargs)

    def _get_emoji(self, action: _Action) -> str:
        return action.get_response(self._emoji)

    async def _send_message(
        self,
        bot: Bot,
        channel: Channel,
        text: str,
        emoji: str = "",
        thumbnail: Optional[str | File] = None,
        fields: Optional[Iterable[FieldData]] = None,
    ) -> None:
        embed_data = EmbedData.create(self._color, text, emoji, thumbnail, fields)
        await (await channel.get_webhook(bot)).send(
            username=self._name,
            avatar_url=self._avatar_url,
            embed=embed_data.build_embed(),
            files=embed_data.get_files(),
        )


class _Bouncer(_Character):
    async def announce_member_joined(self, bot: Bot, member: Member) -> None:
        extras = [
            FieldData("🐣", "Account Created", Utils.format_time(member.created_at)),
        ]
        await self._announce_member_action(bot, member, _Action.MEMBER_JOINED, extras)

    async def announce_member_left(self, bot: Bot, member: Member) -> None:
        extras = [
            FieldData("🌱", "Joined Server", Utils.format_time(member.joined_at)),
            FieldData("🍂", "Server Roles", [role.mention for role in member.roles[1:]]),
        ]
        await self._announce_member_action(bot, member, _Action.MEMBER_LEFT, extras)

    async def _announce_member_action(
        self, bot: Bot, member: Member, action: _Action, extras: Iterable[FieldData]
    ) -> None:
        await self._send_message(
            bot=bot,
            channel=Channel.LOGGING,
            text=f"**{self._get_dialogue(action, name=member.mention)}**",
            emoji=self._get_emoji(action),
            thumbnail=Utils.get_member_avatar(member).url,
            fields=[
                FieldData("❄", "Unique ID", str(member.id), True),
                FieldData("🏷️", "Current Tag", Utils.get_member_nametag(member), True),
                *extras,
            ],
        )


class _Sandy(_Character):
    def __init__(self) -> None:
        super().__init__()
        self._rules_link: str = ""

    async def greet(self, bot: Bot, member: Member) -> None:
        if not self._rules_link:
            channel = await Channel.RULES.get_channel(bot)
            self._rules_link = f'[rules]({channel.jump_url} "Go on... click the link!")'
        welcome_text = self._get_dialogue(_Action.MEMBER_JOINED, name=member.mention)
        rules_text = self._get_dialogue(_Action.MENTION_RULES, rules=self._rules_link)
        await self._send_message(
            bot=bot,
            channel=Channel.WELCOME,
            text=f"{welcome_text}\n\n{rules_text}",
            emoji=self._get_emoji(_Action.MEMBER_JOINED),
            thumbnail="assets/images/sandy_wave.gif",  # TODO: Personalize this image.
        )


BOUNCER: Final[_Bouncer] = _Bouncer()
SANDY: Final[_Sandy] = _Sandy()
