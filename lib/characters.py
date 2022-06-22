from __future__ import annotations

from enum import Enum, auto, unique
from random import choice as choose_random
from typing import Any, Final, Optional

from discord import Bot, Embed, File, MISSING, Member, Webhook

from lib.channels import Channel
from lib.common import Template, load_json_file
from lib.embeds import SimpleEmbed
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
    _DATA: Final[dict[str, Any]] = load_json_file(file_name="characters")

    def __init__(self) -> None:
        self._name: Final[str] = self.__class__.__name__.strip("_").upper()

        Log.d(f"  Initializing character: {self._name}")
        data: dict[str, Any] = _Character._DATA[self._name]

        self._avatar_url: Final[str] = data["avatar_url"]
        self._color: Final[int] = int(data["color"], base=16)
        self._dialogue: Final[dict[str, str | list[str]]] = data["dialogue"]

        for dialogue_key in list(self._dialogue):
            if not _Action.is_defined(dialogue_key):
                Log.w(f'    "{dialogue_key}" is not a recognized action. Ignoring.')
                self._dialogue.pop(dialogue_key)
        Log.d(f"    Supported actions: [{', '.join(self._dialogue)}]")

    async def _send_message(
        self, webhook: Webhook, embed: Embed, file: Optional[File] = None
    ) -> None:
        await webhook.send(
            username=self._name.title(),
            avatar_url=self._avatar_url,
            embed=embed,
            file=file if file else MISSING,
        )

    def _create_simple_embed(self, text: str, emoji: str = "") -> Embed:
        return SimpleEmbed.create(text=text, emoji=emoji, color=self._color)

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


class _Bouncer(_Character):
    async def announce_member_joined(self, bot: Bot, member: Member) -> None:
        await self._announce_member_action(bot, member, _Action.MEMBER_JOINED, "✨")

    async def announce_member_left(self, bot: Bot, member: Member) -> None:
        await self._announce_member_action(bot, member, _Action.MEMBER_LEFT, "💨")

    async def _announce_member_action(
        self, bot: Bot, member: Member, action: _Action, emoji: str
    ) -> None:
        await self._send_message(
            webhook=await Channel.LOGGING.get_webhook(bot),
            embed=self._create_simple_embed(
                text=self._get_dialogue(action, name=member.mention), emoji=emoji
            ),
        )


class _Sandy(_Character):
    async def greet(self, bot: Bot, member: Member) -> None:
        rules_channel = await Channel.RULES.get_channel(bot)
        rules_link = f'[rules]({rules_channel.jump_url} "Go on... click the link!")'
        embed = self._create_simple_embed(
            f"{self._get_dialogue(_Action.MEMBER_JOINED, name=member.mention)}\n\n"
            f"{self._get_dialogue(_Action.MENTION_RULES, rules=rules_link)}"
        )
        await self._send_message(
            webhook=await Channel.WELCOME.get_webhook(bot),
            embed=embed.set_thumbnail(url="attachment://sandy_wave.gif"),
            file=File(fp="assets/images/sandy_wave.gif"),
        )


BOUNCER: Final[_Bouncer] = _Bouncer()
SANDY: Final[_Sandy] = _Sandy()
