from __future__ import annotations

from collections.abc import Iterable
from typing import Final, NamedTuple, TypeAlias

_FieldContent: TypeAlias = str | Iterable[str] | None
_PartialFieldData: TypeAlias = tuple[str, str, _FieldContent]


class FieldData(NamedTuple):
    emoji: str = ""  # Required for non-blank fields.
    title: str = ""  # Required for non-blank fields.
    content: _FieldContent = None
    inline: bool = True


Fields: TypeAlias = list[FieldData]

_BLANK_FIELD: Final[FieldData] = FieldData()
_INLINE_FIELDS_PER_LINE: Final[int] = 3  # Fits into Discord's embed layout on desktop.


def create_inline_fields(*fields: _PartialFieldData) -> list[FieldData]:
    inline_fields = _assemble_fields(*fields, inline=True)
    # Pad with blanks if needed, to prevent different inlined field groups from mixing.
    while len(inline_fields) % _INLINE_FIELDS_PER_LINE:
        inline_fields.append(_BLANK_FIELD)
    return inline_fields


def create_standalone_fields(*fields: _PartialFieldData) -> list[FieldData]:
    return _assemble_fields(*fields, inline=False)


def _assemble_fields(*fields: _PartialFieldData, inline: bool) -> list[FieldData]:
    return [
        FieldData(emoji, title, content, inline) for emoji, title, content in fields
    ]
