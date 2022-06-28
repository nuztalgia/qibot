from __future__ import annotations

from enum import Enum, auto, unique
from random import choice as choose_random
from typing import Any, ClassVar, Final, Iterable, Optional, TypeAlias

from discord import File, Member

from lib.channels import Channel
from lib.common import Template, Utils
from lib.embeds import EmbedData, FieldData
from lib.images import ImageUtils
from lib.logger import Log

_ActionDict: TypeAlias = dict[str, str | list[str]]


class Characters:
    BOUNCER: ClassVar[_Bouncer]
    SANDY: ClassVar[_Sandy]

    @classmethod
    async def initialize(cls) -> None:
        Log.d("Loading character data...")
        _Character.DATA = await Utils.load_json_from_file(name="characters")
        cls.BOUNCER = _Bouncer()
        cls.SANDY = _Sandy()


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
                Log.w(f'  "{key}" is not a recognized action. Ignoring.')
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
    DATA: ClassVar[dict[str, Any]]

    def __init__(self) -> None:
        self._name: Final[str] = self.__class__.__name__.strip("_").title()

        Log.d(f"  Initializing character: {self._name.upper()}")
        data: Final[dict[str, Any]] = type(self).DATA[self._name.upper()]

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
        channel: Channel,
        text: str,
        emoji: str = "",
        thumbnail: Optional[str | File] = None,
        fields: Optional[Iterable[FieldData]] = None,
    ) -> None:
        embed_data = EmbedData.create(self._color, text, emoji, thumbnail, fields)
        await (await channel.get_webhook()).send(
            username=self._name,
            avatar_url=self._avatar_url,
            embed=embed_data.build_embed(),
            files=embed_data.get_files(),
        )


class _Bouncer(_Character):
    async def announce_member_joined(self, member: Member) -> None:
        extra_fields = [
            FieldData("🐣", "Account Created", Utils.format_time(member.created_at)),
        ]
        await self._announce_member_action(member, _Action.MEMBER_JOINED, extra_fields)

    async def announce_member_left(self, member: Member) -> None:
        extra_fields = [
            FieldData("🌱", "Joined Server", Utils.format_time(member.joined_at)),
            FieldData("🍂", "Server Roles", [role.mention for role in member.roles[1:]]),
        ]
        await self._announce_member_action(member, _Action.MEMBER_LEFT, extra_fields)

    async def _announce_member_action(
        self, member: Member, action: _Action, extra_fields: Iterable[FieldData]
    ) -> None:
        await self._send_message(
            channel=Channel.LOGGING,
            text=f"**{self._get_dialogue(action, name=member.mention)}**",
            emoji=self._get_emoji(action),
            thumbnail=await ImageUtils.get_member_avatar(member),
            fields=[
                FieldData("❄", "Unique ID", str(member.id), True),
                FieldData("🏷️", "Current Tag", Utils.get_member_nametag(member), True),
                *extra_fields,
            ],
        )


class _Sandy(_Character):
    def __init__(self) -> None:
        super().__init__()
        self.rules_text: Final[str] = self._get_dialogue(
            action=_Action.MENTION_RULES,
            rules=f'[rules]({Channel.RULES.url} "Go on... click the link!")',
        )

    async def greet(self, member: Member) -> None:
        welcome_text = self._get_dialogue(_Action.MEMBER_JOINED, name=member.mention)
        await self._send_message(
            channel=Channel.WELCOME,
            text=f"{welcome_text}\n\n{self.rules_text}",
            emoji=self._get_emoji(_Action.MEMBER_JOINED),
            thumbnail="assets/images/sandy_wave.gif",  # TODO: Personalize this image.
        )
