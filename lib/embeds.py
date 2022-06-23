from __future__ import annotations

from pathlib import Path
from typing import Any, Final

from discord import Embed, File

from lib.common import Template

_DEFAULT_COLOR: Final[int] = 0x6C79FF

_ATTACHMENT_URL: Final[Template] = Template("attachment://$filename")
_TEXT_WITH_EMOJI: Final[Template] = Template("$emoji \u200B \u200B $text")


def get_embed(color: int = 0, text: str = "", emoji: str = "") -> Embed:
    return _create_embed_data(params=locals()).build_embed()


def get_embed_and_files(
    color: int = 0,
    text: str = "",
    emoji: str = "",
    thumbnail: str | File = "",
) -> (Embed, list[File]):
    embed_data = _create_embed_data(params=locals())
    return embed_data.build_embed(), embed_data.get_files()


def _create_embed_data(params: dict[str, Any]) -> _BaseEmbedData:
    constructor = _ThumbnailEmbedData if params.get("thumbnail") else _SimpleEmbedData
    return constructor(**params)


def _assert_valid_emoji(emoji: str) -> None:
    if (not emoji) or (len(emoji) != 1) or emoji.isascii():
        raise ValueError(f'Invalid emoji: "{emoji}" (Must be non-ascii & single-char.)')


class _BaseEmbedData:
    def __init__(self, color: int, **_) -> None:
        self._required_attr_names: Final[list[str]] = []
        self._files: Final[list[File]] = []
        self._color: Final[int] = color or _DEFAULT_COLOR

    def _validate(self) -> None:
        for attr_name in self._required_attr_names:
            if not getattr(self, f"_{attr_name}", None):
                raise AttributeError(
                    f'Required attribute "{attr_name}" is missing '
                    f'or empty for "{self.__class__.__name__}"!'
                )

    def build_embed(self) -> Embed:
        self._validate()
        return Embed(color=self._color)

    def get_files(self) -> list[File]:
        return self._files if self._files else Embed.Empty


class _SimpleEmbedData(_BaseEmbedData):
    def __init__(self, text: str, emoji: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._required_attr_names.append("text")
        self._text: Final[str] = text
        self._emoji: Final[str] = emoji  # Allowed to be empty.

    def _validate(self) -> None:
        super()._validate()
        if self._emoji:
            _assert_valid_emoji(self._emoji)

    def build_embed(self) -> Embed:
        embed = super().build_embed()
        if self._emoji:
            embed.description = _TEXT_WITH_EMOJI.sub(text=self._text, emoji=self._emoji)
        else:
            embed.description = self._text
        return embed


class _ThumbnailEmbedData(_SimpleEmbedData):
    def __init__(self, thumbnail: str | File, **kwargs) -> None:
        super().__init__(**kwargs)
        self._required_attr_names.append("thumbnail")
        self._thumbnail: str | File = thumbnail  # Intentionally not marked "Final".

    def _validate(self) -> None:
        if isinstance(self._thumbnail, str):
            # Convert the thumbnail string into a File if it exists and is valid.
            # Otherwise, assume it's a URL and leave it for Discord to deal with.
            if Path(self._thumbnail).is_file():
                self._thumbnail = File(fp=self._thumbnail)

        if isinstance(self._thumbnail, File):
            # Wrangle the File into the expected fields & format required by Discord.
            thumbnail_url = _ATTACHMENT_URL.sub(filename=self._thumbnail.filename)
            self._files.append(self._thumbnail)
            self._thumbnail = thumbnail_url

        # Perform standard validation AFTER any changes are made to the thumbnail field.
        # At this point, it should be a non-empty and well-formed URL string.
        super()._validate()

    def build_embed(self) -> Embed:
        return super().build_embed().set_thumbnail(url=self._thumbnail)
