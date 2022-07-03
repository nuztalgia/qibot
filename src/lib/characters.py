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

_ActionDict: TypeAlias = dict[str, dict[str, str | list[str]]]


class Characters:
    _GREETER: ClassVar[_Greeter]
    _REPORTER: ClassVar[_Reporter]

    @classmethod
    async def initialize(cls) -> None:
        Log.d("Loading character data...")
        _Character.DATA = Utils.load_json_from_file(filename="characters")
        cls._GREETER = _Greeter()
        cls._REPORTER = _Reporter()

    @classmethod
    async def greet(cls, member: Member) -> None:
        await cls._GREETER.greet(member)

    @classmethod
    async def report_member_joined(cls, member: Member) -> None:
        extras = [
            FieldData("🐣", "Account Created", Utils.format_time(member.created_at)),
        ]
        await cls._REPORTER.report_member_action(member, _Action.MEMBER_JOINED, extras)

    @classmethod
    async def report_member_left(cls, member: Member) -> None:
        extras = [
            FieldData("🌱", "Joined Server", Utils.format_time(member.joined_at)),
            FieldData("🍂", "Server Roles", [role.mention for role in member.roles[1:]]),
        ]
        await cls._REPORTER.report_member_action(member, _Action.MEMBER_LEFT, extras)

    @classmethod
    async def report_member_renamed(cls, member: Member, old_name: str) -> None:
        extras = [
            FieldData("🌘", "Old Name", old_name, True),
            FieldData("🌔", "New Name", member.display_name, True),
            FieldData(inline=True),  # Blank field to properly align with common fields.
        ]
        await cls._REPORTER.report_member_action(member, _Action.MEMBER_RENAMED, extras)


@unique
class _Action(Enum):
    MEMBER_JOINED = auto()
    MEMBER_LEFT = auto()
    MEMBER_RENAMED = auto()
    MENTION_RULES = auto()

    @property
    def key(self) -> str:
        return self.name.lower()

    @classmethod
    def _is_defined(cls, key: str) -> bool:
        return any(action for action in cls if key == action.key)

    @classmethod
    def sanitize(cls, action_dict: _ActionDict) -> _ActionDict:
        sanitized_dict = {}
        for key in list(action_dict):
            if cls._is_defined(key):
                sanitized_dict[key] = action_dict[key]
            else:
                Log.w(f'  "{key}" is not a recognized action. Ignoring.')
        return sanitized_dict


class _Character:
    DATA: ClassVar[dict[str, Any]]

    def __init__(self) -> None:
        role = self.__class__.__name__.strip("_")
        Log.d(f'  Initializing character for role "{role}".')
        data = type(self).DATA[role.lower()]

        self._name: Final[str] = data["name"]
        self._color: Final[int] = int(data["color"], base=16)
        self._avatar_url: Final[str] = data["avatar_url"]
        self._responses: Final[_ActionDict] = _Action.sanitize(data["responses"])

        Log.d(f'    Name: "{self._name}"')
        Log.d(f"    Supported actions: [{', '.join(self._responses)}]")

    def _get_response(self, action: _Action, category: str) -> str:
        response = ""
        if action.key in self._responses:
            # Use the single defined string, or a random choice from the defined list.
            response = self._responses[action.key].get(category, response)
            if isinstance(response, list):
                response = choose_random(response)
        return response

    def _get_dialogue(self, action: _Action, **kwargs) -> str:
        dialogue = self._get_response(action, "dialogue")
        if not dialogue:
            Log.e(f'Dialogue for "{action.key}" is not defined for {self._name}.')
        available_subs = self._responses[action.key] | kwargs
        while available_subs.keys() & Utils.get_template_keys(dialogue):
            dialogue = Template(dialogue).safe_sub(available_subs)
        return dialogue

    async def _send_message(
        self,
        action: _Action,
        channel: Channel,
        text: str,
        thumbnail: Optional[str | File] = None,
        fields: Optional[Iterable[FieldData]] = None,
    ) -> None:
        emoji = self._get_response(action, "emoji")
        thumbnail = thumbnail or self._get_response(action, "thumbnail")
        embed_data = EmbedData.create(self._color, text, emoji, thumbnail, fields)
        await (await channel.get_webhook()).send(
            username=self._name,
            avatar_url=self._avatar_url,
            embed=embed_data.build_embed(),
            files=embed_data.get_files(),
        )


class _Greeter(_Character):
    async def greet(self, member: Member) -> None:
        welcome_text = self._get_dialogue(_Action.MEMBER_JOINED, name=member.mention)
        rules_text = self._get_dialogue(_Action.MENTION_RULES, url=Channel.RULES.url)
        await self._send_message(
            action=_Action.MEMBER_JOINED,
            channel=Channel.WELCOME,
            text=f"{welcome_text}\n\n{rules_text}",
        )


class _Reporter(_Character):
    async def report_member_action(
        self, member: Member, action: _Action, extra_fields: list[FieldData]
    ) -> None:
        await self._send_message(
            action=action,
            channel=Channel.LOGGING,
            text=f"**{self._get_dialogue(action, name=member.mention)}**",
            thumbnail=await ImageUtils.get_member_avatar(member),
            fields=[
                FieldData("❄", "Unique ID", str(member.id), True),
                FieldData("🏷️", "Current Tag", Utils.get_member_nametag(member), True),
                FieldData(inline=True),  # Force extra fields to start on the next row.
                *extra_fields,
            ],
        )
