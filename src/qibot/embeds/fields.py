from typing import Final, Iterable

from discord import Embed

from qibot.embeds.core import SPACING, TEXT_WITH_EMOJI, EmbedData, assert_valid_emoji
from qibot.embeds.fielddata import FieldData
from qibot.utils import Template

_FIELD_CONTENT: Final[Template] = Template(
    f"{TEXT_WITH_EMOJI.safe_sub(emoji='▪')}{SPACING * 4}"  # Extra horizontal padding.
)
_EMPTY_FIELD_CONTENT: Final[str] = TEXT_WITH_EMOJI.sub(emoji="✖", text="*None!*")


class FieldsMixin(EmbedData):
    def __init__(self, fields: Iterable[FieldData], **kwargs) -> None:
        super().__init__(**kwargs)
        self._required_attr_names.append("fields")
        self._fields: Final[Iterable[FieldData]] = tuple(fields)  # Make it immutable.

    def _validate(self) -> None:
        super()._validate()
        for field in self._fields:
            # Validate any non-blank fields. (Blank fields are allowed for formatting.)
            if field.emoji or field.title or field.content:
                assert_valid_emoji(field.emoji)
                if not field.title:
                    raise ValueError("A title is required for all fields.")

    def build_embed(self) -> Embed:
        embed = super().build_embed()
        for field in self._fields:
            embed.add_field(
                name=TEXT_WITH_EMOJI.sub(emoji=field.emoji, text=field.title),
                value=type(self)._get_field_value(field),
                inline=field.inline,
            )
        return embed

    @classmethod
    def _get_field_value(cls, field: FieldData) -> str:
        if not (field.emoji or field.title):
            return SPACING
        elif not field.content:
            return _EMPTY_FIELD_CONTENT
        elif isinstance(field.content, str):
            return _FIELD_CONTENT.sub(text=field.content)
        else:
            return "\n".join(_FIELD_CONTENT.sub(text=text) for text in field.content)
