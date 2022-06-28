from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Final, Literal, TypeAlias

from PIL.Image import Image, new as new_image, open as open_image
from PIL.ImageDraw import Draw
from discord import Asset, File, Member

from lib.common import Template, Utils

_ImageSource: TypeAlias = str | Asset

_COLOR_BLACK: Final[int] = 0
_COLOR_WHITE: Final[int] = 1

_IMAGE_FORMAT: Final[Literal["png"]] = "png"

_FILENAME_TEMPLATE: Final[Template] = Template(f"$name.{_IMAGE_FORMAT}")
_FILENAME_DEFAULT: Final[str] = _FILENAME_TEMPLATE.sub(name="image")


class ImageUtils:
    @staticmethod
    async def get_member_avatar(
        member: Member, size: int = 64, circle_crop: bool = True
    ) -> File:
        # The following line will fail loudly if "size" is not a power of 2.
        asset = member.display_avatar.with_size(size).with_format(_IMAGE_FORMAT)
        image_wrapper = await _ImageWrapper.create_from(asset)
        if circle_crop:
            image_wrapper.circle_crop()
        return image_wrapper.write_to_file(name="avatar")


class _ImageWrapper:
    def __init__(self, image: Image) -> None:
        self._image = image

    @staticmethod
    async def _get_image_data(source: _ImageSource) -> str | bytes:
        if isinstance(source, str):
            if Path(source).is_file():
                return source
            return await Utils.load_content_from_url(source)
        elif isinstance(source, Asset):
            return await source.read()
        else:
            raise TypeError(
                f'Cannot create image from object of type "{type(source)}". ({source})'
            )

    @classmethod
    async def create_from(cls, source: Image | _ImageSource) -> _ImageWrapper:
        if isinstance(source, Image):
            # Edits will be applied to a copy, in case the original is used elsewhere.
            image = source.copy()
        else:
            data = await cls._get_image_data(source)
            image = open_image(data if isinstance(data, str) else BytesIO(data))
        return cls(image)

    def write_to_file(self, name: str = "") -> File:
        filename = _FILENAME_TEMPLATE.sub(name=name) if name else _FILENAME_DEFAULT
        with BytesIO() as image_bytes:
            self._image.save(fp=image_bytes, format=_IMAGE_FORMAT)
            image_bytes.seek(0)
            return File(fp=image_bytes, filename=filename)

    def circle_crop(self) -> None:
        mask = new_image(mode="1", size=self._image.size, color=_COLOR_BLACK)
        Draw(mask).ellipse(xy=(0, 0, *self._image.size), fill=_COLOR_WHITE)
        self._image.putalpha(mask)
