from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto, unique
from random import choice
from typing import ClassVar, Final

from discord import Embed, Webhook

from lib.common import Template, load_json_file
from lib.embeds import SimpleEmbed
from lib.logger import Log

_UNKNOWN_ACTION_TEMPLATE: Final[Template] = Template(
    "Um... I'm not sure how to handle `$action_key`. Sorry!"
)


@unique
class Action(Enum):
    MEMBER_JOINED = auto()
    MEMBER_LEFT = auto()

    @classmethod
    def is_defined(cls, key: str) -> bool:
        return any(member for member in cls if key == member.key)

    @property
    def key(self) -> str:
        return self.name.lower()


@dataclass(frozen=True)
class Character:
    BOUNCER: ClassVar[Character] = None
    SANDY: ClassVar[Character] = None

    name: str
    color: int
    avatar_url: str
    action_strings: dict[str, str | list[str]]

    @classmethod
    def initialize_all(cls) -> None:
        for character in load_json_file(file_name="characters"):
            character_name = character.get("name", "<No Name>").upper()
            character["color"] = int(character.get("color", "0"), base=16)
            if hasattr(cls, character_name):
                Log.d(f"  Initializing character: {character_name}")
                setattr(cls, character_name, cls(**character))
            else:
                Log.w(f'  "{character_name}" is not a recognized character. Ignoring.')

    def __post_init__(self) -> None:
        for action_key in list(self.action_strings):
            if not Action.is_defined(action_key):
                Log.w(f'    "{action_key}" is not a recognized action. Ignoring.')
                self.action_strings.pop(action_key)
        Log.d(f"    Supported actions: [{', '.join(self.action_strings)}]")

    async def handle(self, action: Action, webhook: Webhook, **kwargs) -> None:
        embed = self._get_embed(action, **kwargs)
        await webhook.send(username=self.name, avatar_url=self.avatar_url, embed=embed)

    def _get_embed(self, action: Action, **kwargs) -> Embed:
        return SimpleEmbed.create(
            text=self._get_dialogue(action, **kwargs),
            emoji=kwargs.get("emoji", ""),
            color=self.color,
        )

    def _get_dialogue(self, action: Action, **kwargs) -> str:
        if action.key in self.action_strings:
            # Use the single defined string, or a random choice from the defined list.
            action_value = self.action_strings[action.key]
            if isinstance(action_value, list):
                action_value = choice(action_value)
            return Template(action_value).safe_sub(kwargs)
        else:
            return _UNKNOWN_ACTION_TEMPLATE.sub(action_key=action.key)
