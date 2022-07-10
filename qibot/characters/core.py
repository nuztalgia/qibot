from enum import Enum, auto, unique
from random import choice as choose_random
from typing import Any, Final, TypeAlias

from discord import ApplicationContext, File

from qibot.embeds import Fields, create_embed_with_files
from qibot.utils import (
    BotChannel,
    Log,
    Template,
    get_template_keys,
    load_json_from_file,
)

_ActionDict: TypeAlias = dict[str, dict[str, str | list[str]]]


@unique
class Action(Enum):
    BOT_HELP = auto()
    BOT_METADATA = auto()
    MEMBER_JOINED = auto()
    MEMBER_LEFT = auto()
    MEMBER_RENAMED = auto()
    MENTION_RULES = auto()

    @property
    def key(self) -> str:
        return self.name.lower()

    @classmethod
    def sanitize(cls, action_dict: _ActionDict) -> _ActionDict:
        sanitized_dict = {}
        for key in list(action_dict):
            if any(action for action in cls if key == action.key):
                sanitized_dict[key] = action_dict[key]
            else:
                Log.w(f'  "{key}" is not a recognized action. Ignoring.')
        return sanitized_dict


class Character:
    DATA: Final[dict[str, Any]] = load_json_from_file(filename="characters")

    def __init__(self) -> None:
        role = self.__class__.__name__.strip("_")
        Log.d(f'Initializing character for role "{role}".')
        data = type(self).DATA[role.lower()]

        self._name: Final[str] = data.get("name")
        self._color: Final[int] = int(data.get("color", "0"), base=16)
        self._avatar_url: Final[str] = data.get("avatar_url")
        self._responses: Final[_ActionDict] = Action.sanitize(data["responses"])

        if self._name:
            Log.d(f'  Name: "{self._name}"')
        Log.d(f"  Supported actions: [{', '.join(self._responses)}]")

    def _get_response(self, action: Action, category: str) -> str:
        if action.key in self._responses:
            # Use the single defined string, or a random choice from the defined list.
            response = self._responses[action.key].get(category, "")
            if isinstance(response, list):
                response = choose_random(response)
            return response
        else:
            return ""

    def _get_dialogue(self, action: Action, **kwargs) -> str:
        dialogue = self._get_response(action, "dialogue")
        if not dialogue:
            Log.e(f'Dialogue for "{action.key}" is not defined for {self._name}.')
        available_subs = self._responses[action.key] | kwargs
        while available_subs.keys() & get_template_keys(dialogue):
            dialogue = Template(dialogue).safe_sub(available_subs)
        return dialogue

    async def _send_message(
        self,
        action: Action,
        destination: ApplicationContext | BotChannel,
        text: str = "",
        thumbnail: str | File | None = None,
        fields: Fields | None = None,
    ) -> None:
        embed, files = create_embed_with_files(
            color=self._color,
            text=text or self._get_dialogue(action),
            emoji=self._get_response(action, "emoji"),
            thumbnail=thumbnail or self._get_response(action, "thumbnail"),
            fields=fields,
        )
        if isinstance(destination, ApplicationContext):
            await destination.respond(embed=embed)
        else:
            await (await destination.get_webhook()).send(
                username=self._name,
                avatar_url=self._avatar_url,
                embed=embed,
                files=files,
            )
