from __future__ import annotations

from enum import Enum, auto, unique
from random import choice as choose_random
from typing import Any, Final, Iterable, Optional

from discord import Bot, File, Member

from lib.channels import Channel
from lib.common import Template, Utils
from lib.embeds import EmbedData, FieldData
from lib.logger import Log


@unique
class _Action(Enum):
    MEMBER_JOINED = auto()
    MEMBER_LEFT = auto()
    MENTION_RULES = auto()

    @classmethod
    def is_defined(cls, dialogue_key: str) -> bool:
        return any(member for member in cls if dialogue_key == member.dialogue_key)

    @property
    def dialogue_key(self) -> str:
        return self.name.lower()


class _Character:
    _DATA: Final[dict[str, Any]] = Utils.load_json_file(file_name="characters")

    def __init__(self) -> None:
        self._name: Final[str] = self.__class__.__name__.strip("_").title()

        Log.d(f"  Initializing character: {self._name.upper()}")
        data: dict[str, Any] = _Character._DATA[self._name.upper()]

        self._avatar_url: Final[str] = data["avatar_url"]
        self._color: Final[int] = int(data["color"], base=16)
        self._dialogue: Final[dict[str, str | list[str]]] = data["dialogue"]

        for dialogue_key in list(self._dialogue):
            if not _Action.is_defined(dialogue_key):
                Log.w(f'    "{dialogue_key}" is not a recognized action. Ignoring.')
                self._dialogue.pop(dialogue_key)
        Log.d(f"    Supported actions: [{', '.join(self._dialogue)}]")

    def _get_dialogue(self, action: _Action, **kwargs) -> str:
        dialogue_key = action.dialogue_key
        if dialogue_key in self._dialogue:
            # Use the single defined string, or a random choice from the defined list.
            dialogue_value = self._dialogue[dialogue_key]
            if isinstance(dialogue_value, list):
                dialogue_value = choose_random(dialogue_value)
            return Template(dialogue_value).safe_sub(kwargs)
        else:
            Log.e(f'Dialogue for "{dialogue_key}" is not defined for {self._name}.')

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
        await self._announce_member_action(bot, member, _Action.MEMBER_JOINED, "✨")

    async def announce_member_left(self, bot: Bot, member: Member) -> None:
        await self._announce_member_action(bot, member, _Action.MEMBER_LEFT, "💨")

    async def _announce_member_action(
        self, bot: Bot, member: Member, action: _Action, emoji: str
    ) -> None:
        text = self._get_dialogue(action, name=member.mention)
        await self._send_message(bot, Channel.LOGGING, text, emoji=emoji)


class _Sandy(_Character):
    def __init__(self) -> None:
        super().__init__()
        self._rules_link: str = ""

    async def greet(self, bot: Bot, member: Member) -> None:
        if not self._rules_link:
            channel = await Channel.RULES.get_channel(bot)
            self._rules_link = f'[rules]({channel.jump_url} "Go on... click the link!")'
        text = (
            f"{self._get_dialogue(_Action.MEMBER_JOINED, name=member.mention)}\n\n"
            f"{self._get_dialogue(_Action.MENTION_RULES, rules=self._rules_link)}"
        )
        await self._send_message(
            bot, Channel.WELCOME, text, thumbnail="assets/images/sandy_wave.gif"
        )


BOUNCER: Final[_Bouncer] = _Bouncer()
SANDY: Final[_Sandy] = _Sandy()
