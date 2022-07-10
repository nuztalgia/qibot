from typing import Final

from discord import Embed

from qibot.embeds.core import TEXT_WITH_EMOJI, EmbedData, assert_valid_emoji


class TextMixin(EmbedData):
    def __init__(self, text: str, emoji: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._required_attr_names.append("text")
        self._text: Final[str] = text
        self._emoji: Final[str] = emoji  # Allowed to be empty.

    def _validate(self) -> None:
        super()._validate()
        if self._emoji:
            assert_valid_emoji(self._emoji)

    def build_embed(self) -> Embed:
        embed = super().build_embed()
        if self._emoji:
            embed.description = TEXT_WITH_EMOJI.sub(text=self._text, emoji=self._emoji)
        else:
            embed.description = self._text
        return embed
