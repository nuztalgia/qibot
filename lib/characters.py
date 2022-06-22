from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique
from random import choice
from typing import ClassVar, Final

from discord import AllowedMentions, Webhook

from lib.common import Template, load_json_file
from lib.logger import Log

_UNKNOWN_ACTION_TEMPLATE: Final[Template] = Template(
    "Um... I'm not sure how to handle `$action_key`. Sorry!"
)


@unique
class Action(Enum):
    MEMBER_JOINED = AllowedMentions(users=True)
    MEMBER_LEFT = AllowedMentions.none()

    @classmethod
    def is_defined(cls, key: str) -> bool:
        return any(member for member in cls if key == member.key)

    @property
    def key(self) -> str:
        return self.name.lower()

    @property
    def allowed_mentions(self) -> AllowedMentions:
        return self.value


@dataclass(frozen=True)
class Character:
    BOUNCER: ClassVar[Character] = None
    SANDY: ClassVar[Character] = None

    name: str
    color: str
    avatar_url: str
    action_strings: dict[str, str | list[str]]

    @classmethod
    def initialize_all(cls) -> None:
        for character in load_json_file(file_name="characters"):
            character_name = character.get("name", "<No Name>").upper()
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

    async def speak(self, webhook: Webhook, message_text: str, **kwargs) -> None:
        await webhook.send(
            message_text, username=self.name, avatar_url=self.avatar_url, **kwargs
        )

    async def handle(self, action: Action, webhook: Webhook, **kwargs) -> None:
        await self.speak(
            webhook=webhook,
            message_text=self._get_message_text_for_action(action.key, **kwargs),
            allowed_mentions=(
                kwargs.get("allowed_mentions", action.allowed_mentions)
                if action.key in self.action_strings
                else AllowedMentions.none()
            ),
        )

    def _get_message_text_for_action(self, action_key: str, **kwargs) -> str:
        if action_key in self.action_strings:
            # Use the single defined string, or a random choice from the defined list.
            action_value = self.action_strings[action_key]
            if isinstance(action_value, list):
                action_value = choice(action_value)
            return Template(action_value).safe_sub(kwargs)
        else:
            return _UNKNOWN_ACTION_TEMPLATE.sub(action_key=action_key)
