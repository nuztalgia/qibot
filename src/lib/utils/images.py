from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Final, Literal, TypeAlias

from discord import Asset, File, Member
from PIL.Image import Image
from PIL.Image import new as new_image
from PIL.Image import open as open_image
from PIL.ImageDraw import Draw

from lib.utils.misc import load_content_from_url
from lib.utils.templates import Template

_ImageSource: TypeAlias = str | Asset

_COLOR_BLACK: Final[int] = 0
_COLOR_WHITE: Final[int] = 1

_AVATAR_SIZE_MAX: Final[int] = 512
_AVATAR_SIZE_DEFAULT: Final[int] = 64

_IMAGE_FORMAT: Final[Literal["png"]] = "png"

_FILENAME_TEMPLATE: Final[Template] = Template(f"$name.{_IMAGE_FORMAT}")
_FILENAME_DEFAULT: Final[str] = _FILENAME_TEMPLATE.sub(name="image")


async def get_member_avatar_file(
    member: Member, size: int = _AVATAR_SIZE_DEFAULT, circle_crop: bool = True
) -> File:
    image_wrapper = await ImageWrapper.create_from(
        # Note: "with_size" must be called with an integer that is a power of 2.
        member.display_avatar.with_size(_AVATAR_SIZE_MAX).with_format(_IMAGE_FORMAT)
    )
    if circle_crop:
        image_wrapper.circle_crop()
    return image_wrapper.resize(size).write_to_file(name="avatar")


class ImageWrapper:
    def __init__(self, image: Image) -> None:
        self._image = image

    @staticmethod
    async def _get_image_data(source: _ImageSource) -> str | bytes:
        if isinstance(source, str):
            if Path(source).is_file():
                return source
            return await load_content_from_url(source)
        elif isinstance(source, Asset):
            return await source.read()
        else:
            raise TypeError(
                f'Cannot create image from object of type "{type(source)}". ({source})'
            )

    @classmethod
    async def create_from(cls, source: Image | _ImageSource) -> ImageWrapper:
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

    def circle_crop(self) -> ImageWrapper:
        mask = new_image(mode="1", size=self._image.size, color=_COLOR_BLACK)
        circle_size = (self._image.width - 2, self._image.height - 2)
        Draw(mask).ellipse(xy=(0, 0, *circle_size), fill=_COLOR_WHITE)
        self._image.putalpha(mask)
        return self

    def resize(self, size: int | tuple[int, int]) -> ImageWrapper:
        if isinstance(size, int):
            size = (size, size)
        self._image = self._image.resize(size)
        return self
