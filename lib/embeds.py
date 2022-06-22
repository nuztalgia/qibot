from typing import Final

from discord import Embed

_DEFAULT_COLOR: Final[int] = 0x6C79FF
_SPACING: Final[str] = "\u200B \u200B"


class _BaseEmbed:
    def __init__(self, color: int = _DEFAULT_COLOR) -> None:
        self._required_attr_names: Final[list[str]] = []
        self._color: Final[int] = color

    def _validate(self) -> None:
        for attr_name in self._required_attr_names:
            if not getattr(self, f"_{attr_name}", None):
                raise AttributeError(
                    f'Required attribute "{attr_name}" is missing '
                    f'or empty for "{self.__class__.__name__}"!'
                )

    def _build_discord_embed(self) -> Embed:
        self._validate()
        return Embed(color=self._color)


class SimpleEmbed(_BaseEmbed):
    def __init__(self, text: str, emoji: str, color: int) -> None:
        super().__init__(color)
        self._text: Final[str] = text
        self._emoji: Final[str] = emoji
        self._required_attr_names.append("text")

    @staticmethod
    def create(text: str, emoji: str = "", color: int = 0) -> Embed:
        embed = SimpleEmbed(text, emoji, color)
        return embed._build_discord_embed()

    def _validate(self) -> None:
        super()._validate()
        if self._emoji and ((len(self._emoji) != 1) or self._emoji.isascii()):
            raise ValueError(f'Invalid value for "emoji" string: "{self._emoji}"')

    def _build_discord_embed(self) -> Embed:
        embed = super()._build_discord_embed()
        embed.description = self._get_description_text()
        return embed

    def _get_description_text(self) -> str:
        return f"{self._emoji} {_SPACING} {self._text}" if self._emoji else self._text
