from typing import Final, Iterable, Type

from discord import Embed, File

from qibot.embeds.core import EmbedData
from qibot.embeds.fielddata import FieldData
from qibot.embeds.fields import FieldsMixin
from qibot.embeds.images import ThumbnailMixin
from qibot.embeds.text import TextMixin
from qibot.utils import Log


def create_embed(
    *,
    color: int = 0,
    text: str = "",
    emoji: str = "",
    thumbnail: str | File | None = None,
    fields: Iterable[FieldData] | None = None,
) -> Embed:
    embed, files = create_embed_with_files(**locals())
    if files:
        Log.w(f"Created embed and discarded files: {[file.filename for file in files]}")
    return embed


def create_embed_with_files(
    *,
    color: int = 0,
    text: str = "",
    emoji: str = "",
    thumbnail: str | File | None = None,
    fields: Iterable[FieldData] | None = None,
) -> tuple[Embed, list[File]]:
    embed_data = _assemble_embed_data(**locals())
    return embed_data.build_embed(), embed_data.get_files()


def _assemble_embed_data(
    *,
    color: int,
    text: str,
    emoji: str,
    thumbnail: str | File | None,
    fields: Iterable[FieldData] | None,
) -> EmbedData:
    params = locals()
    class_mixins = {
        mixin
        for mixin, required_params in _MIXIN_MATCHER.items()
        if all(params.get(param_name) for param_name in required_params)
    }

    mixin_label = "And".join(mixin.__name__ for mixin in class_mixins) or "NoMixins"
    cls = type(f"{EmbedData.__name__}With{mixin_label}", (*class_mixins, EmbedData), {})

    return cls(**params)


_MIXIN_MATCHER: Final[dict[Type[EmbedData], set[str]]] = {
    FieldsMixin: {"fields"},
    TextMixin: {"text"},
    ThumbnailMixin: {"thumbnail"},
}
