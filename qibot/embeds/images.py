from typing import Final

from discord import Embed, File

from qibot.assets import IMAGE_PATH
from qibot.embeds.core import EmbedData
from qibot.utils import Template

_ATTACHMENT_URL: Final[Template] = Template("attachment://$filename")


class ThumbnailMixin(EmbedData):
    def __init__(self, thumbnail: str | File, **kwargs) -> None:
        super().__init__(**kwargs)
        self._required_attr_names.append("thumbnail")
        self._thumbnail: str | File = thumbnail  # Intentionally not marked "Final".

    def _validate(self) -> None:
        # Convert the thumbnail string into a File if it exists and is valid.
        # Otherwise, assume it's a URL and leave it for Discord to deal with.
        if isinstance(self._thumbnail, str):
            file_path = IMAGE_PATH / self._thumbnail
            if file_path.is_file():
                self._thumbnail = File(fp=file_path)

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
