from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable

from discord import Embed, File

from lib.common import Template

_DEFAULT_COLOR: Final[int] = 0x6C79FF
_SPACING: Final[str] = " \u200B "

_ATTACHMENT_URL: Final[Template] = Template("attachment://$filename")
_TEXT_WITH_EMOJI: Final[Template] = Template(f"$emoji{_SPACING}$text")

_FIELD_CONTENT: Final[Template] = Template(
    f"{_TEXT_WITH_EMOJI.safe_sub(emoji='▪')}{_SPACING * 4}"  # Extra horizontal padding.
)
_EMPTY_FIELD_CONTENT: Final[str] = _TEXT_WITH_EMOJI.sub(emoji="✖", text="*None!*")


def _assert_valid_emoji(emoji: str) -> None:
    if (not emoji) or (len(emoji) > 2) or emoji.isascii():
        raise ValueError(f'Invalid emoji: "{emoji}" (Must be non-ascii and <=2 chars.)')


@dataclass(frozen=True)
class FieldData:
    emoji: str = ""  # Required for non-blank fields.
    title: str = ""  # Required for non-blank fields.
    content: str | Iterable[str] | None = None
    inline: bool = False


class EmbedData:
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
        return self._files or Embed.Empty

    @staticmethod
    def create(
        color: int = 0,
        text: str = "",
        emoji: str = "",
        thumbnail: str | File | None = None,
        fields: Iterable[FieldData] | None = None,
    ) -> EmbedData:
        params = locals()
        cls = _ThumbnailEmbedData if params.get("thumbnail") else _SimpleEmbedData
        if params.get("fields"):
            cls = type(f"{cls.__name__}WithFields", (_FieldsMixin, cls), {})
        return cls(**params)


class _FieldsMixin(EmbedData):
    def __init__(self, fields: Iterable[FieldData], **kwargs) -> None:
        super().__init__(**kwargs)
        self._required_attr_names.append("fields")
        self._fields: Final[Iterable[FieldData]] = tuple(fields)  # Make it immutable.

    def _validate(self) -> None:
        super()._validate()
        for field in self._fields:
            # Validate any non-blank fields. (Blank fields are allowed for formatting.)
            if field.emoji or field.title or field.content:
                _assert_valid_emoji(field.emoji)
                if not field.title:
                    raise ValueError("A title is required for all fields.")

    def build_embed(self) -> Embed:
        embed = super().build_embed()
        for field in self._fields:
            embed.add_field(
                name=_TEXT_WITH_EMOJI.sub(emoji=field.emoji, text=field.title),
                value=type(self)._get_field_value(field),
                inline=field.inline,
            )
        return embed

    @classmethod
    def _get_field_value(cls, field: FieldData) -> str:
        if not (field.emoji or field.title):
            return _SPACING
        elif not field.content:
            return _EMPTY_FIELD_CONTENT
        elif isinstance(field.content, str):
            return _FIELD_CONTENT.sub(text=field.content)
        else:
            return "\n".join(_FIELD_CONTENT.sub(text=text) for text in field.content)


class _SimpleEmbedData(EmbedData):
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
        # Convert the thumbnail string into a File if it exists and is valid.
        # Otherwise, assume it's a URL and leave it for Discord to deal with.
        if isinstance(self._thumbnail, str) and Path(self._thumbnail).is_file():
            self._thumbnail = File(fp=self._thumbnail)

        # Wrangle the File into the expected fields & format required by Discord.
        if isinstance(self._thumbnail, File):
            thumbnail_url = _ATTACHMENT_URL.sub(filename=self._thumbnail.filename)
            self._files.append(self._thumbnail)
            self._thumbnail = thumbnail_url

        # Perform standard validation AFTER any changes are made to the thumbnail field.
        # At this point, it should be a non-empty and well-formed URL string.
        super()._validate()

    def build_embed(self) -> Embed:
        return super().build_embed().set_thumbnail(url=self._thumbnail)
